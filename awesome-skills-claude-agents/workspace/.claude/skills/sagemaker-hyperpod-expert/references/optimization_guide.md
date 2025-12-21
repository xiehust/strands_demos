# HyperPod Optimization Guide

## Performance Optimization

### 1. Compute Optimization

#### GPU Utilization
- **Target**: >90% GPU utilization during training
- **Monitor**: `nvidia-smi dmon -s u` for real-time utilization
- **Common issues**:
  - CPU bottlenecks in data loading
  - Inefficient data preprocessing
  - Small batch sizes
  - Suboptimal mixed precision settings

**Solutions**:
```python
# Use DataLoader with multiple workers
train_loader = DataLoader(
    dataset,
    batch_size=batch_size,
    num_workers=8,  # Tune based on CPU cores
    pin_memory=True,
    prefetch_factor=2
)

# Enable automatic mixed precision
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    output = model(input)
    loss = criterion(output, target)
```

#### Multi-GPU Training
- Use DistributedDataParallel (DDP) over DataParallel
- Enable NCCL optimizations
- Proper gradient accumulation

```python
# NCCL environment variables
export NCCL_DEBUG=INFO
export NCCL_SOCKET_IFNAME=^docker,lo
export NCCL_MIN_NRINGS=8
export NCCL_TREE_THRESHOLD=0
export NCCL_IB_DISABLE=0
export NCCL_NET_GDR_LEVEL=5
```

### 2. Storage Optimization

#### FSx for Lustre Tuning

**File Striping**:
```bash
# Set stripe count for large files
lfs setstripe -c -1 /fsx/checkpoints  # Use all OSTs
lfs setstripe -c 4 /fsx/datasets      # Use 4 OSTs

# Check striping configuration
lfs getstripe /fsx/path/to/file
```

**Client-Side Optimization**:
```bash
# Mount options in /etc/fstab
fs-xxxxx.fsx.region.amazonaws.com@tcp:/fsx /mnt/fsx lustre defaults,noatime,flock,_netdev 0 0

# Tune client cache
lctl set_param osc.*.max_dirty_mb=256
lctl set_param osc.*.max_pages_per_rpc=1024
```

**I/O Patterns**:
- Sequential reads: Best performance
- Random reads: Use client caching
- Write patterns: Buffer when possible
- Avoid small file creation/deletion in hot paths

#### S3 Integration
- Use S3 data repository associations
- Lazy load with automatic import
- Batch checkpoint uploads
- Use S3 Transfer Acceleration for cross-region

### 3. Network Optimization

#### EFA Tuning
```bash
# Verify EFA installation
fi_info -p efa

# EFA environment variables
export FI_PROVIDER=efa
export FI_EFA_USE_DEVICE_RDMA=1
export FI_EFA_FORK_SAFE=1

# AWS OFI NCCL plugin
export LD_LIBRARY_PATH=/opt/amazon/efa/lib:$LD_LIBRARY_PATH
export NCCL_PROTO=simple
```

#### NCCL Collective Operations
- All-reduce: Most common for gradient synchronization
- All-gather: For gathering distributed data
- Broadcast: For weight initialization

**Benchmarking**:
```bash
# NCCL tests
/opt/nccl-tests/build/all_reduce_perf -b 8 -e 1G -f 2 -g 8
```

### 4. Training Loop Optimization

#### Gradient Accumulation
```python
# Accumulate gradients over multiple steps
accumulation_steps = 4
optimizer.zero_grad()

for i, (inputs, labels) in enumerate(train_loader):
    outputs = model(inputs)
    loss = criterion(outputs, labels) / accumulation_steps
    loss.backward()

    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

#### Checkpointing Strategy
- Checkpoint frequency: Balance durability vs performance
- Asynchronous checkpointing when possible
- Incremental checkpoints for large models

```python
# Asynchronous checkpoint saving
import torch.distributed.checkpoint as dist_cp

def save_checkpoint_async(model, optimizer, epoch):
    checkpoint = {
        'epoch': epoch,
        'model_state': model.state_dict(),
        'optimizer_state': optimizer.state_dict()
    }

    # Save to local storage first
    torch.save(checkpoint, f'/tmp/checkpoint_{epoch}.pt')

    # Upload to S3 asynchronously
    upload_to_s3_async(f'/tmp/checkpoint_{epoch}.pt',
                       f's3://bucket/checkpoints/checkpoint_{epoch}.pt')
```

### 5. Slurm Job Optimization

#### Resource Allocation
```bash
#!/bin/bash
#SBATCH --job-name=training
#SBATCH --nodes=4              # Number of nodes
#SBATCH --ntasks-per-node=8   # GPUs per node
#SBATCH --cpus-per-task=12    # CPU cores per GPU
#SBATCH --gres=gpu:8          # Request 8 GPUs per node
#SBATCH --time=48:00:00       # Max runtime
#SBATCH --exclusive           # Exclusive node access

# Enable job requeue on failure
#SBATCH --requeue
#SBATCH --signal=B:TERM@300  # Send SIGTERM 5 min before timeout
```

#### Job Arrays for Hyperparameter Tuning
```bash
#!/bin/bash
#SBATCH --array=0-9           # 10 parallel jobs

# Each job gets different hyperparameters
learning_rates=(0.001 0.0005 0.0001)
batch_sizes=(32 64 128)

idx=$SLURM_ARRAY_TASK_ID
lr=${learning_rates[$((idx / 3))]}
bs=${batch_sizes[$((idx % 3))]}

python train.py --lr $lr --batch-size $bs
```

## Cost Optimization

### 1. Instance Selection
- Use Savings Plans for predictable workloads
- Spot instances for fault-tolerant training (with checkpointing)
- Right-size instance types based on model requirements

### 2. Storage Optimization
- Use S3 Intelligent-Tiering for datasets
- Delete old checkpoints programmatically
- Compress checkpoints when possible
- Use FSx for Lustre data compression

### 3. Efficient Training Practices
- Early stopping with validation monitoring
- Learning rate warmup and scheduling
- Transfer learning instead of training from scratch
- Model pruning and quantization for inference

## Monitoring and Profiling

### Key Metrics to Track

1. **GPU Metrics**
   - Utilization (%)
   - Memory usage
   - Temperature
   - SM efficiency

2. **Network Metrics**
   - EFA throughput
   - NCCL bandwidth
   - Latency

3. **Storage Metrics**
   - FSx throughput (MB/s)
   - IOPS
   - Client cache hit rate

4. **Training Metrics**
   - Samples per second
   - Time per iteration
   - Loss convergence
   - Gradient norms

### Profiling Tools

```python
# PyTorch Profiler
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True
) as prof:
    for batch in train_loader:
        output = model(batch)
        loss = criterion(output, target)
        loss.backward()

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

### CloudWatch Integration
- Custom metrics for training progress
- Alarms for resource utilization
- Dashboards for cluster health
- Log aggregation with CloudWatch Logs
