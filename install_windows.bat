@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

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
python -m pip install --upgrade pip --timeout 15 --quiet >nul 2>&1
python -m pip install -r requirements.txt

echo @echo off > start.bat
echo cd /d "%%~dp0" >> start.bat
echo call venv\Scripts\activate >> start.bat
echo python main.py >> start.bat
echo if %%errorlevel%% neq 0 pause >> start.bat


echo.
echo Installation complete. Open 'start.bat' to play!
echo Have fun and good luck beating the high scores!
echo.
pause
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