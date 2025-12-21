# HyperPod Troubleshooting Guide

## Common Issues and Solutions

### 1. Job Failures and Hangs

#### Symptoms
- Jobs stuck in pending state
- Jobs fail immediately after start
- Jobs hang during execution
- Inconsistent job completion times

#### Diagnostic Commands
```bash
# Check job status
squeue -u $USER
scontrol show job <job_id>

# Check node status
sinfo -Nel
scontrol show nodes <node_name>

# View job logs
cat slurm-<job_id>.out
journalctl -u slurmd  # On compute node
```

#### Common Causes and Solutions

**Insufficient Resources**:
```bash
# Check available resources
sinfo -o "%n %C %m %e"

# View partition limits
scontrol show partition

# Solution: Request fewer resources or wait for availability
```

**Node Health Issues**:
```bash
# Check node drain reason
sinfo -R

# Manually drain problematic node (admin)
scontrol update NodeName=<node> State=DRAIN Reason="debugging"

# Resume node after fix
scontrol update NodeName=<node> State=RESUME
```

**Job Time Limit**:
- Solution: Increase time limit in job script or implement checkpointing

### 2. EFA and Network Issues

#### Symptoms
- Slow distributed training
- NCCL timeout errors
- EFA device not found
- Network bandwidth lower than expected

#### Diagnostics
```bash
# Verify EFA installation
fi_info -p efa

# Check EFA device
ibv_devinfo

# Test EFA bandwidth between nodes
# On node 1:
ib_send_bw -d <efa_device>
# On node 2:
ib_send_bw -d <efa_device> <node1_ip>

# NCCL test
mpirun -np 16 -N 8 \
  --map-by ppr:8:node \
  -x NCCL_DEBUG=INFO \
  /opt/nccl-tests/build/all_reduce_perf -b 8 -e 1G -f 2 -g 8
```

#### Common Solutions

**EFA Driver Issues**:
```bash
# Reinstall EFA driver
curl -O https://efa-installer.amazonaws.com/aws-efa-installer-latest.tar.gz
tar -xf aws-efa-installer-latest.tar.gz
cd aws-efa-installer
sudo ./efa_installer.sh -y

# Verify installation
modprobe efa
fi_info -p efa
```

**Security Group Configuration**:
- Ensure all traffic is allowed within cluster security group
- EFA requires all protocols and all ports within the security group

**NCCL Configuration**:
```bash
# Add to job script
export NCCL_DEBUG=INFO
export NCCL_SOCKET_IFNAME=^docker,lo
export FI_PROVIDER=efa
export FI_EFA_USE_DEVICE_RDMA=1
export NCCL_PROTO=simple
```

### 3. Storage and I/O Issues

#### FSx for Lustre Problems

**Symptoms**:
- Slow data loading
- I/O timeouts
- "Cannot allocate memory" errors
- Metadata operation slowness

**Diagnostics**:
```bash
# Check FSx mount status
df -h | grep fsx
mount | grep lustre

# Check Lustre client health
lctl ping <MGS_NID>
lctl dl

# Monitor I/O performance
lfs df -h
lctl get_param osc.*.stats

# Check file striping
lfs getstripe /fsx/path/to/file
```

**Solutions**:

*Remount FSx*:
```bash
sudo umount /fsx
sudo mount -t lustre -o noatime fs-xxxxx.fsx.region.amazonaws.com@tcp:/fsx /fsx
```

*Optimize Striping*:
```bash
# For large files/directories
lfs setstripe -c -1 /fsx/large_datasets

# For many small files
lfs setstripe -c 1 /fsx/small_files
```

*Clear Client Cache*:
```bash
# Drop caches
echo 3 | sudo tee /proc/sys/vm/drop_caches

# Reconnect Lustre client
sudo lctl set_param osc.*.force_sync=1
```

**S3 Data Repository Issues**:
```bash
# Check DRA status
aws fsx describe-data-repository-associations

# Force import from S3
aws fsx create-data-repository-task \
  --file-system-id fs-xxxxx \
  --type IMPORT_METADATA_FROM_REPOSITORY \
  --paths /path/to/import

# Check import task status
aws fsx describe-data-repository-tasks
```

### 4. GPU Issues

#### Symptoms
- GPU not detected
- CUDA errors
- GPU memory errors
- Performance degradation

**Diagnostics**:
```bash
# Check GPU status
nvidia-smi

# Continuous monitoring
nvidia-smi dmon -s pucvmet

# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.device_count())"

# Check ECC errors
nvidia-smi -q | grep -A 5 "ECC Errors"

# Check GPU clocks
nvidia-smi -q -d CLOCK
```

**Solutions**:

*GPU Not Detected*:
```bash
# Reload NVIDIA driver
sudo modprobe -r nvidia_uvm nvidia_drm nvidia_modeset nvidia
sudo modprobe nvidia nvidia_modeset nvidia_drm nvidia_uvm

# Verify
nvidia-smi
```

*GPU Memory Issues*:
```python
# Clear PyTorch cache
import torch
torch.cuda.empty_cache()

# Enable gradient checkpointing
from torch.utils.checkpoint import checkpoint

class MyModel(nn.Module):
    def forward(self, x):
        return checkpoint(self.layer, x)
```

*Reset GPU State*:
```bash
# Reset all GPUs
sudo nvidia-smi --gpu-reset

# Or reset specific GPU
sudo nvidia-smi -i 0 --gpu-reset
```

### 5. Out of Memory (OOM) Errors

#### Diagnostic Steps

```python
# Monitor memory usage
import torch
print(f"Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"Cached: {torch.cuda.memory_reserved() / 1e9:.2f} GB")

# Get memory summary
print(torch.cuda.memory_summary())

# Find memory leaks
import gc
gc.collect()
torch.cuda.empty_cache()
```

#### Solutions

**Reduce Batch Size**:
```python
# Gradient accumulation for effective large batch
effective_batch_size = 512
per_gpu_batch = 64
accumulation_steps = effective_batch_size // (per_gpu_batch * num_gpus)
```

**Enable Gradient Checkpointing**:
```python
from transformers import AutoModel

model = AutoModel.from_pretrained("model_name")
model.gradient_checkpointing_enable()
```

**Use Mixed Precision**:
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
with autocast():
    output = model(input)
    loss = criterion(output, target)
scaler.scale(loss).backward()
```

**Optimize Model Architecture**:
```python
# Use memory-efficient attention
from xformers.ops import memory_efficient_attention

# Or use Flash Attention
from flash_attn import flash_attn_func
```

### 6. Checkpoint and Resume Issues

#### Symptoms
- Cannot load checkpoint
- Training state not restored correctly
- Checkpoint corruption

**Diagnostics**:
```python
# Check checkpoint integrity
import torch
checkpoint = torch.load('checkpoint.pt', map_location='cpu')
print(checkpoint.keys())

# Verify model state dict compatibility
model_keys = set(model.state_dict().keys())
checkpoint_keys = set(checkpoint['model_state_dict'].keys())
print(f"Missing keys: {model_keys - checkpoint_keys}")
print(f"Unexpected keys: {checkpoint_keys - model_keys}")
```

**Solutions**:

*Robust Checkpoint Saving*:
```python
import torch
import os
import tempfile
import shutil

def save_checkpoint_safely(state, filepath):
    """Save checkpoint atomically to prevent corruption."""
    # Save to temporary file first
    tmp_path = tempfile.mktemp(dir=os.path.dirname(filepath))
    torch.save(state, tmp_path)

    # Atomic rename
    shutil.move(tmp_path, filepath)

# Use in training loop
if rank == 0:  # Only save on main process
    state = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict(),
        'loss': loss,
        'rng_state': torch.get_rng_state()
    }
    save_checkpoint_safely(state, f'checkpoint_epoch_{epoch}.pt')
```

*Handle Job Preemption*:
```python
import signal
import sys

def signal_handler(sig, frame):
    """Handle SIGTERM for graceful shutdown."""
    print("Received SIGTERM, saving checkpoint...")
    save_checkpoint_safely(get_current_state(), 'checkpoint_preempt.pt')
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
```

### 7. Distributed Training Issues

#### Symptoms
- Processes hang during initialization
- Training speed inconsistent across nodes
- Gradient synchronization errors

**Diagnostics**:
```bash
# Check process status
ps aux | grep python

# Check distributed training logs
cat slurm-<job_id>.out | grep -i "rank\|error\|timeout"

# Verify network connectivity between nodes
# On each node:
hostname -I
ping <other_node_ip>
```

**Solutions**:

*Proper Distributed Initialization*:
```python
import torch.distributed as dist
import os

def setup_distributed():
    """Initialize distributed training properly."""
    # Slurm environment variables
    rank = int(os.environ['SLURM_PROCID'])
    local_rank = int(os.environ['SLURM_LOCALID'])
    world_size = int(os.environ['SLURM_NTASKS'])

    # Set device
    torch.cuda.set_device(local_rank)

    # Initialize process group with timeout
    dist.init_process_group(
        backend='nccl',
        init_method='env://',
        world_size=world_size,
        rank=rank,
        timeout=datetime.timedelta(minutes=30)
    )

    return rank, local_rank, world_size
```

*Slurm Launch Script*:
```bash
#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=8
#SBATCH --gres=gpu:8

# Get master node
export MASTER_ADDR=$(scontrol show hostnames $SLURM_JOB_NODELIST | head -n 1)
export MASTER_PORT=12355

# Launch training
srun python train.py \
  --distributed \
  --nodes=$SLURM_JOB_NUM_NODES \
  --gpus=8
```

### 8. Logging and Debugging

#### Enable Comprehensive Logging

```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'training_rank_{rank}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Starting training on rank {rank}")
logger.info(f"Batch size: {batch_size}, Learning rate: {lr}")
```

#### Debug Mode

```bash
# Run with Python debugger
srun python -m pdb train.py

# Or use ipdb for better interface
srun python -m ipdb train.py

# Enable PyTorch anomaly detection
export TORCH_ANOMALY_DETECT=1
```

### Emergency Commands

```bash
# Cancel all your jobs
scancel -u $USER

# Cancel specific partition
scancel -u $USER -p <partition_name>

# Drain node immediately (admin)
scontrol update NodeName=<node> State=DRAIN Reason="emergency"

# Force kill processes on node
pkill -9 -u $USER python
```
