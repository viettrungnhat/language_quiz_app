#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice Quiz Module v2.0 - Improved with Google TTS + AWS Polly + Whisper
Sử dụng Google Text-to-Speech (Online) + AWS Polly (cho Anh/Trung/Nhật) + Whisper (OpenAI)
"""

import os
import io
import tempfile
from pathlib import Path
from typing import Tuple, Optional
from difflib import SequenceMatcher
import threading
from dotenv import load_dotenv

# Load environment variables từ .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import openai
except ImportError:
    openai = None

try:
    import pygame
except ImportError:
    pygame = None

try:
    import boto3
except ImportError:
    boto3 = None


class VoiceManager:
    """Quản lý text-to-speech và speech-to-text (v2.0) - gTTS + AWS Polly"""
    
    def __init__(self):
        # Google TTS
        self.gtts_available = gTTS is not None
        
        # AWS Polly
        self.polly_available = boto3 is not None
        self.polly_client = None
        if self.polly_available:
            try:
                aws_key = os.getenv("AWS_ACCESS_KEY_ID")
                aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
                aws_region = os.getenv("AWS_REGION", "ap-southeast-2")
                
                if aws_key and aws_secret:
                    self.polly_client = boto3.client(
                        'polly',
                        region_name=aws_region,
                        aws_access_key_id=aws_key,
                        aws_secret_access_key=aws_secret
                    )
                    print("✅ AWS Polly initialized successfully")
                else:
                    print("⚠️ AWS credentials not found in .env - Polly disabled")
                    self.polly_available = False
            except Exception as e:
                print(f"⚠️ AWS Polly init error: {e}")
                self.polly_available = False
        
        # Speech Recognition
        self.recognizer = sr.Recognizer() if sr else None
        if self.recognizer:
            # Giảm energy_threshold để nhạy hơn (mặc định 300, tăng = kém nhạy hơn)
            self.recognizer.energy_threshold = 1000  # Giảm từ 4000 xuống 1000
            self.recognizer.dynamic_energy_threshold = True  # Auto-adjust
        
        # Pygame cho audio playback
        self.pygame_available = pygame is not None
        if self.pygame_available:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"⚠️ Pygame init error: {e}")
                self.pygame_available = False
    
    def speak_google_tts(self, text: str, language: str = "en") -> bool:
        """
        Phát âm thanh từ văn bản dùng Google TTS (Online)
        language: "en" (English), "vi" (Vietnamese), "zh-cn" (Chinese), "ja" (Japanese)
        Returns: True nếu thành công
        """
        if not self.gtts_available:
            print("❌ gTTS not installed. Run: pip install gtts")
            return False
        
        try:
            # Language mapping
            lang_map = {
                "en": "en",
                "vi": "vi",
                "chinese": "zh-cn",
                "zh": "zh-cn",
                "japanese": "ja",
                "ja": "ja"
            }
            
            gtts_lang = lang_map.get(language.lower(), "en")
            
            # Tạo TTS
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Lưu vào bytes
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # Phát âm bằng pygame hoặc lưu file
            if self.pygame_available:
                self._play_audio_pygame(audio_fp)
            else:
                # Fallback: lưu file tạm
                temp_file = "/tmp/tts_temp.mp3"
                tts.save(temp_file)
                self._play_audio_file(temp_file)
            
            return True
        except Exception as e:
            print(f"❌ Google TTS error: {e}")
            return False
    
    def speak_with_polly(self, text: str, language: str = "en", voice: str = None) -> bool:
        """
        Phát âm thanh từ văn bản dùng AWS Polly
        language: "en", "zh", "ja"
        voice: Tên giọng (nếu None sẽ dùng default)
        Returns: True nếu thành công
        """
        if not self.polly_available or not self.polly_client:
            print("❌ AWS Polly not available. Fallback to gTTS...")
            return self.speak_google_tts(text, language)
        
        try:
            # Voice mapping
            voice_map = {
                "en": "Joanna",       # Female English
                "zh": "Zhiyu",        # Male Mandarin
                "ja": "Mizuki"        # Female Japanese
            }
            
            polly_lang = language.lower()
            polly_voice = voice or voice_map.get(polly_lang, "Joanna")
            
            # Gọi AWS Polly
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=polly_voice,
                Engine='neural'  # Neural engine cho chất lượng tốt hơn
            )
            
            # Phát audio
            audio_stream = response['AudioStream'].read()
            audio_fp = io.BytesIO(audio_stream)
            
            if self.pygame_available:
                self._play_audio_pygame(audio_fp)
            else:
                # Lưu file tạm
                temp_file = Path(tempfile.gettempdir()) / "polly_temp.mp3"
                with open(temp_file, 'wb') as f:
                    f.write(audio_stream)
                self._play_audio_file(str(temp_file))
            
            return True
        except Exception as e:
            print(f"❌ AWS Polly error: {e}. Fallback to gTTS...")
            return self.speak_google_tts(text, language)
    
    def _play_audio_pygame(self, audio_fp):
        """Phát audio bằng pygame"""
        try:
            pygame.mixer.music.load(audio_fp)
            pygame.mixer.music.play()
            
            # Chờ phát xong
            while pygame.mixer.music.get_busy():
                pass
        except Exception as e:
            print(f"Pygame playback error: {e}")
    
    def _play_audio_file(self, filepath):
        """Phát audio từ file"""
        try:
            if os.path.exists(filepath):
                os.system(f'start {filepath}')  # Windows
        except Exception as e:
            print(f"Audio file error: {e}")
    
    def listen_to_microphone(self, timeout: int = 10, language: str = "en-US") -> Optional[str]:
        """
        Lắng nghe từ microphone và chuyển thành text
        Dùng Google Speech Recognition hoặc Whisper
        Returns: text hoặc None nếu lỗi
        """
        if not sr:
            print("❌ speech_recognition not installed")
            return None
        
        try:
            with sr.Microphone() as source:
                print("🎤 Đang lắng nghe... Hãy nói câu trả lời của bạn")
                print(f"⚙️ Energy threshold: {self.recognizer.energy_threshold}")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Ghi âm
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
                
                # Nhận dạng
                print("🔄 Đang xử lý giọng nói...")
                
                try:
                    # Thử dùng Google Speech Recognition
                    text = self.recognizer.recognize_google(audio, language=language)
                    print(f"✅ Nhận dạng: {text}")
                    return text.strip()
                except sr.UnknownValueError:
                    print(f"❌ Không thể nhận dạng: Không nghe được giọng nói rõ ràng")
                    return None
                except sr.RequestError:
                    print("⚠️ Lỗi kết nối. Kiểm tra internet connection.")
                    return None
        
        except sr.Timeout:
            print("❌ Hết thời gian. Hãy nói câu trả lời.")
            return None
        except Exception as e:
            print(f"❌ Lỗi microphone: {str(e)}")
            return None


class VoiceQuizManager:
    """Quản lý toàn bộ voice quiz (v2.0)"""
    
    def __init__(self):
        self.voice_manager = VoiceManager()
        self.results = []
    
    def ask_question_voice(self, question_text: str, language: str = "en", repeat: int = 2) -> Optional[str]:
        """
        Hỏi câu hỏi bằng giọng nói (lặp lại) + tự động lắng nghe trả lời
        
        Args:
            question_text: Nội dung câu hỏi
            language: Ngôn ngữ ("en", "vi", "zh", "ja")
            repeat: Số lần đọc câu hỏi
        
        Returns: Câu trả lời của người dùng hoặc None
        """
        # 1. Đọc câu hỏi lặp lại
        for i in range(repeat):
            print(f"\n[Lần {i+1}/{repeat}] 📢 Đọc câu hỏi...")
            self.voice_manager.speak_google_tts(question_text, language=language)
            
            if i < repeat - 1:
                print("⏳ Chờ 1 giây...")
                import time
                time.sleep(1)
        
        # 2. Tự động lắng nghe trả lời
        print("\n▶️ Tự động lắng nghe trả lời...")
        answer = self.voice_manager.listen_to_microphone(timeout=10, language='en-US')
        
        return answer
    
    def compare_answers(self, user_answer: str, correct_answer: str) -> Tuple[bool, float, str]:
        """
        So sánh câu trả lời của người dùng với câu trả lời đúng
        Returns: (is_correct, similarity_score, feedback)
        """
        if not user_answer:
            return False, 0.0, "❌ Không có câu trả lời"
        
        user_clean = user_answer.lower().strip()
        correct_clean = correct_answer.lower().strip()
        
        # Tính độ tương đồng
        matcher = SequenceMatcher(None, user_clean, correct_clean)
        similarity = matcher.ratio()
        
        # Kiểm tra từng từ
        user_words = set(user_clean.split())
        correct_words = set(correct_clean.split())
        
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
    print("🧪 Test Voice Manager v2.0...")
    
    manager = VoiceQuizManager()
    
    # Test TTS
    print("\n🔊 Test Google Text-to-Speech...")
    manager.voice_manager.speak_google_tts("Hello, how are you today?", language="en")
    
    print("\n✅ Test hoàn thành!")
