@echo off
REM Script tạo bản portable của Language Quiz App

setlocal enabledelayedexpansion

set SOURCE_DIR=d:\Da Ngon Ngu\language_quiz_app
set PORTABLE_DIR=d:\Language_Quiz_App_Portable

echo =========================================
echo Creating Portable Package
echo =========================================
echo.

REM 1. Tạo thư mục portable
if exist "%PORTABLE_DIR%" (
    echo Removing old portable folder...
    rmdir /s /q "%PORTABLE_DIR%"
)

echo Creating portable directory...
mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\data"
mkdir "%PORTABLE_DIR%\results"

REM 2. Copy source Python files
echo Copying Python source files...
copy "%SOURCE_DIR%\*.py" "%PORTABLE_DIR%\" /y >nul
copy "%SOURCE_DIR%\*.ico" "%PORTABLE_DIR%\" /y >nul
copy "%SOURCE_DIR%\*.txt" "%PORTABLE_DIR%\" /y >nul
copy "%SOURCE_DIR%\*.md" "%PORTABLE_DIR%\" /y >nul
copy "%SOURCE_DIR%\.env" "%PORTABLE_DIR%\" /y >nul
copy "%SOURCE_DIR%\.env.example" "%PORTABLE_DIR%\" /y >nul
copy "%SOURCE_DIR%\.gitignore" "%PORTABLE_DIR%\" /y >nul
copy "%SOURCE_DIR%\requirements.txt" "%PORTABLE_DIR%\" /y >nul

REM 3. Copy data files
echo Copying data files...
if exist "%SOURCE_DIR%\data\" (
    xcopy "%SOURCE_DIR%\data\*" "%PORTABLE_DIR%\data\" /e /y >nul
)

REM 4. Copy sample JSONs
if exist "%SOURCE_DIR%\*.json" (
    copy "%SOURCE_DIR%\*.json" "%PORTABLE_DIR%\" /y >nul
)

REM 5. Create startup script
echo Creating startup script...
(
    echo @echo off
    echo cd %%~dp0
    echo python gui_main_v2_new.py
    echo pause
) > "%PORTABLE_DIR%\run_app.bat"

REM 6. Create README for portable
echo Creating README...
(
    echo # Language Quiz App - Portable Version
    echo.
    echo ## How to Run
    echo.
    echo 1. Make sure Python 3.8+ is installed on your system
    echo 2. Run: run_app.bat
    echo.
    echo ## Setup .env file
    echo.
    echo Copy .env.example to .env and add your AWS credentials:
    echo - AWS_ACCESS_KEY_ID
    echo - AWS_SECRET_ACCESS_KEY
    echo - AWS_REGION
    echo.
    echo ## First Time Setup
    echo.
    echo Run in Command Prompt:
    echo   pip install -r requirements.txt
    echo.
    echo Then run:
    echo   run_app.bat
) > "%PORTABLE_DIR%\README_PORTABLE.txt"

REM 7. Create Python requirements.txt
echo Creating requirements file...
copy "%SOURCE_DIR%\requirements.txt" "%PORTABLE_DIR%\" /y >nul

echo.
echo =========================================
echo Portable package created successfully!
echo =========================================
echo.
echo Location: %PORTABLE_DIR%
echo.
echo Next steps:
echo 1. Copy this folder to another machine
echo 2. Install Python 3.8+ on target machine
echo 3. Run: pip install -r requirements.txt
echo 4. Create .env file with AWS credentials
echo 5. Run: run_app.bat
echo.
pause
