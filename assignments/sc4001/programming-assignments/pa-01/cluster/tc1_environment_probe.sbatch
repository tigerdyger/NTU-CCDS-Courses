#!/bin/bash
# Resource limits verified with MyTCinfo on 2026-09-13.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --job-name=sc4001-env-probe
#SBATCH --output=outputs/slurm/env_probe_%j.out
#SBATCH --error=outputs/slurm/env_probe_%j.err

set -euo pipefail

export CUBLAS_WORKSPACE_CONFIG=:4096:8

project_dir="${SLURM_SUBMIT_DIR:-$PWD}"
venv_dir="${SC4001_VENV:-${HOME}/sc4001-venv}"
cd "$project_dir"

nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
"$venv_dir/bin/python" - <<'PY'
import platform

import numpy
import torch

print(f"python={platform.python_version()}")
print(f"torch={torch.__version__}")
print(f"torch_cuda_build={torch.version.cuda}")
print(f"cuda_available={torch.cuda.is_available()}")
print(f"numpy={numpy.__version__}")
if not torch.cuda.is_available():
    raise RuntimeError("The allocated compute node is not CUDA-visible to PyTorch")
device = torch.device("cuda")
probe = torch.ones(8, device=device).square().sum()
print(f"gpu={torch.cuda.get_device_name(0)}")
print(f"cuda_probe={probe.item()}")
PY
