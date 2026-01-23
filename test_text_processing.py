#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Text Processing Features - Language Quiz v2.2.3
Kiểm tra tính năng xử lý văn bản và nhận dạng ngôn ngữ
"""

from voice_quiz_v3 import VoiceManagerV3

def test_lam_sach_van_ban():
    """Test làm sạch văn bản"""
    print("=" * 60)
    print("TEST 1: LÀM SẠCH VĂN BẢN")
    print("=" * 60)
    
    test_cases = [
        ("• Beautiful day!", "Beautiful day!"),
        ("5 + 3 = 8", "5 cộng 3 bằng 8"),
        ("10 * 2 - 5", "10 nhân 2 trừ 5"),
        ("**Hello** _world_", "Hello world"),
        ("好きです。", "好きです."),
        ("    Multiple   spaces   ", "Multiple spaces"),
        ("➤ Đây là bullet point", "Đây là bullet point"),
        ("", ""),
    ]
    
    voice_manager = VoiceManagerV3()
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = voice_manager.lam_sach_van_ban(input_text)
        status = "✅" if result == expected else "❌"
        print(f"\nTest {i} {status}")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")


def test_doan_ngon_ngu():
    """Test nhận dạng ngôn ngữ"""
    print("\n" + "=" * 60)
    print("TEST 2: NHẬN DẠNG NGÔN NGỮ")
    print("=" * 60)
    
    test_cases = [
        ("こんにちは", "ja"),          # Japanese
        ("你好世界", "zh"),             # Chinese
        ("안녕하세요", "ko"),           # Korean
        ("Xin chào Việt Nam", "vi"),   # Vietnamese
        ("Hello world", "en"),          # English
        ("Đây là một câu tiếng Việt có dấu", "vi"),
        ("私は学生です", "ja"),         # Japanese
        ("我爱你", "zh"),               # Chinese
    ]
    
    voice_manager = VoiceManagerV3()
    
    for i, (text, expected_lang) in enumerate(test_cases, 1):
        detected = voice_manager.doan_ngon_ngu_theo_ky_tu(text)
        status = "✅" if detected == expected_lang else "⚠️"
        print(f"\nTest {i} {status}")
        print(f"  Text:     '{text}'")
        print(f"  Expected: {expected_lang}")
        print(f"  Detected: {detected}")


def test_speak_with_auto_clean():
    """Test TTS với auto-clean"""
    print("\n" + "=" * 60)
    print("TEST 3: TTS VỚI AUTO-CLEAN")
    print("=" * 60)
    
    voice_manager = VoiceManagerV3()
    
    test_texts = [
        ("• Hello, how are you?", "en"),
        ("**Xin chào** Việt Nam!", "vi"),
        ("5 + 3 = 8", "vi"),
        ("こんにちは、元気ですか？", "ja"),
    ]
    
    for i, (text, lang) in enumerate(test_texts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Original: {text}")
        cleaned = voice_manager.lam_sach_van_ban(text)
        print(f"Cleaned:  {cleaned}")
        print(f"Language: {lang}")
        
        # Uncomment để test thật (cần AWS Polly credentials và audio output)
        # voice_manager.speak(text, language=lang, auto_clean=True)


def test_auto_detect_language():
    """Test auto-detect ngôn ngữ khi đọc"""
    print("\n" + "=" * 60)
    print("TEST 4: AUTO-DETECT NGÔN NGỮ")
    print("=" * 60)
    
    voice_manager = VoiceManagerV3()
    
    test_texts = [
        "Hello world",
        "こんにちは",
        "你好",
        "Xin chào",
        "안녕하세요",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- Test {i} ---")
        detected = voice_manager.doan_ngon_ngu_theo_ky_tu(text)
        print(f"Text:     {text}")
        print(f"Detected: {detected}")
        
        # Uncomment để test TTS với auto-detect
        # voice_manager.speak(text, language="auto", auto_clean=True)


def test_multilingual_text():
    """Test đọc văn bản đa ngôn ngữ"""
    print("\n" + "=" * 60)
    print("TEST 5: ĐỌC ĐA NGÔN NGỮ")
    print("=" * 60)
    
    voice_manager = VoiceManagerV3()
    
    multilingual_text = """
Hello, how are you?
こんにちは、元気ですか？
你好，你好吗？
Xin chào, bạn khỏe không?
"""
    
    print("Text đa ngôn ngữ:")
    print(multilingual_text)
    print("\nPhân tích từng dòng:")
    
    for line in multilingual_text.strip().split('\n'):
        if line.strip():
            detected = voice_manager.doan_ngon_ngu_theo_ky_tu(line)
            print(f"  '{line}' → {detected}")
    
    # Uncomment để test đọc thật
    # print("\n🔊 Đọc văn bản đa ngôn ngữ...")
    # voice_manager.speak_multilingual(multilingual_text)


def test_edge_cases():
    """Test các trường hợp biên"""
    print("\n" + "=" * 60)
    print("TEST 6: EDGE CASES")
    print("=" * 60)
    
    voice_manager = VoiceManagerV3()
    
    edge_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("•••", "Bullets only"),
        ("***", "Markdown only"),
        ("123", "Numbers only"),
        ("!@#$%", "Special chars only"),
        ("Hello\nWorld", "Multiple lines"),
        ("EnglishとJapanese混合", "Mixed languages"),
    ]
    
    print("\nTest làm sạch văn bản:")
    for text, description in edge_cases:
        result = voice_manager.lam_sach_van_ban(text)
        print(f"\n{description}:")
        print(f"  Input:  '{text}'")
        print(f"  Output: '{result}'")
        print(f"  Empty:  {result == ''}")


def main():
    """Chạy tất cả tests"""
    print("\n" + "🎓" * 30)
    print("LANGUAGE QUIZ v2.2.3 - TEXT PROCESSING TEST SUITE")
    print("🎓" * 30)
    
    try:
        test_lam_sach_van_ban()
        test_doan_ngon_ngu()
        test_speak_with_auto_clean()
        test_auto_detect_language()
        test_multilingual_text()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nNote: TTS tests chỉ hiển thị output, không phát âm thật.")
        print("Uncomment các dòng 'voice_manager.speak()' để test âm thanh thật.")
        print("\nRequirements:")
        print("  - AWS Polly credentials (đã config)")
        print("  - Audio output device")
        print("  - pygame installed")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
