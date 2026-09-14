#!/bin/bash
# Resource limits verified with MyTCInfo on 2026-09-13.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=06:00:00
#SBATCH --job-name=sc4001-pa1-partb
#SBATCH --output=outputs/slurm/part_b_%j.out
#SBATCH --error=outputs/slurm/part_b_%j.err

set -euo pipefail

export CUBLAS_WORKSPACE_CONFIG=:4096:8

project_dir="${SLURM_SUBMIT_DIR:-$PWD}"
venv_dir="${SC4001_VENV:-${HOME}/sc4001-venv}"
cd "$project_dir"
mkdir -p outputs/slurm

nvidia-smi
"$venv_dir/bin/python" \
    -m src.run_part_b --stage train --device cuda --num-workers 4
