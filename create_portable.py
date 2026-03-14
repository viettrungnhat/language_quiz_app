#!/usr/bin/env python3
"""
Create portable version of Language Quiz App
Copy all necessary files to a new directory for distribution
"""

import os
import shutil
from pathlib import Path

SOURCE_DIR = Path(r"d:\Da Ngon Ngu\language_quiz_app")
PORTABLE_DIR = Path(r"d:\Language_Quiz_App_Portable")

def create_portable():
    print("=" * 50)
    print("Creating Portable Package")
    print("=" * 50)
    print()
    
    # 1. Remove old portable if exists
    if PORTABLE_DIR.exists():
        print(f"Removing old portable folder: {PORTABLE_DIR}")
        shutil.rmtree(PORTABLE_DIR)
    
    # 2. Create portable directory structure
    print("Creating directory structure...")
    PORTABLE_DIR.mkdir(parents=True, exist_ok=True)
    (PORTABLE_DIR / "data").mkdir(exist_ok=True)
    (PORTABLE_DIR / "results").mkdir(exist_ok=True)
    
    # 3. Copy Python files
    print("Copying Python source files...")
    py_files = [
        "gui_main_v2_new.py",
        "gui_main_v2.py",
        "gui_main.py",
        "main.py",
        "voice_quiz.py",
        "voice_quiz_v2.py",
        "quiz_engine.py",
        "scorer.py",
        "data_loader.py",
        "db_manager.py",
        "excel_to_json.py",
        "aws_config.py",
    ]
    
    for py_file in py_files:
        src = SOURCE_DIR / py_file
        if src.exists():
            shutil.copy(src, PORTABLE_DIR / py_file)
            print(f"  ✓ {py_file}")
    
    # 4. Copy config and data files
    print("\nCopying configuration files...")
    config_files = [
        ".env",
        ".env.example",
        ".gitignore",
        "requirements.txt",
        "config.json",
        "user_settings.json",
        "logo.ico",
    ]
    
    for cfg_file in config_files:
        src = SOURCE_DIR / cfg_file
        if src.exists():
            shutil.copy(src, PORTABLE_DIR / cfg_file)
            print(f"  ✓ {cfg_file}")
    
    # 5. Copy documentation
    print("\nCopying documentation...")
    doc_files = [
        "README.md",
        "QUICK_START.txt",
        "QUICK_REFERENCE_v2.2.2.md",
        "VOICE_QUICK_START.txt",
    ]
    
    for doc_file in doc_files:
        src = SOURCE_DIR / doc_file
        if src.exists():
            shutil.copy(src, PORTABLE_DIR / doc_file)
            print(f"  ✓ {doc_file}")
    
    # 6. Copy data folder
    print("\nCopying data files...")
    data_src = SOURCE_DIR / "data"
    if data_src.exists():
        for file in data_src.glob("*.json"):
            shutil.copy(file, PORTABLE_DIR / "data" / file.name)
            print(f"  ✓ data/{file.name}")
    
    # 7. Create startup script
    print("\nCreating startup script...")
    run_script = PORTABLE_DIR / "run_app.bat"
    run_script.write_text("""@echo off
cd /d "%~dp0"
python gui_main_v2_new.py
pause
""")
    print(f"  ✓ run_app.bat")
    
    # 8. Create setup script
    setup_script = PORTABLE_DIR / "setup.bat"
    setup_script.write_text("""@echo off
echo Installing required Python packages...
echo.
pip install -r requirements.txt
echo.
echo Installation complete!
echo You can now run: run_app.bat
pause
""")
    print(f"  ✓ setup.bat")
    
    # 9. Create portable README
    readme = PORTABLE_DIR / "README_PORTABLE.txt"
    readme.write_text("""Language Quiz App - Portable Version
Ung dung kiem tra ngon ngu da nen tang

REQUIREMENTS
============
- Python 3.8 or higher (installed on target machine)

QUICK START
===========

1. FIRST TIME SETUP (one-time only):
   - Open Command Prompt in this folder
   - Run: setup.bat
   - This installs all required Python packages

2. AFTER SETUP:
   - Double-click: run_app.bat
   OR
   - Open Command Prompt and run: python gui_main_v2_new.py

AWS POLLY CONFIGURATION (Optional)
==================================

For English/Chinese/Japanese voice (using AWS Polly):

1. Edit .env file in this folder
2. Add your AWS credentials:
   AWS_ACCESS_KEY_ID=your_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_here
   AWS_REGION=ap-southeast-2

3. Save and restart the app

FOLDER STRUCTURE
================

Language_Quiz_App_Portable/
├── gui_main_v2_new.py (Main app)
├── voice_quiz_v2.py (Voice module)
├── quiz_engine.py (Quiz logic)
├── run_app.bat (Quick start)
├── setup.bat (First time setup)
├── requirements.txt (Python packages)
├── .env.example (AWS config template)
├── data/ (Quiz data files)
└── results/ (Quiz results)

TROUBLESHOOTING
===============

Error: "Python is not installed"
→ Download and install Python from: https://www.python.org
→ Make sure to check "Add to PATH" during installation

Error: "ModuleNotFoundError"
→ Run: setup.bat again
→ This installs all required packages

Error: "Connection timeout"
→ Check your internet connection
→ App needs internet for Google Speech Recognition

Error: "Microphone not working"
→ Check microphone permissions on your computer
→ Test microphone in System Settings

TIPS
====

- Quiz data files are in: data/ folder
- Quiz results are saved in: results/ folder
- Your settings are saved automatically
- .env file is YOUR PERSONAL config (don't share!)

GITHUB
======

Source code: https://github.com/viettrungnhat/language_quiz_app

Version: 2.2.2
Last updated: 2026-03-14
""", encoding='utf-8')
    print(f"  ✓ README_PORTABLE.txt")
    
    # 10. Summary
    print()
    print("=" * 50)
    print("✅ Portable package created successfully!")
    print("=" * 50)
    print()
    print(f"📁 Location: {PORTABLE_DIR}")
    print()
    print("📋 Next Steps:")
    print("  1. Copy folder to another machine")
    print("  2. Run: setup.bat (first time only)")
    print("  3. Run: run_app.bat")
    print()
    print("If AWS Polly needed:")
    print("  - Edit: .env file")
    print("  - Add AWS credentials")
    print("  - Restart app")
    print()

if __name__ == "__main__":
    try:
        create_portable()
        input("Press Enter to exit...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Press Enter to exit...")
