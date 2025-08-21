#!/usr/bin/env bash
# === StudentSuccess Jupyter launcher (macOS) ===
set -euo pipefail

# ---- Settings (change if needed) ----
ENV_NAME="student_success_dev"
NOTEBOOK_DIR="$(cd "$(dirname "$0")" && pwd)/jupyter_notebooks"
# If you installed Miniconda elsewhere, modify this line:
CONDA_INIT="${HOME}/miniconda3/etc/profile.d/conda.sh"
# -------------------------------------

if [ ! -f "${CONDA_INIT}" ]; then
  echo "Could not find conda initialization script at: ${CONDA_INIT}"
  echo "If Miniconda is installed somewhere else, edit this file and update CONDA_INIT."
  exit 1
fi

# Initialize Conda for this shell and activate env
# shellcheck disable=SC1090
source "${CONDA_INIT}"
conda activate "${ENV_NAME}"

# Launch JupyterLab in the notebooks directory
mkdir -p "${NOTEBOOK_DIR}"
cd "${NOTEBOOK_DIR}"
jupyter lab
