---
name: sagemaker-hyperpod-expert
description: Expert system for AWS SageMaker HyperPod cluster optimization, troubleshooting, and configuration analysis. Use when users need help with (1) HyperPod cluster setup and configuration, (2) Performance optimization for distributed training, (3) Diagnosing cluster issues (node failures, network problems, storage issues), (4) Analyzing Slurm job scripts and configurations, (5) EFA and NCCL tuning, (6) GPU utilization optimization, (7) FSx for Lustre performance tuning, or (8) Checkpoint and fault tolerance strategies. Provides diagnostic scripts, reference documentation, and actionable recommendations.
---

# SageMaker HyperPod Expert

Expert system for optimizing, troubleshooting, and configuring AWS SageMaker HyperPod clusters for distributed training workloads.

## Quick Diagnostic Workflow

When users report HyperPod issues or request optimization, follow this workflow:

### 1. Gather Context
Ask targeted questions to understand the situation:
- What symptoms are observed? (slow training, job failures, hangs, errors)
- What configuration is being used? (instance types, number of nodes, job script)
- What workload is running? (model size, framework, distributed strategy)
- Are there any error messages or logs available?

### 2. Run Diagnostics
Use the diagnostic script to assess cluster health:

```bash
# Run comprehensive cluster diagnostics
python scripts/diagnose_cluster.py

# Save report to file
python scripts/diagnose_cluster.py -o diagnostic_report.txt

# Get JSON output for programmatic analysis
python scripts/diagnose_cluster.py --json
```

The diagnostic script checks:
- Slurm cluster health (node status, job queue)
- GPU health and utilization
- EFA device status and configuration
- FSx for Lustre mount status
- NCCL environment variables

### 3. Analyze Job Configuration
If the user provides a Slurm batch script, analyze it:

```bash
# Analyze job script for issues and optimizations
python scripts/analyze_job_config.py path/to/job_script.sh

# Save analysis to file
python scripts/analyze_job_config.py path/to/job_script.sh -o analysis_report.txt
```

The analyzer checks for:
- Resource allocation best practices
- Distributed training configuration
- Checkpoint and fault tolerance
- Performance optimization settings
- NCCL and EFA configuration

### 4. Load Reference Documentation
Based on the issue category, load relevant reference material:

**For performance issues:**
```bash
# Read optimization guide
read references/optimization_guide.md
```

**For cluster architecture questions:**
```bash
# Read architecture reference
read references/hyperpod_architecture.md
```

**For troubleshooting specific problems:**
```bash
# Read troubleshooting guide
read references/troubleshooting.md
```

### 5. Provide Recommendations
Based on findings, provide:
- Specific configuration changes with code examples
- Step-by-step remediation instructions
- Links to relevant sections in reference documentation
- Performance tuning suggestions with expected impact

## Common Issue Categories

### Network and Communication Issues
**Symptoms:** Slow distributed training, NCCL timeouts, EFA errors
**First Steps:**
1. Run `python scripts/diagnose_cluster.py` to check EFA status
2. Verify security group allows all traffic within cluster
3. Check NCCL environment variables
4. Read `references/troubleshooting.md` section 2 for detailed fixes

**Quick Fixes:**
```bash
# Verify EFA installation
fi_info -p efa

# Set NCCL environment variables
export NCCL_DEBUG=INFO
export NCCL_SOCKET_IFNAME=^docker,lo
export FI_PROVIDER=efa
export FI_EFA_USE_DEVICE_RDMA=1
```

### Storage Performance Issues
**Symptoms:** Slow data loading, I/O timeouts, training bottlenecks
**First Steps:**
1. Check FSx mount status and disk usage
2. Verify file striping configuration
3. Review data loading code for inefficiencies
4. Read `references/optimization_guide.md` section 2 for storage tuning

**Quick Fixes:**
```bash
# Check FSx mount
df -h | grep fsx
mount | grep lustre

# Optimize file striping for large datasets
lfs setstripe -c -1 /fsx/datasets

# Check I/O performance
lfs df -h
```

### GPU Utilization Problems
**Symptoms:** Low GPU utilization, slow training speed, GPU idle time
**First Steps:**
1. Monitor GPU utilization with `nvidia-smi dmon`
2. Check for CPU bottlenecks in data loading
3. Verify batch size and mixed precision settings
4. Read `references/optimization_guide.md` section 1 for compute optimization

**Quick Fixes:**
```python
# Optimize DataLoader
train_loader = DataLoader(
    dataset,
    batch_size=batch_size,
    num_workers=8,  # Increase for faster data loading
    pin_memory=True,
    prefetch_factor=2
)

# Enable automatic mixed precision
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()
```

### Job Failures and Node Issues
**Symptoms:** Jobs fail, nodes go down, jobs stuck in queue
**First Steps:**
1. Check Slurm status with `sinfo -Nel` and `squeue`
2. View job logs: `cat slurm-<job_id>.out`
3. Check node drain reasons: `sinfo -R`
4. Read `references/troubleshooting.md` section 1 for job failure analysis

**Quick Fixes:**
```bash
# Check job details
scontrol show job <job_id>

# Check node status
scontrol show nodes <node_name>

# Enable job requeue in script
#SBATCH --requeue
#SBATCH --signal=B:TERM@300
```

### Configuration Optimization
**Symptoms:** Want to optimize existing configuration, improve performance
**First Steps:**
1. Run `python scripts/analyze_job_config.py job_script.sh`
2. Review current resource allocation vs requirements
3. Check for missing optimizations (checkpointing, mixed precision, etc.)
4. Read `references/optimization_guide.md` for comprehensive tuning

## Script Usage Examples

### Diagnostic Script
```bash
# Basic diagnostics with output to screen
python scripts/diagnose_cluster.py

# Save detailed report
python scripts/diagnose_cluster.py -o cluster_report.txt

# JSON output for automation
python scripts/diagnose_cluster.py --json > cluster_status.json
```

**What it checks:**
- Slurm cluster health (nodes, jobs, partitions)
- GPU status (utilization, temperature, memory)
- EFA devices and configuration
- FSx mount points and storage
- NCCL environment variables

**Exit codes:**
- 0: No critical issues
- 1: Critical issues found (check report)

### Job Configuration Analyzer
```bash
# Analyze a Slurm batch script
python scripts/analyze_job_config.py train_job.sh

# Save analysis report
python scripts/analyze_job_config.py train_job.sh -o analysis.txt
```

**What it checks:**
- Resource allocation (nodes, GPUs, CPUs)
- Time limits and job requeue settings
- Distributed training configuration
- NCCL and EFA environment variables
- Checkpointing and fault tolerance
- Performance optimization settings

**Output includes:**
- Issues: Critical problems that should be fixed
- Warnings: Potential problems or misconfigurations
- Suggestions: Optimization opportunities

## Reference Documentation

This skill includes comprehensive reference material. Load as needed:

### references/hyperpod_architecture.md
**When to read:** Understanding cluster components, instance types, networking, storage architecture
**Contents:**
- Cluster architecture overview
- Instance types and configurations (P5, P4d, P4de)
- Network fabric (EFA, VPC)
- Storage systems (FSx, EFS, S3)
- Slurm integration concepts
- Resilience and auto-recovery features

### references/optimization_guide.md
**When to read:** Performance tuning, cost optimization, monitoring setup
**Contents:**
- Compute optimization (GPU utilization, multi-GPU training)
- Storage optimization (FSx tuning, S3 integration)
- Network optimization (EFA, NCCL)
- Training loop optimization (gradient accumulation, checkpointing)
- Slurm job optimization
- Cost optimization strategies
- Monitoring and profiling techniques

### references/troubleshooting.md
**When to read:** Diagnosing specific issues, fixing failures, debugging problems
**Contents:**
- Job failures and hangs (8 categories)
- EFA and network issues
- Storage and I/O issues
- GPU problems
- Out of memory errors
- Checkpoint and resume issues
- Distributed training problems
- Logging and debugging techniques

## Best Practices for User Interaction

### When Analyzing Issues
1. **Start with diagnostics:** Run scripts before deep investigation
2. **Be specific:** Provide exact commands and configuration changes
3. **Explain impact:** Describe what each change accomplishes
4. **Reference documentation:** Point users to relevant sections for deeper understanding
5. **Provide examples:** Include code snippets and command examples

### When Providing Solutions
1. **Prioritize fixes:** Address critical issues first, then optimizations
2. **Test recommendations:** Only suggest configurations you're confident will work
3. **Consider context:** Account for workload type, cluster size, budget constraints
4. **Be actionable:** Provide step-by-step instructions with exact commands
5. **Set expectations:** Explain expected performance improvements

### When Suggesting Optimizations
1. **Benchmark first:** Recommend measuring current performance before changes
2. **Iterative approach:** Suggest one optimization category at a time
3. **Quantify impact:** Estimate potential improvements (e.g., "should improve GPU utilization from 60% to 90%")
4. **Balance trade-offs:** Discuss cost vs performance considerations
5. **Monitor results:** Suggest metrics to track after implementing changes

## Key Environment Variables Reference

Quick reference for important environment variables (detailed info in references):

### NCCL Configuration
```bash
export NCCL_DEBUG=INFO              # Enable debug logging
export NCCL_SOCKET_IFNAME=^docker,lo  # Exclude non-EFA interfaces
export NCCL_PROTO=simple            # Protocol optimization
export NCCL_MIN_NRINGS=8            # Ring count for collectives
```

### EFA Configuration
```bash
export FI_PROVIDER=efa              # Use EFA provider
export FI_EFA_USE_DEVICE_RDMA=1     # Enable RDMA
export FI_EFA_FORK_SAFE=1           # Fork safety
```

### PyTorch Optimization
```bash
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512  # Memory management
export OMP_NUM_THREADS=12           # Control CPU parallelism
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7  # Specify GPUs
```

## Example Conversations

### Example 1: Performance Issue
**User:** "My distributed training is slow, only getting 30% GPU utilization."

**Response:**
```
Let me help diagnose the GPU utilization issue. First, let's run diagnostics:

python scripts/diagnose_cluster.py

Based on 30% GPU utilization, this is likely a data loading bottleneck. Let me check a few things:

1. How many CPU cores are allocated per GPU in your job script?
2. Can you share your DataLoader configuration?

In the meantime, try these quick fixes:

# Increase DataLoader workers
train_loader = DataLoader(
    dataset,
    batch_size=batch_size,
    num_workers=12,  # Match CPU cores per GPU
    pin_memory=True,
    prefetch_factor=2
)

# Enable automatic mixed precision to reduce compute time
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    output = model(input)
    loss = criterion(output, target)

Also verify your Slurm job allocates enough CPUs:
#SBATCH --cpus-per-task=12  # 12 CPUs per GPU

For comprehensive optimization strategies, see references/optimization_guide.md section 1.
```

### Example 2: Job Configuration Review
**User:** "Can you review my training script for best practices?" [attaches script]

**Response:**
```
I'll analyze your job script for best practices and optimizations:

python scripts/analyze_job_config.py your_script.sh

Based on the analysis, here are the key findings:

ISSUES:
- No checkpoint saving detected - add checkpointing for fault tolerance
- Missing NCCL environment variables for EFA optimization

SUGGESTIONS:
1. Add checkpointing (every N steps):
   if step % checkpoint_interval == 0:
       torch.save({
           'epoch': epoch,
           'model_state': model.state_dict(),
           'optimizer_state': optimizer.state_dict()
       }, f'checkpoint_{step}.pt')

2. Add NCCL configuration for EFA:
   export NCCL_SOCKET_IFNAME=^docker,lo
   export FI_PROVIDER=efa
   export FI_EFA_USE_DEVICE_RDMA=1

3. Enable job requeue for auto-restart on failure:
   #SBATCH --requeue
   #SBATCH --signal=B:TERM@300

See references/optimization_guide.md sections 4-5 for detailed guidance.
```

### Example 3: Cluster Issue
**User:** "My jobs keep failing with NCCL timeout errors."

**Response:**
```
NCCL timeout errors typically indicate network communication issues. Let's diagnose:

python scripts/diagnose_cluster.py

This will check EFA status. Meanwhile, verify these:

1. Check EFA is properly installed:
   fi_info -p efa

2. Verify security group allows all traffic within cluster:
   - All protocols, all ports between nodes
   - Security group should reference itself

3. Set proper NCCL environment variables:
   export NCCL_DEBUG=INFO
   export NCCL_SOCKET_IFNAME=^docker,lo
   export FI_PROVIDER=efa
   export FI_EFA_USE_DEVICE_RDMA=1

4. Increase NCCL timeout in your code:
   dist.init_process_group(
       backend='nccl',
       timeout=datetime.timedelta(minutes=30)  # Increase from default
   )

For detailed troubleshooting steps, read references/troubleshooting.md section 2.

What does the diagnostic script show for EFA status?
```
