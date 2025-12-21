"""Skill storage and synchronization management."""
import asyncio
import zipfile
import shutil
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field

import boto3
from botocore.exceptions import ClientError

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of skill synchronization."""
    added: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    total_local: int = 0
    total_s3: int = 0
    total_db: int = 0


@dataclass
class SkillMetadata:
    """Metadata extracted from SKILL.md."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "unknown"


class SkillManager:
    """Manages skill storage and synchronization between local, S3 and database.

    Storage structure:
    - Local: workspace/.claude/skills/{skill-name}/SKILL.md, ...
    - S3: s3://{bucket}/skills/{skill-name}/SKILL.md, ...
    - Both store the extracted folder contents, NOT ZIP files
    """

    def __init__(self):
        self.s3_bucket = settings.s3_bucket
        self.s3_prefix = "skills/"
        self.local_dir = Path(settings.agent_workspace_dir) / ".claude" / "skills"
        self._s3_client = None

    @property
    def s3_client(self):
        """Lazy initialization of S3 client."""
        if self._s3_client is None:
            self._s3_client = boto3.client(
                's3',
                region_name=settings.aws_region,
            )
        return self._s3_client

    def _ensure_local_dir(self):
        """Ensure local skills directory exists."""
        self.local_dir.mkdir(parents=True, exist_ok=True)

    def scan_local_skills(self) -> dict[str, Path]:
        """Scan local skills directory and return dict of skill_name -> path."""
        self._ensure_local_dir()
        skills = {}

        for item in self.local_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it has SKILL.md (valid skill directory)
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    skills[item.name] = item
                else:
                    logger.warning(f"Skipping directory without SKILL.md: {item.name}")

        logger.info(f"Found {len(skills)} local skills: {list(skills.keys())}")
        return skills

    async def scan_s3_skills(self) -> dict[str, list[str]]:
        """List skills in S3 bucket and return dict of skill_name -> list of s3_keys.

        S3 structure: skills/{skill-name}/SKILL.md, skills/{skill-name}/file.py, etc.
        """
        skills = {}

        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = await asyncio.to_thread(
                lambda: list(paginator.paginate(
                    Bucket=self.s3_bucket,
                    Prefix=self.s3_prefix
                ))
            )

            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    # Extract skill name from key like "skills/skill-name/SKILL.md"
                    # Skip the prefix itself
                    if key == self.s3_prefix:
                        continue

                    remaining = key[len(self.s3_prefix):]
                    parts = remaining.split('/', 1)
                    if len(parts) >= 1 and parts[0]:
                        skill_name = parts[0]
                        if skill_name not in skills:
                            skills[skill_name] = []
                        skills[skill_name].append(key)

            # Filter to only include skills that have SKILL.md
            valid_skills = {}
            for skill_name, keys in skills.items():
                has_skill_md = any(k.endswith('SKILL.md') for k in keys)
                if has_skill_md:
                    valid_skills[skill_name] = keys
                else:
                    logger.warning(f"S3 skill {skill_name} missing SKILL.md, skipping")

            logger.info(f"Found {len(valid_skills)} S3 skills: {list(valid_skills.keys())}")
            return valid_skills

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                logger.warning(f"S3 bucket {self.s3_bucket} does not exist")
                return {}
            else:
                logger.error(f"Error scanning S3: {e}")
                raise

    def extract_skill_metadata(self, skill_dir: Path) -> SkillMetadata:
        """Extract metadata from SKILL.md file."""
        skill_md = skill_dir / "SKILL.md"

        name = skill_dir.name
        description = f"Skill: {name}"
        version = "1.0.0"
        author = "unknown"

        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')

            # Try to extract name from first heading
            name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip()

            # Try to extract description (first paragraph after heading)
            desc_match = re.search(r'^#[^\n]+\n+([^\n#]+)', content, re.MULTILINE)
            if desc_match:
                description = desc_match.group(1).strip()

            # Try to extract version
            version_match = re.search(r'[Vv]ersion[:\s]+([0-9.]+)', content)
            if version_match:
                version = version_match.group(1)

        return SkillMetadata(
            name=name,
            description=description,
            version=version,
            author=author
        )

    async def upload_directory_to_s3(self, skill_name: str, skill_dir: Path) -> str:
        """Upload skill directory contents to S3.

        Args:
            skill_name: Name of the skill (used as S3 folder name)
            skill_dir: Local path to skill directory

        Returns:
            S3 location prefix (s3://bucket/skills/skill-name/)
        """
        s3_prefix = f"{self.s3_prefix}{skill_name}/"
        uploaded_count = 0

        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(skill_dir)
                s3_key = f"{s3_prefix}{relative_path}"

                try:
                    await asyncio.to_thread(
                        self.s3_client.upload_file,
                        str(file_path),
                        self.s3_bucket,
                        s3_key
                    )
                    uploaded_count += 1
                except ClientError as e:
                    logger.error(f"Failed to upload {file_path} to S3: {e}")
                    raise

        logger.info(f"Uploaded {uploaded_count} files for {skill_name} to s3://{self.s3_bucket}/{s3_prefix}")
        return f"s3://{self.s3_bucket}/{s3_prefix}"

    async def download_directory_from_s3(self, skill_name: str) -> Path:
        """Download skill directory from S3 to local.

        Args:
            skill_name: Name of the skill

        Returns:
            Local path to downloaded skill directory
        """
        self._ensure_local_dir()
        s3_prefix = f"{self.s3_prefix}{skill_name}/"
        local_skill_dir = self.local_dir / skill_name

        # Remove existing directory if exists
        if local_skill_dir.exists():
            shutil.rmtree(local_skill_dir)
        local_skill_dir.mkdir(parents=True)

        # List all objects with this prefix
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = await asyncio.to_thread(
            lambda: list(paginator.paginate(
                Bucket=self.s3_bucket,
                Prefix=s3_prefix
            ))
        )

        downloaded_count = 0
        for page in pages:
            for obj in page.get('Contents', []):
                s3_key = obj['Key']
                # Get relative path within skill folder
                relative_path = s3_key[len(s3_prefix):]
                if not relative_path:
                    continue

                local_file_path = local_skill_dir / relative_path

                # Create parent directories if needed
                local_file_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    await asyncio.to_thread(
                        self.s3_client.download_file,
                        self.s3_bucket,
                        s3_key,
                        str(local_file_path)
                    )
                    downloaded_count += 1
                except ClientError as e:
                    logger.error(f"Failed to download {s3_key}: {e}")
                    raise

        logger.info(f"Downloaded {downloaded_count} files for {skill_name} to {local_skill_dir}")
        return local_skill_dir

    async def delete_from_s3(self, skill_name: str) -> None:
        """Delete skill directory from S3."""
        s3_prefix = f"{self.s3_prefix}{skill_name}/"

        try:
            # List all objects with this prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = await asyncio.to_thread(
                lambda: list(paginator.paginate(
                    Bucket=self.s3_bucket,
                    Prefix=s3_prefix
                ))
            )

            # Collect all keys to delete
            keys_to_delete = []
            for page in pages:
                for obj in page.get('Contents', []):
                    keys_to_delete.append({'Key': obj['Key']})

            # Delete in batches of 1000 (S3 limit)
            if keys_to_delete:
                for i in range(0, len(keys_to_delete), 1000):
                    batch = keys_to_delete[i:i + 1000]
                    await asyncio.to_thread(
                        self.s3_client.delete_objects,
                        Bucket=self.s3_bucket,
                        Delete={'Objects': batch}
                    )

            logger.info(f"Deleted {len(keys_to_delete)} files for {skill_name} from S3")

        except ClientError as e:
            logger.error(f"Failed to delete {skill_name} from S3: {e}")
            raise

    def extract_zip_to_directory(self, zip_path: Path, skill_name: str) -> Path:
        """Extract ZIP file to skills directory."""
        self._ensure_local_dir()
        dest_dir = self.local_dir / skill_name

        # Remove existing directory if exists
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Check if ZIP contains a root folder or files directly
            namelist = zf.namelist()

            # Detect if there's a single root folder
            root_folders = set()
            for name in namelist:
                parts = name.split('/')
                if len(parts) > 1 and parts[0]:
                    root_folders.add(parts[0])

            if len(root_folders) == 1:
                # ZIP has a single root folder, extract and rename
                root_folder = list(root_folders)[0]
                temp_dir = self.local_dir / f"_temp_{skill_name}"
                zf.extractall(temp_dir)

                # Move the root folder to the correct name
                extracted_dir = temp_dir / root_folder
                if extracted_dir.exists():
                    shutil.move(str(extracted_dir), str(dest_dir))
                    shutil.rmtree(temp_dir)
                else:
                    # Fallback: rename temp dir
                    shutil.move(str(temp_dir), str(dest_dir))
            else:
                # ZIP contains files directly, extract to dest_dir
                dest_dir.mkdir(parents=True, exist_ok=True)
                zf.extractall(dest_dir)

        logger.info(f"Extracted ZIP to: {dest_dir}")
        return dest_dir

    async def upload_skill_package(
        self,
        zip_content: bytes,
        skill_name: str,
        original_filename: str
    ) -> dict:
        """
        Upload skill package: extract to local, upload extracted files to S3.

        Args:
            zip_content: The ZIP file content as bytes
            skill_name: Name for the skill
            original_filename: Original filename for logging

        Returns:
            dict with skill metadata
        """
        import tempfile

        self._ensure_local_dir()

        # Save ZIP to temp file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(zip_content)
            tmp_path = Path(tmp.name)

        try:
            # Validate ZIP has SKILL.md
            with zipfile.ZipFile(tmp_path, 'r') as zf:
                namelist = zf.namelist()
                has_skill_md = any(
                    name.endswith('SKILL.md') or name == 'SKILL.md'
                    for name in namelist
                )
                if not has_skill_md:
                    raise ValueError("ZIP must contain a SKILL.md file")

            # Extract to local directory
            skill_dir = self.extract_zip_to_directory(tmp_path, skill_name)

            # Extract metadata
            metadata = self.extract_skill_metadata(skill_dir)

            # Upload extracted directory to S3
            s3_location = await self.upload_directory_to_s3(skill_name, skill_dir)

            return {
                "name": metadata.name,
                "description": metadata.description,
                "version": metadata.version,
                "s3_location": s3_location,
                "local_path": str(skill_dir),
            }

        finally:
            # Cleanup temp file
            tmp_path.unlink(missing_ok=True)

    async def delete_skill_files(self, skill_name: str) -> None:
        """Delete skill from local directory and S3."""
        # Delete local directory
        local_path = self.local_dir / skill_name
        if local_path.exists():
            shutil.rmtree(local_path)
            logger.info(f"Deleted local skill directory: {local_path}")

        # Delete from S3
        try:
            await self.delete_from_s3(skill_name)
        except ClientError as e:
            # Log but don't fail if S3 deletion fails
            logger.warning(f"Failed to delete {skill_name} from S3: {e}")

    async def refresh(self, db_skills: list[dict]) -> tuple[SyncResult, list[dict]]:
        """
        Synchronize skills between local directory, S3 and database.

        Args:
            db_skills: Current skills from database

        Returns:
            Tuple of (SyncResult, list of skills to add to DB)
        """
        result = SyncResult()
        skills_to_add = []

        # Scan local and S3
        local_skills = self.scan_local_skills()
        s3_skills = await self.scan_s3_skills()

        # Build DB skill map by folder name
        db_skill_map = {}
        for skill in db_skills:
            # Try to extract folder name from s3_location
            s3_loc = skill.get('s3_location', '')
            if s3_loc:
                # Extract name from s3://bucket/skills/name/ or s3://bucket/skills/name
                match = re.search(r'/skills/([^/]+)/?', s3_loc)
                if match:
                    db_skill_map[match.group(1)] = skill
                    continue
            # Fallback: use sanitized skill name
            name = skill.get('name', '').lower().replace(' ', '-')
            if name:
                db_skill_map[name] = skill

        result.total_local = len(local_skills)
        result.total_s3 = len(s3_skills)
        result.total_db = len(db_skills)

        # Get all unique skill names
        all_skill_names = set(local_skills.keys()) | set(s3_skills.keys())

        for skill_name in all_skill_names:
            in_local = skill_name in local_skills
            in_s3 = skill_name in s3_skills
            in_db = skill_name in db_skill_map

            try:
                if in_local and not in_s3:
                    # Local only: upload to S3
                    logger.info(f"Skill {skill_name}: local only, uploading to S3")

                    skill_dir = local_skills[skill_name]

                    # Upload directory to S3
                    s3_location = await self.upload_directory_to_s3(skill_name, skill_dir)

                    # Extract metadata and prepare DB record
                    if not in_db:
                        metadata = self.extract_skill_metadata(skill_dir)
                        skills_to_add.append({
                            "name": metadata.name,
                            "folder_name": skill_name,
                            "description": metadata.description,
                            "version": metadata.version,
                            "s3_location": s3_location,
                            "is_system": False,
                            "created_by": "sync",
                        })

                    result.added.append(skill_name)

                elif in_s3 and not in_local:
                    # S3 only: download to local
                    logger.info(f"Skill {skill_name}: S3 only, downloading to local")

                    # Download from S3
                    skill_dir = await self.download_directory_from_s3(skill_name)

                    # Extract metadata and add to DB if not exists
                    if not in_db:
                        metadata = self.extract_skill_metadata(skill_dir)
                        skills_to_add.append({
                            "name": metadata.name,
                            "folder_name": skill_name,
                            "description": metadata.description,
                            "version": metadata.version,
                            "s3_location": f"s3://{self.s3_bucket}/{self.s3_prefix}{skill_name}/",
                            "is_system": False,
                            "created_by": "sync",
                        })

                    result.added.append(skill_name)

                elif in_local and in_s3:
                    # Both exist: ensure DB record exists
                    if not in_db:
                        logger.info(f"Skill {skill_name}: exists in local and S3, adding to DB")
                        skill_dir = local_skills[skill_name]
                        metadata = self.extract_skill_metadata(skill_dir)
                        skills_to_add.append({
                            "name": metadata.name,
                            "folder_name": skill_name,
                            "description": metadata.description,
                            "version": metadata.version,
                            "s3_location": f"s3://{self.s3_bucket}/{self.s3_prefix}{skill_name}/",
                            "is_system": False,
                            "created_by": "sync",
                        })
                        result.updated.append(skill_name)
                    else:
                        logger.debug(f"Skill {skill_name}: already synced")

            except Exception as e:
                logger.error(f"Error syncing skill {skill_name}: {e}")
                result.errors.append({"skill": skill_name, "error": str(e)})

        # Check for DB entries without files (orphaned records)
        for skill_name, skill in db_skill_map.items():
            if skill_name not in all_skill_names:
                logger.info(f"Skill {skill_name}: DB only (orphaned), marking for removal")
                result.removed.append(skill_name)

        return result, skills_to_add


# Global instance
skill_manager = SkillManager()
