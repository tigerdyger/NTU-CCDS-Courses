#!/bin/bash
# Local diagnostic experiments only; not the student submission notebook.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=00:20:00
#SBATCH --job-name=sc3000-sft-dpo
#SBATCH --output=outputs/slurm/sft_dpo_%j.out
#SBATCH --error=outputs/slurm/sft_dpo_%j.err

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit from the lab root}"
sc3000_python="${SC3000_PYTHON:-${HOME}/sc4001-venv/bin/python}"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
hostname
"$sc3000_python" -m unittest discover -s tests-local -p 'test_*.py' -v 2>&1
sc3000_extra=()
if [ -n "${SC3000_MAX_STEPS:-}" ]; then
    sc3000_extra+=(--max-steps "$SC3000_MAX_STEPS")
fi
"$sc3000_python" -u tests-local/sft_dpo_experiment.py \
    --device cuda --stage "${SC3000_STAGE:?Specify fit, sft, or dpo}" \
    --data-dir "${SC3000_DATA_DIR:-work/dpo/math-v1-mixed}" \
    --init-checkpoint "${SC3000_INIT:-work/sft/gpt.pt}" \
    --learning-rate "${SC3000_LR:?Specify a stage learning rate}" \
    --epochs "${SC3000_EPOCHS:-5}" --beta "${SC3000_BETA:-0.1}" \
    --output-dir "outputs/${SC3000_STAGE}-tc1-${SLURM_JOB_ID}" "${sc3000_extra[@]}"
