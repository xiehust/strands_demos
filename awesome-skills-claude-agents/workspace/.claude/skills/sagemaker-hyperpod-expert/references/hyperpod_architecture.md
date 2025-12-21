# SageMaker HyperPod Architecture Reference

## Overview

SageMaker HyperPod is a purpose-built infrastructure for distributed training at scale. It provides resilient, high-performance compute clusters optimized for training large foundation models and other ML workloads.

## Cluster Architecture

### Core Components

1. **Compute Instances**
   - GPU instances (p4d.24xlarge, p5.48xlarge, etc.)
   - CPU instances for data processing
   - Instance groups with auto-recovery

2. **Storage Systems**
   - FSx for Lustre (high-performance parallel file system)
   - EFS for shared configuration
   - S3 for data lakes and checkpoints

3. **Network Fabric**
   - EFA (Elastic Fabric Adapter) for low-latency inter-node communication
   - VPC configuration with proper security groups
   - Multi-AZ support for high availability

4. **Orchestration Layer**
   - Slurm workload manager
   - Kubernetes (optional)
   - Job scheduling and resource allocation

### Instance Types and Configurations

**P5 Instances (Latest Generation)**
- p5.48xlarge: 8x H100 GPUs, 640GB GPU memory
- Best for: Large language models, multi-modal training
- Network: 3200 Gbps EFA bandwidth

**P4d Instances**
- p4d.24xlarge: 8x A100 GPUs, 320GB GPU memory
- Network: 400 Gbps EFA bandwidth
- Best for: Most distributed training workloads

**P4de Instances**
- p4de.24xlarge: 8x A100 GPUs with 80GB each
- Total: 640GB GPU memory per instance
- Best for: Memory-intensive models

## Resilience Features

### Auto-Recovery
- Health checks for compute nodes
- Automatic replacement of failed instances
- Checkpoint/resume functionality
- Job requeue on failure

### Data Durability
- FSx snapshots and backups
- S3 checkpoint versioning
- Multi-AZ replication options

## Slurm Integration

### Key Concepts

**Partitions**: Logical groupings of nodes with similar characteristics
**Jobs**: User-submitted workloads with resource requirements
**Nodes**: Individual compute instances in the cluster
**Steps**: Individual tasks within a job

### Common Slurm Commands

```bash
# View cluster status
sinfo

# View job queue
squeue

# Submit job
sbatch script.sh

# Cancel job
scancel <job_id>

# View node details
scontrol show nodes

# View job details
scontrol show job <job_id>
```

## Network Configuration

### EFA Requirements
- Security group rules for EFA traffic
- Placement groups for optimal topology
- EFA driver installation and configuration
- NCCL tuning for collective operations

### VPC Best Practices
- Use private subnets for compute nodes
- NAT gateway for internet access
- VPC endpoints for AWS services
- Security groups with minimal required access

## Storage Configuration

### FSx for Lustre
- Deployment type: PERSISTENT_2 for production
- Storage capacity: Scale based on dataset size
- Throughput: 1000 MB/s/TiB or higher
- Data repository associations for S3 integration

### Performance Tuning
- Lustre striping for large files
- Client-side caching
- Parallel I/O patterns
- Metadata server optimization
