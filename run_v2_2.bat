@echo off
REM Language Quiz v2.2 - Enhanced Voice
REM Chương trình kiểm tra ngôn ngữ với Voice Quiz cải tiến

setlocal enabledelayedexpansion

echo.
echo ================================
echo  Language Quiz v2.2 - Voice
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+
    pause
    exit /b 1
)

REM Install dependencies
echo 1. Installing dependencies...
pip install -r requirements_v2.2.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run GUI
echo.
echo 2. Starting Language Quiz v2.2...
echo.

python gui_main_v2_new.py

pause
