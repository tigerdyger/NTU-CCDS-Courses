#!/bin/bash
# Install a minimal, project-local runtime on a compute node.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --job-name=sc4001-env-setup
#SBATCH --output=outputs/slurm/env_setup_%j.out
#SBATCH --error=outputs/slurm/env_setup_%j.err

set -euo pipefail

project_dir="${SLURM_SUBMIT_DIR:-$PWD}"
venv_dir="${SC4001_VENV:-${HOME}/sc4001-venv}"
export UV_CACHE_DIR="${TMPDIR:-/tmp}/sc4001-uv-cache-${SLURM_JOB_ID}"
export UV_LINK_MODE=copy
cd "$project_dir"

module load uv
module load python/3.11

if [[ ! -x "$venv_dir/bin/python" ]]; then
    uv venv --python python3.11 "$venv_dir"
fi

uv pip install \
    --python "$venv_dir/bin/python" \
    --index-url https://download.pytorch.org/whl/cu118 \
    --extra-index-url https://pypi.org/simple \
    --index-strategy unsafe-best-match \
    --link-mode copy \
    "torch==2.5.1+cu118" \
    "numpy==2.1.3"

"$venv_dir/bin/python" -c "import numpy, torch; print(torch.__version__, torch.version.cuda, numpy.__version__)"
