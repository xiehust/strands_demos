#!/usr/bin/env python3
"""
Slurm Job Configuration Analyzer

Analyzes Slurm batch scripts for best practices, common issues,
and optimization opportunities.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class JobConfigAnalyzer:
    """Analyzer for Slurm job configuration scripts."""

    def __init__(self, script_path: str):
        self.script_path = Path(script_path)
        self.content = ""
        self.sbatch_directives = {}
        self.env_vars = {}
        self.issues = []
        self.warnings = []
        self.suggestions = []

    def read_script(self) -> bool:
        """Read the job script file."""
        try:
            with open(self.script_path, "r") as f:
                self.content = f.read()
            return True
        except Exception as e:
            print(f"Error reading script: {e}")
            return False

    def parse_sbatch_directives(self):
        """Extract SBATCH directives from script."""
        pattern = r"#SBATCH\s+--?([a-zA-Z0-9_-]+)(?:=(.+))?$"
        for line in self.content.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                key = match.group(1)
                value = match.group(2).strip() if match.group(2) else True
                self.sbatch_directives[key] = value

    def parse_env_vars(self):
        """Extract environment variable exports."""
        pattern = r"export\s+([A-Z_][A-Z0-9_]*)=(.+)$"
        for line in self.content.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                key = match.group(1)
                value = match.group(2).strip().strip('"\'')
                self.env_vars[key] = value

    def check_resource_allocation(self):
        """Check resource allocation settings."""
        # Check for required directives
        if "nodes" not in self.sbatch_directives:
            self.warnings.append("No --nodes directive specified")

        if "ntasks-per-node" not in self.sbatch_directives:
            self.warnings.append("No --ntasks-per-node directive specified")

        # Check GPU allocation
        gres = self.sbatch_directives.get("gres")
        if gres:
            if "gpu:" in gres:
                gpu_count = int(gres.split(":")[-1]) if ":" in gres else 0
                ntasks = self.sbatch_directives.get("ntasks-per-node")

                if ntasks and int(ntasks) != gpu_count:
                    self.warnings.append(
                        f"Mismatch: --ntasks-per-node={ntasks} but --gres=gpu:{gpu_count}. "
                        "Typically these should match for multi-GPU training."
                    )
        else:
            self.suggestions.append(
                "Consider adding --gres=gpu:N if using GPUs"
            )

        # Check CPU allocation
        cpus_per_task = self.sbatch_directives.get("cpus-per-task")
        if cpus_per_task:
            cpus = int(cpus_per_task)
            if cpus < 8:
                self.suggestions.append(
                    f"--cpus-per-task={cpus} may be low for data loading. "
                    "Consider 8-12 CPUs per GPU."
                )
        else:
            self.suggestions.append(
                "Consider adding --cpus-per-task=12 for efficient data loading"
            )

        # Check for exclusive node access
        if "exclusive" not in self.sbatch_directives:
            self.suggestions.append(
                "Consider adding --exclusive for better performance isolation"
            )

    def check_time_limits(self):
        """Check time limit settings."""
        time_limit = self.sbatch_directives.get("time")
        if not time_limit:
            self.warnings.append(
                "No --time directive specified. Job may run indefinitely or use partition default."
            )
        else:
            # Check if time is very short
            if ":" in time_limit:
                parts = time_limit.split(":")
                if len(parts) == 3:  # HH:MM:SS
                    hours = int(parts[0].split("-")[-1])  # Handle days
                    if hours < 1:
                        self.warnings.append(
                            f"Very short time limit: {time_limit}. "
                            "Ensure this is sufficient for your job."
                        )

    def check_checkpointing(self):
        """Check for checkpointing and fault tolerance."""
        has_checkpoint_save = (
            "checkpoint" in self.content.lower()
            or "save_checkpoint" in self.content.lower()
            or "torch.save" in self.content
        )

        if not has_checkpoint_save:
            self.suggestions.append(
                "No checkpoint saving detected. Consider implementing checkpointing "
                "for fault tolerance and job resume capability."
            )

        # Check for signal handling
        has_signal_handler = "signal" in self.content.lower() or "SIGTERM" in self.content
        if not has_signal_handler:
            self.suggestions.append(
                "Consider adding SIGTERM signal handler for graceful shutdown. "
                "Use #SBATCH --signal=B:TERM@300 and handle signal in code."
            )

        # Check for requeue
        if "requeue" not in self.sbatch_directives:
            self.suggestions.append(
                "Consider adding --requeue to automatically restart failed jobs"
            )

    def check_distributed_training(self):
        """Check distributed training configuration."""
        # Check for distributed training indicators
        is_distributed = any(
            keyword in self.content.lower()
            for keyword in [
                "distributed",
                "torch.distributed",
                "ddp",
                "world_size",
                "mpirun",
                "srun",
            ]
        )

        if is_distributed:
            # Check for proper environment variables
            required_vars = ["MASTER_ADDR", "MASTER_PORT"]
            for var in required_vars:
                if var not in self.env_vars and var not in self.content:
                    self.warnings.append(
                        f"Distributed training detected but {var} not set"
                    )

            # Check for NCCL configuration
            nccl_vars = ["NCCL_DEBUG", "NCCL_SOCKET_IFNAME", "FI_PROVIDER"]
            missing_nccl = [
                var for var in nccl_vars if var not in self.env_vars
            ]
            if missing_nccl:
                self.suggestions.append(
                    f"Consider setting NCCL environment variables: {', '.join(missing_nccl)}"
                )

        # Check for EFA optimization
        if "FI_PROVIDER" in self.env_vars:
            if self.env_vars["FI_PROVIDER"] != "efa":
                self.warnings.append(
                    f"FI_PROVIDER={self.env_vars['FI_PROVIDER']}. Should be 'efa' for optimal performance."
                )
        elif is_distributed:
            self.suggestions.append(
                "Consider setting FI_PROVIDER=efa for EFA optimization"
            )

    def check_output_settings(self):
        """Check output and error file settings."""
        if "output" not in self.sbatch_directives:
            self.suggestions.append(
                "Consider specifying --output for better log organization"
            )

        if "error" not in self.sbatch_directives:
            self.suggestions.append(
                "Consider specifying --error to separate error logs"
            )

        # Check for job name
        if "job-name" not in self.sbatch_directives:
            self.suggestions.append(
                "Consider adding --job-name for easier job identification"
            )

    def check_performance_settings(self):
        """Check for performance optimization settings."""
        # Check for PyTorch optimizations
        if "torch" in self.content.lower():
            opt_suggestions = []

            if "PYTORCH_CUDA_ALLOC_CONF" not in self.env_vars:
                opt_suggestions.append("PYTORCH_CUDA_ALLOC_CONF for memory management")

            if "OMP_NUM_THREADS" not in self.env_vars:
                opt_suggestions.append("OMP_NUM_THREADS to control CPU parallelism")

            if opt_suggestions:
                self.suggestions.append(
                    f"Consider setting: {', '.join(opt_suggestions)}"
                )

        # Check for GPU settings
        if "nvidia-smi" not in self.content:
            self.suggestions.append(
                "Consider adding 'nvidia-smi' before training for debugging"
            )

    def check_data_loading(self):
        """Check data loading configuration."""
        # Check for DataLoader configuration
        if "DataLoader" in self.content or "dataloader" in self.content.lower():
            if "num_workers" not in self.content:
                self.suggestions.append(
                    "Specify num_workers in DataLoader for efficient data loading"
                )

            if "pin_memory" not in self.content:
                self.suggestions.append(
                    "Consider pin_memory=True in DataLoader for faster GPU transfer"
                )

    def analyze(self) -> Dict:
        """Run all analysis checks."""
        if not self.read_script():
            return {"error": "Failed to read script"}

        self.parse_sbatch_directives()
        self.parse_env_vars()

        # Run all checks
        self.check_resource_allocation()
        self.check_time_limits()
        self.check_checkpointing()
        self.check_distributed_training()
        self.check_output_settings()
        self.check_performance_settings()
        self.check_data_loading()

        return {
            "sbatch_directives": self.sbatch_directives,
            "env_vars": self.env_vars,
            "issues": self.issues,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
        }

    def generate_report(self) -> str:
        """Generate analysis report."""
        report = []
        report.append("=" * 80)
        report.append(f"Slurm Job Configuration Analysis: {self.script_path.name}")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Issues: {len(self.issues)}")
        report.append(f"Warnings: {len(self.warnings)}")
        report.append(f"Suggestions: {len(self.suggestions)}")
        report.append("")

        # SBATCH Directives
        report.append("SBATCH DIRECTIVES")
        report.append("-" * 80)
        if self.sbatch_directives:
            for key, value in self.sbatch_directives.items():
                report.append(f"  --{key}={value}")
        else:
            report.append("  None found")
        report.append("")

        # Environment Variables
        report.append("ENVIRONMENT VARIABLES")
        report.append("-" * 80)
        if self.env_vars:
            for key, value in self.env_vars.items():
                report.append(f"  {key}={value}")
        else:
            report.append("  None found")
        report.append("")

        # Issues
        if self.issues:
            report.append("ISSUES")
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

        # Suggestions
        if self.suggestions:
            report.append("OPTIMIZATION SUGGESTIONS")
            report.append("-" * 80)
            for suggestion in self.suggestions:
                report.append(f"  💡 {suggestion}")
            report.append("")

        report.append("=" * 80)
        report.append("End of Analysis")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Slurm job scripts for best practices and optimization"
    )
    parser.add_argument("script", help="Path to Slurm batch script to analyze")
    parser.add_argument(
        "--output", "-o", help="Output file for report (default: stdout)"
    )
    args = parser.parse_args()

    analyzer = JobConfigAnalyzer(args.script)
    results = analyzer.analyze()

    if "error" in results:
        print(f"Error: {results['error']}", file=sys.stderr)
        sys.exit(1)

    report = analyzer.generate_report()

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Analysis report written to {args.output}")
    else:
        print(report)

    # Exit with non-zero if there are issues
    sys.exit(1 if analyzer.issues else 0)


if __name__ == "__main__":
    main()
