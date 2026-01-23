@echo off
REM Chạy phiên bản GUI trực tiếp

echo =====================================================
echo   🖥️ CHATBOT KIỂM TRA NGÔN NGỮ - GUI VERSION
echo =====================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo Vui lòng cài Python từ: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Cài template nếu chưa có
if not exist "data\TEMPLATE_ENGLISH.xlsx" (
    echo 📝 Tạo file template Excel...
    python create_templates.py
    echo.
)

REM Chạy GUI
echo ▶️ Khởi động giao diện đồ họa...
echo.
python gui_main.py

if errorlevel 1 (
    echo.
    echo ❌ Lỗi khi chạy GUI!
    echo Nếu báo lỗi "tkinter", hãy:
    echo   • Windows: Cài lại Python (chọn tcl/tk)
    echo   • Linux: sudo apt-get install python3-tk
    echo   • Mac: Cài Python từ python.org
    pause
)
