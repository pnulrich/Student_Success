@echo off
setlocal

REM ============================================================================
REM StudentSuccess JupyterLab Launcher - Windows
REM
REM Purpose:
REM   Activates the StudentSuccess Conda development environment and launches
REM   JupyterLab in the user's configured analysis-notebook directory.
REM
REM Configuration:
REM   The notebook directory is intentionally stored outside this script so
REM   that the repository does not contain machine-specific absolute paths.
REM
REM   Required user environment variable:
REM       STUDENT_SUCCESS_NOTEBOOK_DIR
REM
REM   Example:
REM       C:\Research\Research Projects\GSU\HHMI_IE3\Analyses\jupyter_notebooks
REM
REM   The script automatically searches common Windows Anaconda/Miniconda
REM   installation locations. Conda does not need to be on the system PATH.
REM ============================================================================


REM ---- StudentSuccess Conda environment --------------------------------------
REM This environment should be created from the project's environment files.
set "ENV_NAME=student_success_dev"


REM ---- Verify notebook-directory configuration -------------------------------
REM STUDENT_SUCCESS_NOTEBOOK_DIR keeps the analysis workspace independent of
REM the StudentSuccess source-code repository.
if not defined STUDENT_SUCCESS_NOTEBOOK_DIR (
    echo ERROR: STUDENT_SUCCESS_NOTEBOOK_DIR is not defined.
    echo.
    echo Set it to the directory containing your StudentSuccess notebooks.
    pause
    exit /b 1
)

REM Fail rather than creating a missing directory automatically. This prevents
REM a typo in the environment variable from silently creating and opening an
REM unintended notebook directory.
if not exist "%STUDENT_SUCCESS_NOTEBOOK_DIR%" (
    echo ERROR: Notebook directory not found:
    echo %STUDENT_SUCCESS_NOTEBOOK_DIR%
    pause
    exit /b 1
)


REM ---- Locate Conda ----------------------------------------------------------
REM Do not assume Conda is available on PATH. Search common per-user Anaconda
REM and Miniconda installation locations instead.
set "CONDA_ACTIVATE="

REM Anaconda installed under the user's local application-data directory.
if exist "%LOCALAPPDATA%\anaconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%LOCALAPPDATA%\anaconda3\Scripts\activate.bat"
)

REM Miniconda installed under the user's local application-data directory.
if not defined CONDA_ACTIVATE if exist "%LOCALAPPDATA%\miniconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%LOCALAPPDATA%\miniconda3\Scripts\activate.bat"
)

REM Anaconda installed directly under the user's profile directory.
if not defined CONDA_ACTIVATE if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%USERPROFILE%\anaconda3\Scripts\activate.bat"
)

REM Miniconda installed directly under the user's profile directory.
if not defined CONDA_ACTIVATE if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set "CONDA_ACTIVATE=%USERPROFILE%\miniconda3\Scripts\activate.bat"
)

REM Stop with a useful message if no supported Conda installation was found.
if not defined CONDA_ACTIVATE (
    echo ERROR: Could not locate an Anaconda or Miniconda installation.
    echo Checked common locations under LOCALAPPDATA and USERPROFILE.
    pause
    exit /b 1
)


REM ---- Activate StudentSuccess environment -----------------------------------
call "%CONDA_ACTIVATE%" "%ENV_NAME%"

if errorlevel 1 (
    echo ERROR: Could not activate Conda environment %ENV_NAME%.
    pause
    exit /b 1
)


REM ---- Launch JupyterLab -----------------------------------------------------
REM Start JupyterLab from the external analysis workspace rather than from the
REM source-code repository.
cd /d "%STUDENT_SUCCESS_NOTEBOOK_DIR%"
jupyter lab


REM Restore environment changes local to this batch script when Jupyter exits.
endlocal