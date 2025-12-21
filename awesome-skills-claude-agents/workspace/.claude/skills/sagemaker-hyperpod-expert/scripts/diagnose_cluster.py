#!/usr/bin/env python3
"""
HyperPod Cluster Diagnostic Tool

Analyzes cluster configuration, health, and performance metrics.
Generates a comprehensive diagnostic report with recommendations.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple


class ClusterDiagnostics:
    """Diagnostic tool for SageMaker HyperPod clusters."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []

    def run_command(self, cmd: str) -> Tuple[str, int]:
        """Execute shell command and return output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            return "", -1
        except Exception as e:
            return str(e), -1

    def check_slurm_health(self) -> Dict:
        """Check Slurm cluster health."""
        print("Checking Slurm health...")
        health = {"status": "unknown", "nodes": {}, "jobs": {}}

        # Check node status
        output, rc = self.run_command("sinfo -Nel -o '%n|%T|%C|%m|%e'")
        if rc == 0:
            nodes = {"total": 0, "idle": 0, "allocated": 0, "down": 0, "drain": 0}
            for line in output.strip().split("\n")[1:]:  # Skip header
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 2:
                        nodes["total"] += 1
                        state = parts[1].lower()
                        if "idle" in state:
                            nodes["idle"] += 1
                        elif "alloc" in state:
                            nodes["allocated"] += 1
                        elif "down" in state:
                            nodes["down"] += 1
                            self.issues.append(f"Node {parts[0]} is DOWN")
                        elif "drain" in state:
                            nodes["drain"] += 1
                            self.warnings.append(f"Node {parts[0]} is DRAINED")

            health["nodes"] = nodes

            # Check for issues
            if nodes["down"] > 0:
                self.issues.append(
                    f"{nodes['down']} node(s) are down - check node health"
                )
            if nodes["drain"] > 0:
                self.warnings.append(
                    f"{nodes['drain']} node(s) are drained - check drain reasons with 'sinfo -R'"
                )

        # Check job queue
        output, rc = self.run_command("squeue -o '%i|%T|%r' --noheader")
        if rc == 0:
            jobs = {"running": 0, "pending": 0, "failed": 0}
            pending_reasons = {}

            for line in output.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 2:
                    state = parts[1].lower()
                    if "running" in state:
                        jobs["running"] += 1
                    elif "pending" in state:
                        jobs["pending"] += 1
                        reason = parts[2] if len(parts) > 2 else "Unknown"
                        pending_reasons[reason] = pending_reasons.get(reason, 0) + 1
                    elif "fail" in state:
                        jobs["failed"] += 1

            health["jobs"] = jobs
            health["pending_reasons"] = pending_reasons

            # Check for issues
            if jobs["pending"] > 10:
                self.warnings.append(
                    f"{jobs['pending']} jobs pending - may indicate resource shortage"
                )
            if pending_reasons:
                for reason, count in pending_reasons.items():
                    if count > 5:
                        self.warnings.append(
                            f"{count} jobs pending due to: {reason}"
                        )

        return health

    def check_gpu_health(self) -> Dict:
        """Check GPU health and utilization."""
        print("Checking GPU health...")
        gpu_info = {"status": "unknown", "gpus": []}

        output, rc = self.run_command(
            "nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,"
            "memory.used,memory.total,temperature.gpu,power.draw,power.limit "
            "--format=csv,noheader,nounits"
        )

        if rc == 0:
            for line in output.strip().split("\n"):
                if not line:
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 9:
                    gpu_util = float(parts[2]) if parts[2] != "[N/A]" else 0
                    mem_util = float(parts[3]) if parts[3] != "[N/A]" else 0
                    temp = float(parts[6]) if parts[6] != "[N/A]" else 0

                    gpu_info["gpus"].append(
                        {
                            "index": parts[0],
                            "name": parts[1],
                            "gpu_util": gpu_util,
                            "mem_util": mem_util,
                            "memory_used_mb": parts[4],
                            "memory_total_mb": parts[5],
                            "temperature": temp,
                            "power_draw": parts[7],
                            "power_limit": parts[8],
                        }
                    )

                    # Check for issues
                    if temp > 85:
                        self.warnings.append(
                            f"GPU {parts[0]} temperature high: {temp}°C"
                        )
                    if gpu_util < 50:
                        self.warnings.append(
                            f"GPU {parts[0]} low utilization: {gpu_util}%"
                        )

            gpu_info["status"] = "healthy" if gpu_info["gpus"] else "no_gpus"
        else:
            self.warnings.append("nvidia-smi not available or failed")

        return gpu_info

    def check_efa_status(self) -> Dict:
        """Check EFA device status."""
        print("Checking EFA status...")
        efa_info = {"status": "unknown", "devices": []}

        # Check for EFA devices
        output, rc = self.run_command("fi_info -p efa")
        if rc == 0 and "provider: efa" in output.lower():
            efa_info["status"] = "available"

            # Count devices
            device_count = output.lower().count("domain:")
            efa_info["device_count"] = device_count

            if device_count == 0:
                self.issues.append("EFA provider found but no devices detected")
        else:
            self.issues.append(
                "EFA not available - check driver installation with 'fi_info -p efa'"
            )
            efa_info["status"] = "not_available"

        # Check ibv_devinfo as backup
        output, rc = self.run_command("ibv_devinfo")
        if rc == 0 and output.strip():
            efa_info["ibverbs_devices"] = output.count("hca_id:")

        return efa_info

    def check_storage_health(self) -> Dict:
        """Check FSx and storage health."""
        print("Checking storage health...")
        storage = {"fsx_mounts": [], "disk_usage": {}}

        # Check FSx mounts
        output, rc = self.run_command("mount | grep lustre")
        if rc == 0 and output:
            for line in output.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 3:
                    storage["fsx_mounts"].append(
                        {"device": parts[0], "mountpoint": parts[2]}
                    )
            self.info.append(f"Found {len(storage['fsx_mounts'])} FSx mount(s)")
        else:
            self.warnings.append("No FSx for Lustre mounts found")

        # Check disk usage
        output, rc = self.run_command("df -h | grep -E '(fsx|Filesystem)'")
        if rc == 0:
            storage["disk_usage"] = output

        return storage

    def check_nccl_config(self) -> Dict:
        """Check NCCL environment configuration."""
        print("Checking NCCL configuration...")
        import os

        nccl_vars = [
            "NCCL_DEBUG",
            "NCCL_SOCKET_IFNAME",
            "NCCL_IB_DISABLE",
            "NCCL_NET_GDR_LEVEL",
            "NCCL_PROTO",
            "FI_PROVIDER",
            "FI_EFA_USE_DEVICE_RDMA",
        ]

        config = {}
        for var in nccl_vars:
            value = os.environ.get(var)
            config[var] = value if value else "not_set"

        # Check for recommended settings
        if config.get("FI_PROVIDER") != "efa":
            self.warnings.append("FI_PROVIDER not set to 'efa' for optimal EFA usage")

        if config.get("NCCL_SOCKET_IFNAME") == "not_set":
            self.info.append(
                "Consider setting NCCL_SOCKET_IFNAME=^docker,lo to exclude non-EFA interfaces"
            )

        return config

    def generate_report(
        self, slurm: Dict, gpu: Dict, efa: Dict, storage: Dict, nccl: Dict
    ) -> str:
        """Generate diagnostic report."""
        report = []
        report.append("=" * 80)
        report.append("SageMaker HyperPod Cluster Diagnostic Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Critical Issues: {len(self.issues)}")
        report.append(f"Warnings: {len(self.warnings)}")
        report.append(f"Info: {len(self.info)}")
        report.append("")

        # Issues
        if self.issues:
            report.append("CRITICAL ISSUES")
            report.append("-" * 80)
            for issue in self.issues:
                report.append(f"  ✗ {issue}")
            report.append("")

        # Warnings
        if self.warnings:
            report.append("WARNINGS")
            report.append("-" * 80)
            for warning in self.warnings:
                report.append(f"  ⚠ {warning}")
            report.append("")

        # Info
        if self.info:
            report.append("INFORMATION")
            report.append("-" * 80)
            for info in self.info:
                report.append(f"  ℹ {info}")
            report.append("")

        # Slurm Status
        report.append("SLURM CLUSTER STATUS")
        report.append("-" * 80)
        if slurm.get("nodes"):
            nodes = slurm["nodes"]
            report.append(f"Total Nodes: {nodes.get('total', 0)}")
            report.append(f"  - Idle: {nodes.get('idle', 0)}")
            report.append(f"  - Allocated: {nodes.get('allocated', 0)}")
            report.append(f"  - Down: {nodes.get('down', 0)}")
            report.append(f"  - Drained: {nodes.get('drain', 0)}")
        if slurm.get("jobs"):
            jobs = slurm["jobs"]
            report.append(f"Jobs:")
            report.append(f"  - Running: {jobs.get('running', 0)}")
            report.append(f"  - Pending: {jobs.get('pending', 0)}")
        report.append("")

        # GPU Status
        report.append("GPU STATUS")
        report.append("-" * 80)
        if gpu.get("gpus"):
            report.append(f"GPUs Detected: {len(gpu['gpus'])}")
            for g in gpu["gpus"][:3]:  # Show first 3
                report.append(
                    f"  GPU {g['index']}: {g['name']} - "
                    f"Util: {g['gpu_util']}%, Mem: {g['mem_util']}%, "
                    f"Temp: {g['temperature']}°C"
                )
            if len(gpu["gpus"]) > 3:
                report.append(f"  ... and {len(gpu['gpus']) - 3} more GPUs")
        else:
            report.append("No GPUs detected")
        report.append("")

        # EFA Status
        report.append("EFA STATUS")
        report.append("-" * 80)
        report.append(f"Status: {efa.get('status', 'unknown')}")
        if efa.get("device_count"):
            report.append(f"Devices: {efa['device_count']}")
        report.append("")

        # Storage
        report.append("STORAGE STATUS")
        report.append("-" * 80)
        if storage.get("fsx_mounts"):
            report.append(f"FSx Mounts: {len(storage['fsx_mounts'])}")
            for mount in storage["fsx_mounts"]:
                report.append(f"  - {mount['mountpoint']}")
        report.append("")

        # NCCL Config
        report.append("NCCL CONFIGURATION")
        report.append("-" * 80)
        for key, value in nccl.items():
            report.append(f"  {key}: {value}")
        report.append("")

        report.append("=" * 80)
        report.append("End of Report")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose SageMaker HyperPod cluster health and configuration"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for report (default: stdout)",
        default=None,
    )
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    args = parser.parse_args()

    diagnostics = ClusterDiagnostics()

    # Run all checks
    slurm_health = diagnostics.check_slurm_health()
    gpu_health = diagnostics.check_gpu_health()
    efa_status = diagnostics.check_efa_status()
    storage_health = diagnostics.check_storage_health()
    nccl_config = diagnostics.check_nccl_config()

    # Generate report
    if args.json:
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "slurm": slurm_health,
            "gpu": gpu_health,
            "efa": efa_status,
            "storage": storage_health,
            "nccl": nccl_config,
            "issues": diagnostics.issues,
            "warnings": diagnostics.warnings,
            "info": diagnostics.info,
        }
        report = json.dumps(report_data, indent=2)
    else:
        report = diagnostics.generate_report(
            slurm_health, gpu_health, efa_status, storage_health, nccl_config
        )

    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)

    # Exit code based on issues
    sys.exit(1 if diagnostics.issues else 0)


if __name__ == "__main__":
    main()
