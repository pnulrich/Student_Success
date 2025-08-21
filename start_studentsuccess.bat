@echo off
REM === StudentSuccess Jupyter launcher (Windows) ===

REM ---- Settings (change if needed) ----
set ENV_NAME=student_success_dev
set NOTEBOOK_DIR=%~dp0jupyter_notebooks
REM If Miniconda/Anaconda is globally installed, adjust this path if different:
set CONDA_ACTIVATE="C:\ProgramData\miniconda3\Scripts\activate.bat"
REM If installed per-user, try: "%UserProfile%\miniconda3\Scripts\activate.bat"
REM -------------------------------------

REM Launch a new Command Prompt window:
start "StudentSuccess" cmd /K ^
  %CONDA_ACTIVATE% %ENV_NAME% ^&^& cd /d "%NOTEBOOK_DIR%" ^&^& jupyter lab
