#!/bin/bash
# Diagnostic only, not a formal Lab 1 training run.
# Resource limits checked using MyTCinfo on 2026-09-15.
# Create outputs/slurm before submitting this file from the lab root.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --job-name=sc3000-lab1-smoke
#SBATCH --output=outputs/slurm/baseline_smoke_%j.out
#SBATCH --error=outputs/slurm/baseline_smoke_%j.err

set -euo pipefail

cd "${SLURM_SUBMIT_DIR:?Submit this job through sbatch from the lab root}"
sc3000_python="${SC3000_PYTHON:-${HOME}/sc4001-venv/bin/python}"
test -x "$sc3000_python"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

# Preserve Slurm's CUDA_VISIBLE_DEVICES; do not hard-code a GPU index.
hostname
nvidia-smi
"$sc3000_python" -u tests-local/baseline_smoke.py \
    --device cuda --steps 4 \
    --output-dir "outputs/baseline-smoke-tc1-${SLURM_JOB_ID}"
