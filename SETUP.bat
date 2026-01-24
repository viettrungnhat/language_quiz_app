@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo   🚀 Language Quiz App - Tự động cài đặt
echo ═══════════════════════════════════════════════════════════════
echo.

:: Kiểm tra Python đã cài chưa
echo [1/5] Kiểm tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python chưa được cài đặt!
    echo.
    echo 📥 Vui lòng tải Python tại: https://www.python.org/downloads/
    echo.
    echo ⚠️  LƯU Ý QUAN TRỌNG khi cài Python:
    echo    ✓ Tích chọn "Add Python to PATH"
    echo    ✓ Chọn phiên bản Python 3.10 hoặc mới hơn
    echo.
    pause
    exit /b 1
)

:: Hiển thị phiên bản Python
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Đã tìm thấy %PYTHON_VERSION%
echo.

:: Kiểm tra pip
echo [2/5] Kiểm tra pip...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip chưa sẵn sàng
    echo 📥 Đang cài đặt pip...
    python -m ensurepip --default-pip
)
echo ✅ pip đã sẵn sàng
echo.

:: Nâng cấp pip
echo [3/5] Nâng cấp pip lên phiên bản mới nhất...
python -m pip install --upgrade pip
echo.

:: Cài đặt thư viện từ requirements.txt
echo [4/5] Cài đặt các thư viện cần thiết...
echo 📦 Đang cài: openpyxl, gtts, SpeechRecognition, pygame, requests, opencv-python, python-dotenv...
echo.
python -m pip install -r requirements.txt

:: Cài thêm các thư viện cho Discord và Camera
echo.
echo [4.5/5] Cài đặt thư viện bổ sung (Discord, Camera)...
python -m pip install requests opencv-python python-dotenv

echo.
echo [5/5] Kiểm tra cài đặt...
python -c "import openpyxl; import gtts; import speech_recognition; import pygame; import requests; import cv2; print('✅ Tất cả thư viện đã sẵn sàng!')"

if %errorlevel% equ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ✅ CÀI ĐẶT THÀNH CÔNG!
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 📋 BƯỚC TIẾP THEO:
    echo    1. Mở file .env.example và đổi tên thành .env
    echo    2. Thêm Discord Webhook URL vào file .env (nếu cần)
    echo    3. Chạy file RUN_APP.bat để khởi động ứng dụng
    echo.
    echo 📖 Xem thêm: README.md và SETUP_GUIDE.md
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ⚠️  CÀI ĐẶT CHƯA HOÀN TOÀN
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 🔧 Một số thư viện có thể cần cài thủ công:
    echo.
    echo    • PyAudio (cho microphone):
    echo      pip install pyaudio
    echo      Hoặc tải wheel tại: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo.
    echo    • OpenCV (cho camera):
    echo      pip install opencv-python
    echo.
)

pause
