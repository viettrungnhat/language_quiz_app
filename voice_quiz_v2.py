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
    import winsound
except ImportError:
    winsound = None

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
                    print("[OK] AWS Polly initialized successfully")
                else:
                    print("[INFO] AWS credentials not found in .env - Polly disabled")
                    self.polly_available = False
            except Exception as e:
                print(f"[WARN] AWS Polly init error: {e}")
                self.polly_available = False
        
        # Speech Recognition
        self.recognizer = sr.Recognizer() if sr else None
        if self.recognizer:
            # ⚠️ QUAN TRỌNG: Cố định energy_threshold (không auto-adjust)
            # Giảm energy_threshold để nhạy hơn (mặc định 300, tăng = kém nhạy hơn)
            self.recognizer.energy_threshold = 5  # Rất thấp = cực kỳ nhạy, sẽ nhận từ tiếng lẹo
            self.recognizer.dynamic_energy_threshold = False  # KHÔNG auto-adjust
            print(f"[OK] STT Energy Threshold: {self.recognizer.energy_threshold} (ultra-sensitive)")


        
        # Pygame cho audio playback
        self.pygame_available = pygame is not None
        if self.pygame_available:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"[WARN] Pygame init error: {e}")
                self.pygame_available = False
    
    @staticmethod
    def list_microphones():
        """List all available microphones"""
        try:
            if not sr:
                return []
            
            mics = []
            for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
                mics.append((i, mic_name))
            return mics
        except Exception as e:
            print(f"⚠️ Error listing microphones: {e}")
            return [(None, "(Mặc định)")]
    
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
            
            # 🔊 Wrap text với SSML để tăng volume
            ssml_text = f'<speak><prosody volume="loud">{text}</prosody></speak>'
            
            # Gọi AWS Polly
            response = self.polly_client.synthesize_speech(
                Text=ssml_text,
                OutputFormat='mp3',
                VoiceId=polly_voice,
                Engine='standard',  # ⚡ Standard engine nhanh hơn neural
                TextType='ssml'  # ✅ Báo là SSML

            )
            
            # Phát audio
            audio_stream = response['AudioStream'].read()
            audio_fp = io.BytesIO(audio_stream)
            
            if self.pygame_available:
                self._play_audio_pygame(audio_fp, language=language)
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
    
    def _play_audio_pygame(self, audio_fp, language="en"):
        """Phát audio bằng pygame với volume khác nhau per language"""
        try:
            # Ensure pygame mixer is initialized
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Volume mapping: Anh/Trung/Nhật max, Việt giảm xuống
            volume_map = {
                "en": 1.0,      # English: max
                "zh": 1.0,      # Chinese: max
                "ja": 1.0,      # Japanese: max
                "vi": 0.5,      # Vietnamese: 50% (hạ xuống)
            }
            
            lang_key = language.lower()[:2]  # Lấy 2 ký tự đầu (en, zh, ja, vi)
            volume = volume_map.get(lang_key, 1.0)
            
            pygame.mixer.music.load(audio_fp)
            pygame.mixer.music.set_volume(volume)
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
    
    def listen_to_microphone(self, timeout: int = 10, language: str = "en-US", quiz_type: str = "meaning") -> Optional[str]:
        """
        Lắng nghe từ microphone và chuyển thành text
        Dùng Google Speech Recognition hoặc Whisper
        
        Args:
            timeout: Tổng thời gian lắng nghe (giây)
            language: Ngôn ngữ STT
            quiz_type: Loại quiz ("meaning", "example", "vietnamese") để điều chỉnh thời gian lắng nghe
        
        Returns: text hoặc None nếu lỗi
        """
        if not sr:
            print("❌ speech_recognition not installed")
            return None
        
        # Điều chỉnh phrase_time_limit dựa vào quiz_type
        # "meaning": 4s (từ đơn, ngắn), "example"/"vietnamese": 12s (câu dài, phù hợp)
        phrase_time_limit = 4 if quiz_type == "meaning" else 12
        # Điều chỉnh pause_threshold tùy theo loại quiz
        pause_threshold = 0.5 if quiz_type == "meaning" else 0.6
        
        try:
            with sr.Microphone() as source:
                print("🎤 Đang lắng nghe... Hãy nói câu trả lời của bạn")
                
                # 🔊 Phát beep báo hiệu bắt đầu
                if winsound:
                    winsound.Beep(1000, 200)  # 1000 Hz, 200ms
                
                # ⚠️ KHÔNG dùng adjust_for_ambient_noise - nó sẽ ghi đè energy_threshold!
                # Chỉ cần pause_threshold để cho phép giọng nói tự nhiên
                self.recognizer.pause_threshold = pause_threshold
                self.recognizer.phrase_time_limit = phrase_time_limit  # ⏱️ Thay đổi tùy theo loại quiz
                
                print(f"⚙️ Energy threshold: {self.recognizer.energy_threshold} (fixed)")
                print(f"⏱️ Thời gian lắng nghe: {phrase_time_limit}s ({quiz_type})")
                
                # Ghi âm
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                # 🔊 Phát beep báo hiệu kết thúc
                if winsound:
                    winsound.Beep(800, 150)  # 800 Hz, 150ms
                
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
        
        except Exception as e:
            if "timed out" in str(e).lower():
                print("❌ Hết thời gian. Hãy nói câu trả lời.")
            else:
                print(f"❌ Lỗi microphone: {str(e)}")
            return None
            return None


class VoiceQuizManager:
    """Quản lý toàn bộ voice quiz (v2.0)"""
    
    def __init__(self):
        self.voice_manager = VoiceManager()
        self.results = []
    
    def ask_question_voice(self, question_text: str, language: str = "en", repeat: int = 2, quiz_type: str = "meaning") -> Optional[str]:
        """
        Hỏi câu hỏi bằng giọng nói (lặp lại) + tự động lắng nghe trả lời
        
        Args:
            question_text: Nội dung câu hỏi
            language: Ngôn ngữ ("en", "vi", "zh", "ja")
            repeat: Số lần đọc câu hỏi
            quiz_type: Loại quiz ("meaning", "example", "vietnamese") để điều chỉnh thời gian lắng nghe
        
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
        answer = self.voice_manager.listen_to_microphone(timeout=10, language='en-US', quiz_type=quiz_type)
        
        return answer
    
    def compare_answers(self, user_answer: str, correct_answer: str) -> Tuple[bool, float, str, bool]:
        """
        So sánh câu trả lời của người dùng với câu trả lời đúng
        Dùng Scorer từ app cho consistent comparison
        Returns: (is_correct, similarity_score, feedback, is_semantic)
        """
        if not user_answer:
            return False, 0.0, "❌ Không có câu trả lời", False
        
        # Import scorer để dùng logic consistent
        try:
            from scorer import Scorer
            scorer = Scorer()
            score, feedback, is_semantic = scorer.calculate_score(user_answer, correct_answer, attempt=1)
            
            # Convert score to similarity (10 = 1.0, 0 = 0.0)
            similarity = score / 10.0
            is_correct = score >= 5  # Coi >= 5 là đúng
            
            return is_correct, similarity, feedback, is_semantic
        except ImportError:
            # Fallback nếu không có scorer
            print("⚠️ Scorer not found, using fallback comparison")
            
            import re
            import unicodedata
            
            def normalize_text(text):
                # Loại bỏ dấu thanh Unicode
                nfd_text = unicodedata.normalize('NFD', text)
                text_clean = ''.join(c for c in nfd_text if unicodedata.category(c) != 'Mn')
                # Loại bỏ dấu câu (,;:.!?)
                text_clean = re.sub(r'[^\w\s]', '', text_clean)
                # Loại bỏ khoảng trắng dư thừa
                return re.sub(r'\s+', ' ', text_clean.strip().lower())
            
            user_normalized = normalize_text(user_answer)
            correct_normalized = normalize_text(correct_answer)
            
            if user_normalized == correct_normalized:
                return True, 1.0, "✅ Hoàn hảo!", False
            
            # Fallback simple check
            matcher = SequenceMatcher(None, user_normalized, correct_normalized)
            similarity = matcher.ratio()
            
            if similarity >= 0.95:
                return True, similarity, f"✔️ Gần đúng ({similarity*100:.0f}%)", False
            
            return False, similarity, f"❌ Sai. Trả lời đúng là: {correct_answer}", False


# Test
if __name__ == "__main__":
    print("🧪 Test Voice Manager v2.0...")
    
    manager = VoiceQuizManager()
    
    # Test TTS
    print("\n🔊 Test Google Text-to-Speech...")
    manager.voice_manager.speak_google_tts("Hello, how are you today?", language="en")
    
    print("\n✅ Test hoàn thành!")
