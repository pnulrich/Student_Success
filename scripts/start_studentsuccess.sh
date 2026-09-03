#!/usr/bin/env bash
# NOTE:
#   This launcher has not yet been tested on Linux or macOS.
#   It is intended to provide functionality equivalent to the tested
#   Windows start_studentsuccess.bat launcher. Verify Conda discovery,
#   environment activation, and JupyterLab startup before relying on it
#   in a Linux or macOS environment.

set -euo pipefail

# ============================================================================
# StudentSuccess JupyterLab Launcher - macOS/Linux
#
# Purpose:
#   Activates the StudentSuccess Conda development environment and launches
#   JupyterLab in the user's configured analysis-notebook directory.
#
# Configuration:
#   The notebook directory is intentionally stored outside this script so
#   that the repository does not contain machine-specific absolute paths.
#
#   Required user environment variable:
#       STUDENT_SUCCESS_NOTEBOOK_DIR
#
#   Example:
#       export STUDENT_SUCCESS_NOTEBOOK_DIR="$HOME/Research/HHMI_IE3/Analyses/jupyter_notebooks"
#
#   The script automatically searches common Anaconda/Miniconda installation
#   locations. Conda does not need to already be initialized in the shell.
# ============================================================================


# ---- StudentSuccess Conda environment ---------------------------------------
# This environment should be created from the project's environment files.
ENV_NAME="student_success_dev"


# ---- Verify notebook-directory configuration -------------------------------
# STUDENT_SUCCESS_NOTEBOOK_DIR keeps the analysis workspace independent of
# the StudentSuccess source-code repository.
if [[ -z "${STUDENT_SUCCESS_NOTEBOOK_DIR:-}" ]]; then
    echo "ERROR: STUDENT_SUCCESS_NOTEBOOK_DIR is not defined."
    echo
    echo "Set it to the directory containing your StudentSuccess notebooks."
    echo
    echo "Example:"
    echo 'export STUDENT_SUCCESS_NOTEBOOK_DIR="$HOME/Research/HHMI_IE3/Analyses/jupyter_notebooks"'
    exit 1
fi

# Fail rather than creating a missing directory automatically. This prevents
# a typo in the environment variable from silently creating and opening an
# unintended notebook directory.
if [[ ! -d "${STUDENT_SUCCESS_NOTEBOOK_DIR}" ]]; then
    echo "ERROR: Notebook directory not found:"
    echo "${STUDENT_SUCCESS_NOTEBOOK_DIR}"
    exit 1
fi


# ---- Locate Conda -----------------------------------------------------------
# Search common per-user Anaconda and Miniconda installation locations.
# Sourcing conda.sh enables "conda activate" within this shell script.
CONDA_INIT=""

if [[ -f "${HOME}/anaconda3/etc/profile.d/conda.sh" ]]; then
    CONDA_INIT="${HOME}/anaconda3/etc/profile.d/conda.sh"
elif [[ -f "${HOME}/miniconda3/etc/profile.d/conda.sh" ]]; then
    CONDA_INIT="${HOME}/miniconda3/etc/profile.d/conda.sh"
elif [[ -f "${HOME}/opt/anaconda3/etc/profile.d/conda.sh" ]]; then
    CONDA_INIT="${HOME}/opt/anaconda3/etc/profile.d/conda.sh"
elif [[ -f "${HOME}/opt/miniconda3/etc/profile.d/conda.sh" ]]; then
    CONDA_INIT="${HOME}/opt/miniconda3/etc/profile.d/conda.sh"
fi

# Stop with a useful message if no supported Conda installation was found.
if [[ -z "${CONDA_INIT}" ]]; then
    echo "ERROR: Could not locate an Anaconda or Miniconda installation."
    echo "Checked common locations under your home directory."
    echo
    echo "If Conda is installed elsewhere, update this script or initialize"
    echo "Conda for your shell before launching StudentSuccess."
    exit 1
fi


# ---- Activate StudentSuccess environment -----------------------------------
# shellcheck disable=SC1090
source "${CONDA_INIT}"

if ! conda activate "${ENV_NAME}"; then
    echo "ERROR: Could not activate Conda environment ${ENV_NAME}."
    exit 1
fi


# ---- Launch JupyterLab ------------------------------------------------------
# Start JupyterLab from the external analysis workspace rather than from the
# source-code repository.
cd "${STUDENT_SUCCESS_NOTEBOOK_DIR}"
jupyter lab