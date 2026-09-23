#!/bin/bash
# Execute a fresh copy of the notebook without inserting diagnostic cells or
# changing any source cell. Keep all outputs under a new per-job directory.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --job-name=sc3000-canonical
#SBATCH --output=outputs/slurm/canonical_%j.out
#SBATCH --error=outputs/slurm/canonical_%j.err

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit this job from the lab root}"
sc3000_python="${SC3000_PYTHON:-${HOME}/sc3000-notebook-venv/bin/python}"
test -x "$sc3000_python"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"

hostname
nvidia-smi
"$sc3000_python" -u tests-local/run_student_notebook.py \
    --mode canonical --device cuda \
    --output-dir "outputs/student-notebook-canonical-${SLURM_JOB_ID}"
