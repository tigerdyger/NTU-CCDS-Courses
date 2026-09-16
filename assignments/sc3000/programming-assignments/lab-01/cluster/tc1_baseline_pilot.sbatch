#!/bin/bash
# Development-only experiment; the holdout must remain unevaluated.
#SBATCH --partition=UGGPU-TC1
#SBATCH --qos=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --gres=gpu:1
#SBATCH --mem=16G
#SBATCH --time=00:20:00
#SBATCH --job-name=sc3000-lab1-pilot
#SBATCH --output=outputs/slurm/baseline_pilot_%j.out
#SBATCH --error=outputs/slurm/baseline_pilot_%j.err

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit from the lab root}"
sc3000_python="${SC3000_PYTHON:-${HOME}/sc4001-venv/bin/python}"
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="${SLURM_CPUS_PER_TASK}"
hostname
if [ "${SC3000_SCORE_SCOPE:-full}" = response ]; then
    "$sc3000_python" -m unittest discover -s tests-local -p test_response_scoring.py -v 2>&1
fi
"$sc3000_python" -u tests-local/baseline_pilot.py \
    --device cuda --data-dir "${SC3000_DATA_DIR:-work/dpo/math-v1-mixed}" \
    --epochs "${SC3000_EPOCHS:-1}" --learning-rate "${SC3000_LR:-1e-4}" \
    --score-scope "${SC3000_SCORE_SCOPE:-full}" \
    --output-dir "outputs/baseline-pilot-tc1-${SLURM_JOB_ID}"
