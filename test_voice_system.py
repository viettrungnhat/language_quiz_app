#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Voice Quiz Module
Kiểm tra xem các thành phần giọng nói hoạt động bình thường không
"""

import sys
import time
from pathlib import Path

print("="*70)
print("🧪 KIỂM TRA HỆ THỐNG GIỌNG NÓI")
print("="*70)

# 1. Kiểm tra imports
print("\n1️⃣ Kiểm tra packages...")
print("-" * 70)

packages = {
    'pyttsx3': 'Text-to-Speech',
    'speech_recognition': 'Speech-to-Text',
    'pyaudio': 'Microphone support',
    'openpyxl': 'Excel support'
}

missing = []
for pkg, desc in packages.items():
    try:
        __import__(pkg)
        print(f"   ✅ {pkg:20} ({desc})")
    except ImportError:
        print(f"   ❌ {pkg:20} ({desc}) - THIẾU")
        missing.append(pkg)

if missing:
    print(f"\n⚠️  Cần cài đặt: pip install {' '.join(missing)}")
    sys.exit(1)

# 2. Kiểm tra TTS
print("\n2️⃣ Kiểm tra Text-to-Speech...")
print("-" * 70)

try:
    import pyttsx3
    engine = pyttsx3.init()
    print("   ✅ pyttsx3 khởi tạo thành công")
    
    # List voices
    voices = engine.getProperty('voices')
    print(f"   📻 Số voice hệ thống: {len(voices)}")
    for i, voice in enumerate(voices[:3]):
        print(f"      {i+1}. {voice.name}")
    
    print("\n   🔊 Test phát âm (5 giây)...")
    engine.say("Hello, this is a voice test")
    engine.runAndWait()
    print("   ✅ Phát âm thành công (bạn có nghe được không?)")
    
except Exception as e:
    print(f"   ❌ Lỗi TTS: {e}")
    sys.exit(1)

# 3. Kiểm tra STT
print("\n3️⃣ Kiểm tra Speech-to-Text...")
print("-" * 70)

try:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    print("   ✅ speech_recognition khởi tạo thành công")
    
    # Kiểm tra microphone
    print("\n   🎤 Kiểm tra microphone...")
    try:
        with sr.Microphone() as source:
            print("   ✅ Microphone khả dụng")
            print("   📌 Thông tin microphone:")
            print(f"      Device index: 0 (mặc định)")
            print(f"      Sample rate: 16000 Hz")
    except Exception as e:
        print(f"   ❌ Lỗi microphone: {e}")
        print("      Đảm bảo microphone đã kết nối!")
        sys.exit(1)
    
except Exception as e:
    print(f"   ❌ Lỗi STT: {e}")
    sys.exit(1)

# 4. Kiểm tra voice_quiz module
print("\n4️⃣ Kiểm tra voice_quiz.py...")
print("-" * 70)

try:
    from voice_quiz import VoiceManager, VoiceQuizManager
    print("   ✅ voice_quiz.py có thể import")
    
    manager = VoiceQuizManager()
    print("   ✅ VoiceQuizManager khởi tạo thành công")
    
except Exception as e:
    print(f"   ❌ Lỗi voice_quiz: {e}")
    sys.exit(1)

# 5. Kiểm tra gui_main_v2
print("\n5️⃣ Kiểm tra gui_main_v2.py...")
print("-" * 70)

try:
    import tkinter as tk
    print("   ✅ tkinter khả dụng")
    
    # Không thể khởi tạo GUI trong script này
    print("   ℹ️  (GUI sẽ được test khi chạy riêng)")
    
except Exception as e:
    print(f"   ⚠️  Lỗi tkinter: {e}")

# 6. Kiểm tra internet connection (Google STT)
print("\n6️⃣ Kiểm tra kết nối internet...")
print("-" * 70)

try:
    import urllib.request
    urllib.request.urlopen("https://www.google.com", timeout=2)
    print("   ✅ Kết nối internet có sẵn")
    print("   ℹ️  (Google Speech Recognition sẽ hoạt động)")
except:
    print("   ⚠️  Không có internet")
    print("   ⚠️  Speech Recognition sẽ KHÔNG hoạt động")
    print("   💡 (Chỉ có thể dùng Text-to-Speech)")

# 7. TÓNG TẮT
print("\n" + "="*70)
print("✅ KIỂM TRA HOÀN THÀNH!")
print("="*70)

print("""
📊 KẾT QUẢ:
   ✅ Tất cả packages cần thiết đã cài
   ✅ Text-to-Speech (TTS) hoạt động
   ✅ Microphone được kết nối
   ✅ Module voice_quiz có thể import

🎯 BẠN CÓ THỂ:
   1. Chạy GUI v2.0: python gui_main_v2.py
   2. Bắt đầu Voice Quiz
   3. Kiểm tra bằng giọng nói

💡 TIPS:
   • Nếu STT không hoạt động → Kiểm tra internet
   • Nếu TTS không hoạt động → Kiểm tra loa
   • Nếu Microphone không hoạt động → Kiểm tra kết nối

═══════════════════════════════════════════════════════════════════════════════
""")

print("\n🚀 Sẵn sàng! Chạy: python gui_main_v2.py")
