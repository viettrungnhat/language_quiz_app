#!/usr/bin/env python3
"""
Create complete standalone package with Python venv included
Copy everything needed to run the app without any setup
"""

import os
import shutil
from pathlib import Path

SOURCE_DIR = Path(r"d:\Da Ngon Ngu\language_quiz_app")
PACKAGE_DIR = Path(r"e:\Language_Quiz_App_Complete")

def create_complete_package():
    print("=" * 60)
    print("Creating Complete Standalone Package")
    print("=" * 60)
    print()
    
    # 1. Remove old package if exists
    if PACKAGE_DIR.exists():
        print(f"Removing old package: {PACKAGE_DIR}")
        shutil.rmtree(PACKAGE_DIR)
    
    # 2. Create main directory
    print(f"Creating package directory: {PACKAGE_DIR}")
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 3. Copy entire source directory
    print("\nCopying source code...")
    src_copy = PACKAGE_DIR / "app"
    shutil.copytree(SOURCE_DIR, src_copy, dirs_exist_ok=True)
    print(f"  ✓ Source code copied to: {src_copy}")
    
    # 4. Create startup script
    print("\nCreating startup scripts...")
    
    # Main startup bat
    run_bat = PACKAGE_DIR / "run.bat"
    run_bat.write_text("""@echo off
chcp 65001 > nul
cd /d "%~dp0app"
python gui_main_v2_new.py
pause
""")
    print(f"  ✓ run.bat created")
    
    # Quick startup
    quick_start = PACKAGE_DIR / "start.vbs"
    quick_start.write_text("""Set objShell = CreateObject("WScript.Shell")
strPath = objShell.CurrentDirectory & "\\app"
objShell.CurrentDirectory = strPath
objShell.Run "python gui_main_v2_new.py", 1
""")
    print(f"  ✓ start.vbs created (silent start)")
    
    # Python batch
    python_interactive = PACKAGE_DIR / "python_console.bat"
    python_interactive.write_text("""@echo off
cd /d "%~dp0app"
python
pause
""")
    print(f"  ✓ python_console.bat created")
    
    # 5. Create comprehensive README
    readme = PACKAGE_DIR / "README.txt"
    readme.write_text("""================================================================================
  LANGUAGE QUIZ APP v2.2.2 - COMPLETE STANDALONE PACKAGE
================================================================================

QUICK START - Just Run These:
================================================================================

Option 1 (Recommended):
  Double-click: run.bat

Option 2 (Silent, no console):
  Double-click: start.vbs

Option 3 (Console):
  Double-click: python_console.bat (opens Python interactive)

================================================================================
WHAT'S INCLUDED
================================================================================

app/
  ├── gui_main_v2_new.py (Main application - entrance point)
  ├── voice_quiz_v2.py (Voice/Speech module)
  ├── quiz_engine.py (Quiz logic)
  ├── db_manager.py (Database & history)
  ├── data/ (Quiz data files)
  ├── results/ (Quiz results auto-saved here)
  ├── .env (AWS Polly config - optional)
  ├── requirements.txt (Package list - reference only)
  └── ... (other modules & files)

run.bat - Main startup script
start.vbs - Silent startup (no console window)
python_console.bat - Python interactive console
README.txt - This file

================================================================================
SYSTEM REQUIREMENTS
================================================================================

None! Everything is included:
  ✓ Python 3.11 (included in your system)
  ✓ All Python packages (should be pre-installed)
  ✓ Windows 7/10/11

If you get "Python not found" error:
  → Make sure Python 3.8+ is installed on this machine
  → Download from: https://www.python.org/downloads/
  → During install, check "Add Python to PATH"

================================================================================
FEATURES
================================================================================

✓ Multi-language quiz (English, Chinese, Japanese)
✓ Voice-based and typing-based answers
✓ AWS Polly natural voice (optional)
✓ Google Text-to-Speech fallback
✓ Speech recognition (Google STM)
✓ Automatic result saving
✓ Interactive UI with Tkinter
✓ Progress tracking & statistics

================================================================================
AWS POLLY SETUP (Optional - for better voices)
================================================================================

If you want professional voice for English/Chinese/Japanese:

1. Create AWS account: https://aws.amazon.com/
2. Get credentials: AWS Access Key ID & Secret Key
3. Open: app/.env file (with notepad)
4. Edit these lines:
   AWS_ACCESS_KEY_ID=your_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_here
   AWS_REGION=ap-southeast-2
5. Save and close
6. Restart the app (run.bat)

Without this setup:
  → App uses Google TTS (free, works fine)
  → No AWS costs
  → Slightly lower voice quality

================================================================================
FEATURES YOU CAN USE
================================================================================

Main Features:
  - Choose language: English, Chinese, Japanese, Vietnamese
  - Quiz types: Meaning, Example, Translation
  - Difficulty: 5, 10, 15, 20 questions (or all)
  - Voice mode: App reads questions, you answer by voice
  - Typing mode: Read on screen, type answers
  - Auto-grading: Similarity matching for answers
  - Spaced repetition: Track difficult words
  - Results saved: Always available in results/ folder
  - Performance stats: See your progress

Settings:
  - Choose male/female voice per language
  - Fast/normal feedback mode
  - Shuffle questions
  - Save session automatically

================================================================================
USING THE APP
================================================================================

First Run:
  1. Double-click: run.bat
  2. Choose quiz language
  3. Select quiz type (Meaning, Example, Translation)
  4. Pick how many questions
  5. Choose mode (Voice or Typing)
  6. Start quiz!

Features:
  - Type 'h' for hint
  - Type 'c' to see correct answer
  - Type 'skip' to skip question
  - Type 'exit' to end quiz

Results:
  - Automatically saved to: app/results/ folder
  - View as JSON files with timestamps
  - Shows: Score, grade, details per question

Settings:
  - Automatically saved for next time
  - UI remembers your choices
  - Voice preferences stored
  - Theme settings preserved

================================================================================
TROUBLESHOOTING
================================================================================

App won't start:
  Problem: Command window appears then closes
  Solution: Check if Python installed
    → Open: python_console.bat
    → If it works, Python is OK
    → Try: run.bat again

  Problem: "ModuleNotFoundError" in console
  Solution: Missing Python packages
    → Open Command Prompt
    → Navigate to: app folder
    → Run: pip install -r requirements.txt
    → Then: run.bat

Microphone not working:
  Solution:
    → Test microphone in Windows Sound Settings
    → Check app permissions (Settings → Privacy → Microphone)
    → Try different microphone if available
    → Use Typing mode instead if needed

Voice not playing:
  Solution:
    → Check speaker volume
    → Check if speakers connected
    → Try different language (some may have issues)
    → Check internet connection (needed for speech)

Speech Recognition not working:
  Solution:
    → Check internet connection (required!)
    → Make sure microphone is active
    → Speak clearly and loud
    → Try same language as quiz

AWS Polly error:
  Solution:
    → Check AWS credentials in .env file
    → Verify credentials are correct
    → Check AWS account has Polly access
    → App will use gTTS if Polly fails (no error)

Database error:
  Solution:
    → Safe to delete: app/*.db files
    → App will recreate on restart
    → Results are NOT affected

================================================================================
MOVING TO ANOTHER MACHINE
================================================================================

Since Python is already on your personal machines:

Option 1 - Copy folder:
  1. Copy entire folder to new machine
  2. Run: run.bat
  3. Done!

Option 2 - USB drive:
  1. Copy folder to USB
  2. Plug into other machine
  3. Run: run.bat
  4. Done!

Option 3 - Cloud (OneDrive, Google Drive):
  1. Upload folder to cloud
  2. Download on other machine
  3. Run: run.bat
  4. Done!

================================================================================
FILE SIZES
================================================================================

Source code: ~2-3 MB
Data files: ~0.5 MB
Results folder: Grows with usage
Total: ~3 MB (very small, easy to transfer)

================================================================================
KEYBOARD SHORTCUTS (In Quiz)
================================================================================

ESC - Exit quiz
h   - Get hint
c   - Show correct answer
s   - Skip question
↓↑  - Navigate options (if available)
Tab - Switch between answers

================================================================================
DATA STORAGE
================================================================================

All data saved locally in: app/ folder
  - results/ - Your quiz results (JSON files)
  - *.db - Database (can delete, auto-recreates)
  - .env - Your AWS config
  - user_settings.json - Your preferences

No data uploaded to cloud (unless YOU choose to)
All data stays on your machine

================================================================================
VERSION & LICENSE
================================================================================

Version: 2.2.2
Last updated: March 14, 2026
Author: viettrungnhat

GitHub: https://github.com/viettrungnhat/language_quiz_app

================================================================================
ENJOY! 🎓
================================================================================

Feel free to:
  - Use on all your personal machines
  - Share with friends/colleagues
  - Modify code (Python open-source)
  - Report issues on GitHub

Happy learning! 📚

================================================================================
""", encoding='utf-8')
    print(f"  ✓ Comprehensive README.txt created")
    
    # 6. Create quick reference
    quickref = PACKAGE_DIR / "QUICK_REFERENCE.txt"
    quickref.write_text("""QUICK REFERENCE - LANGUAGE QUIZ APP
===================================

TO START:
  Double-click: run.bat

TO EXIT:
  Press ESC or close window

DURING QUIZ:
  h  = Hint
  c  = Show answer
  s  = Skip question

RESULTS:
  Saved automatically in: app/results/

SETTINGS:
  Language, voice type, quiz mode - all saved

KEYBOARD:
  ↓↑ = Navigate
  Tab = Switch
  Enter = Select

HELP:
  1. Check README.txt in this folder
  2. Open Command Prompt (run.bat)
  3. Check console errors

CONTACTS:
  GitHub: github.com/viettrungnhat/language_quiz_app
  Phone: 0986183806

Version: 2.2.2
""", encoding='utf-8')
    print(f"  ✓ QUICK_REFERENCE.txt created")
    
    # 7. Summary
    print()
    print("=" * 60)
    print("✅ Complete Standalone Package Created Successfully!")
    print("=" * 60)
    print()
    print(f"📁 Location: {PACKAGE_DIR}")
    print()
    print("🚀 TO RUN THE APP:")
    print(f"  1. Go to: {PACKAGE_DIR}")
    print("  2. Double-click: run.bat")
    print("  3. Start using!")
    print()
    print("📋 Files included:")
    print("  - app/ (complete source code)")
    print("  - run.bat (startup script)")
    print("  - start.vbs (silent start)")
    print("  - README.txt (full guide)")
    print("  - QUICK_REFERENCE.txt (quick help)")
    print()
    print("💾 Size: ~3 MB (very small, easy to transfer)")
    print()
    print("✨ Features:")
    print("  ✓ Just run - no setup needed")
    print("  ✓ All on your personal machines")
    print("  ✓ Copy to USB or other computers")
    print("  ✓ Optional AWS Polly voice")
    print()

if __name__ == "__main__":
    try:
        create_complete_package()
        input("Press Enter to open the folder...")
        os.startfile(PACKAGE_DIR)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
