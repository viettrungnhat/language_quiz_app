@echo off
chcp 65001 >nul
title Language Quiz App - Multi-Language Voice Quiz

echo ═══════════════════════════════════════════════════════════════
echo   🎓 Language Quiz App v2.2
echo ═══════════════════════════════════════════════════════════════
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python chưa được cài đặt!
    echo 📥 Vui lòng chạy SETUP.bat trước
    pause
    exit /b 1
)

echo ▶️  Đang khởi động ứng dụng...
echo.

:: Chạy ứng dụng
python gui_main_v2_new.py

:: Nếu có lỗi
if %errorlevel% neq 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════════
    echo   ❌ LỖI KHI CHẠY ỨNG DỤNG
    echo ═══════════════════════════════════════════════════════════════
    echo.
    echo 💡 Giải pháp:
    echo    1. Chạy lại SETUP.bat để cài đặt đầy đủ thư viện
    echo    2. Kiểm tra file .env đã được cấu hình đúng
    echo    3. Xem file README.md để biết thêm chi tiết
    echo.
)

pause
