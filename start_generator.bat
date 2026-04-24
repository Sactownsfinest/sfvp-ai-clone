@echo off
title SFVP AI Script Generator
color 0F
echo.
echo  ================================================
echo   SACTOWN'S FINEST — AI Script Generator
echo  ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed or not in PATH.
    echo  Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Install requests if needed (only dependency)
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo  Installing required package: requests...
    pip install requests
    echo.
)

REM Run the generator
python "%~dp0personality\generator.py"

echo.
pause
