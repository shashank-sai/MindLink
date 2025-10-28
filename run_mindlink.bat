@echo off
title MindLink Therapy Assistant

echo MindLink Therapy Assistant
echo ==========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
pip show ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install required packages
        echo Please check your internet connection and try again
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Starting MindLink Therapy Assistant...
echo.

REM Start the application
python main.py

echo.
echo MindLink session ended.
pause