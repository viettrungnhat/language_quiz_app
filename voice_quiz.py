#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice-based Quiz Module
Hỗ trợ kiểm tra bằng giọng nói (Text-to-Speech & Speech-to-Text)
"""

import pyttsx3
import speech_recognition as sr
from threading import Thread
import json
from typing import Tuple, Optional
from difflib import SequenceMatcher


class VoiceManager:
    """Quản lý text-to-speech và speech-to-text"""
    
    def __init__(self):
        # Text-to-Speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Tốc độ nói (130-200)
        self.tts_engine.setProperty('volume', 0.9)  # Âm lượng (0-1)
        
        # Speech-to-Text
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Ngưỡng âm thanh
        
    def speak(self, text: str, language: str = "en") -> None:
        """
        Phát âm thanh từ văn bản
        language: "en" (English), "vi" (Vietnamese), "zh" (Chinese), "ja" (Japanese)
        """
        try:
            # Thiết lập ngôn ngữ
            voices = self.tts_engine.getProperty('voices')
            
            if language == "vi":
                # Vietnamese - thường không được hỗ trợ, dùng English làm thay thế
                self.tts_engine.setProperty('voice', voices[0].id)
            elif language == "zh":
                # Chinese - tìm voice Trung Quốc
                for voice in voices:
                    if 'Chinese' in voice.name or 'Mandarin' in voice.name:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            elif language == "ja":
                # Japanese - tìm voice Nhật Bản
                for voice in voices:
                    if 'Japanese' in voice.name:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            else:  # English
                for voice in voices:
                    if 'English' in voice.name:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"Lỗi text-to-speech: {e}")
    
    def listen_to_microphone(self, timeout: int = 10) -> Optional[str]:
        """
        Lắng nghe từ microphone và chuyển thành text
        timeout: thời gian chờ (giây)
        Returns: text hoặc None nếu lỗi
        """
        try:
            with sr.Microphone() as source:
                # Điều chỉnh cho tiếng nền
                print("🎤 Đang lắng nghe... Hãy nói câu trả lời của bạn")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Ghi âm
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                
                # Nhận dạng bằng Google Speech Recognition (miễn phí)
                print("🔄 Đang xử lý giọng nói...")
                text = self.recognizer.recognize_google(audio, language='en-US')
                return text.strip()
        
        except sr.RequestError as e:
            print(f"❌ Lỗi kết nối: {e}")
            return None
        except sr.UnknownValueError:
            print("❌ Không thể nhận dạng giọng nói")
            return None
        except sr.Timeout:
            print("❌ Hết thời gian (không nói gì)")
            return None
        except Exception as e:
            print(f"❌ Lỗi microphone: {e}")
            return None
    
    def listen_to_microphone_vietnamese(self, timeout: int = 10) -> Optional[str]:
        """
        Lắng nghe và nhận dạng tiếng Việt
        """
        try:
            with sr.Microphone() as source:
                print("🎤 Đang lắng nghe tiếng Việt...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                
                print("🔄 Đang xử lý...")
                # Google hỗ trợ tiếng Việt
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                return text.strip()
        
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None


class VoiceQuizManager:
    """Quản lý toàn bộ voice quiz"""
    
    def __init__(self):
        self.voice_manager = VoiceManager()
        self.results = []
    
    def ask_question_voice(self, question_text: str, language: str = "en") -> Optional[str]:
        """
        Hỏi câu hỏi bằng giọng nói và lắng nghe trả lời
        """
        # 1. Phát câu hỏi
        print(f"\n❓ Câu hỏi: {question_text}")
        self.voice_manager.speak(question_text, language=language)
        
        # 2. Lắng nghe trả lời
        if language == "vi":
            answer = self.voice_manager.listen_to_microphone_vietnamese(timeout=10)
        else:
            answer = self.voice_manager.listen_to_microphone(timeout=10)
        
        return answer
    
    def compare_answers(self, user_answer: str, correct_answer: str) -> Tuple[bool, float, str]:
        """
        So sánh câu trả lời của người dùng với câu trả lời đúng
        Returns: (is_correct, similarity_score, feedback)
        """
        user_clean = user_answer.lower().strip()
        correct_clean = correct_answer.lower().strip()
        
        # Kiểm tra từng từ
        user_words = set(user_clean.split())
        correct_words = set(correct_clean.split())
        
        # Tính độ tương đồng
        matcher = SequenceMatcher(None, user_clean, correct_clean)
        similarity = matcher.ratio()
        
        # Kiểm tra từng từ khớp
        if user_clean == correct_clean:
            return True, 1.0, "✅ Chính xác 100%!"
        
        elif similarity >= 0.8:
            common_words = len(user_words & correct_words)
            total_words = len(correct_words)
            if common_words / total_words >= 0.7:
                return True, similarity, f"✅ Tốt! Độ chính xác: {similarity*100:.0f}%"
        
        # Sai
        return False, similarity, f"❌ Sai. Trả lời đúng là: {correct_answer}"


# Test
if __name__ == "__main__":
    print("🧪 Test Voice Manager...")
    
    manager = VoiceQuizManager()
    
    # Test TTS
    print("\n🔊 Test text-to-speech...")
    manager.voice_manager.speak("Hello, how are you today?", language="en")
    
    # Test STT
    print("\n🎤 Test speech-to-text...")
    # answer = manager.voice_manager.listen_to_microphone(timeout=5)
    # if answer:
    #     print(f"Bạn nói: {answer}")
