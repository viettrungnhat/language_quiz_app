@echo off
echo 🚀 Chatbot Kiem Tra Ngon Ngu
echo =====================================
echo.
echo 1. GUI Version (Recommended - Giao dien do hoa)
echo 2. Terminal Version (Tui lenh)
echo.
set /p choice="Chon: "
if "%choice%"=="1" (
    python gui_main.py
) else if "%choice%"=="2" (
    python main.py
) else (
    echo Lua chon khong hop le!
)
pause
