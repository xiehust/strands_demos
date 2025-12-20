"""
Integration tests for Skill API endpoints.
"""
import pytest
from unittest.mock import patch
from datetime import datetime


# Helper to create complete skill data
def make_skill_data(
    skill_id: str,
    name: str,
    description: str = "A skill",
    version: str = "1.0.0",
    is_system: bool = False,
    created_by: str = "system",
):
    """Create complete skill data with all required fields."""
    return {
        "id": skill_id,
        "name": name,
        "description": description,
        "version": version,
        "isSystem": is_system,
        "createdBy": created_by,
        "createdAt": datetime.now().isoformat(),
    }


class TestSkillEndpoints:
    """Tests for /api/skills endpoints."""

    @patch("src.api.routers.skills.db_client")
    def test_list_skills_empty(self, mock_db, test_client):
        """Test listing skills when empty."""
        mock_db.list_skills.return_value = []

        response = test_client.get("/api/skills")

        assert response.status_code == 200
        assert response.json() == []

    @patch("src.api.routers.skills.db_client")
    def test_list_skills(self, mock_db, test_client):
        """Test listing skills."""
        mock_db.list_skills.return_value = [
            make_skill_data("xlsx", "xlsx", "Excel file processing"),
            make_skill_data("pdf", "pdf", "PDF file processing"),
        ]

        response = test_client.get("/api/skills")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "xlsx"
        assert data[1]["name"] == "pdf"

    @patch("src.api.routers.skills.db_client")
    def test_get_skill_success(self, mock_db, test_client):
        """Test getting a specific skill."""
        mock_db.get_skill.return_value = make_skill_data(
            "xlsx", "xlsx", "Excel file processing skill"
        )

        response = test_client.get("/api/skills/xlsx")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "xlsx"
        assert data["name"] == "xlsx"

    @patch("src.api.routers.skills.db_client")
    def test_get_skill_not_found(self, mock_db, test_client):
        """Test getting non-existent skill."""
        mock_db.get_skill.return_value = None

        response = test_client.get("/api/skills/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("src.api.routers.skills.db_client")
    def test_create_skill(self, mock_db, test_client):
        """Test creating a new skill."""
        mock_db.create_skill.return_value = make_skill_data(
            "new-skill", "new-skill", "A new skill"
        )

        response = test_client.post(
            "/api/skills",
            json={
                "name": "new-skill",
                "description": "A new skill",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new-skill"
        mock_db.create_skill.assert_called_once()

    @patch("src.api.routers.skills.db_client")
    def test_delete_skill(self, mock_db, test_client):
        """Test deleting a skill."""
        mock_db.get_skill.return_value = make_skill_data(
            "delete-skill", "delete-skill", "To delete"
        )
        mock_db.delete_skill.return_value = True

        response = test_client.delete("/api/skills/delete-skill")

        assert response.status_code == 204
        mock_db.delete_skill.assert_called_once_with("delete-skill")

    @patch("src.api.routers.skills.db_client")
    def test_delete_skill_not_found(self, mock_db, test_client):
        """Test deleting non-existent skill."""
        mock_db.get_skill.return_value = None

        response = test_client.delete("/api/skills/nonexistent")

        assert response.status_code == 404
