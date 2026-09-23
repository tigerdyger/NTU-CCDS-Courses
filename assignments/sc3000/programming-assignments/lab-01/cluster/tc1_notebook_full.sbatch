#!/bin/bash
# Isolated notebook verification. Submit from the lab root after creating outputs/slurm.
# The runner copies the notebook and inputs to fresh outputs directories; it does not
# overwrite the canonical work/dpo files or earlier completed experiments.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --job-name=sc3000-notebook
#SBATCH --output=outputs/slurm/notebook_%j.out
#SBATCH --error=outputs/slurm/notebook_%j.err

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
    --mode smoke --device cuda \
    --output-dir "outputs/student-notebook-gpu-smoke-${SLURM_JOB_ID}"
"$sc3000_python" -u tests-local/run_student_notebook.py \
    --mode full --device cuda \
    --output-dir "outputs/student-notebook-tc1-${SLURM_JOB_ID}"
