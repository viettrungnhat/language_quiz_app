@echo off
REM =========================================
REM GUI v2.1 - Voice Quiz v2 Launcher
REM Google TTS + Speech Recognition
REM =========================================

echo.
echo 🎤 GUI v2.1 - Voice Quiz v2 (Google TTS)
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 📦 Checking packages...

python -c "import gtts" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  gtts not installed. Installing...
    pip install gtts
)

python -c "import speech_recognition" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  SpeechRecognition not installed. Installing...
    pip install SpeechRecognition
)

python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  openpyxl not installed. Installing...
    pip install openpyxl
)

REM Create templates if not exist
if not exist "TEMPLATE_ENGLISH.xlsx" (
    echo 📄 Creating Excel templates...
    python create_templates.py
)

echo.
echo 🚀 Launching GUI v2.1 (Google TTS Voice Quiz)...
echo.

python gui_main_v2.py

pause
