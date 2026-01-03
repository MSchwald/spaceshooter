@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

if exist venv goto :start_game

python -c "import sys; exit(0 if sys.version_info[:2] >= (3,11) else 1)" >nul 2>nul
if errorlevel 1 (
    py -3.11 -c "import sys; exit(0)" >nul 2>nul
    if errorlevel 1 (
        goto :python_error
    )
    set "PYTHON_EXE=py -3.11"
) else (
    set "PYTHON_EXE=python"
)

echo Creating virtual environment...
%PYTHON_EXE% -m venv venv
if errorlevel 1 (
    echo ERROR: Could not create venv.
    pause
    exit /b
)

call venv\Scripts\activate

echo Installing requirements...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt

:start_game
call venv\Scripts\activate
python main.py
exit /b

:python_error
echo.
echo This game requires Python 3.11 or higher to run.
echo Please download it from:
echo https://www.python.org/downloads/windows
echo ("Windows installer 64-bit" for most systems)
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
exit /b