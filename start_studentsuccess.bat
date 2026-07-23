@echo off
REM === StudentSuccess Jupyter launcher (Windows) ===

set ENV_NAME=student_success_dev
set PROJECT_ROOT=C:\Research\Research Projects\GSU\HHMI_IE3
set NOTEBOOK_DIR=%PROJECT_ROOT%\Analyses\jupyter_notebooks
set CONDA_ACTIVATE=C:\Users\pulrich\AppData\Local\anaconda3\Scripts\activate.bat

if not exist "%CONDA_ACTIVATE%" (
    echo ERROR: Conda activation script not found:
    echo %CONDA_ACTIVATE%
    pause
    exit /b 1
)

if not exist "%NOTEBOOK_DIR%" (
    echo ERROR: Notebook directory not found:
    echo %NOTEBOOK_DIR%
    pause
    exit /b 1
)

start "StudentSuccess" cmd /K call "%CONDA_ACTIVATE%" %ENV_NAME% ^&^& cd /d "%NOTEBOOK_DIR%" ^&^& jupyter lab