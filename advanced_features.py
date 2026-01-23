"""
Các tính năng nâng cao (Optional - thêm sau)
"""

import json
from datetime import datetime
from pathlib import Path

class UserProgress:
    """Lưu trữ tiến độ học của người dùng"""
    
    def __init__(self, username, progress_file="progress.json"):
        self.username = username
        self.progress_file = progress_file
        self.progress_data = self._load_progress()
    
    def _load_progress(self):
        """Load tiến độ từ file"""
        if Path(self.progress_file).exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_progress(self):
        """Lưu tiến độ vào file"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
    
    def record_result(self, language, quiz_type, score, questions):
        """Ghi lại kết quả kiểm tra"""
        key = f"{language}_{quiz_type}"
        
        if key not in self.progress_data:
            self.progress_data[key] = {
                'attempts': [],
                'weak_words': []
            }
        
        self.progress_data[key]['attempts'].append({
            'date': datetime.now().isoformat(),
            'score': score,
            'questions': questions
        })
        
        self._save_progress()
    
    def add_weak_word(self, language, word):
        """Thêm từ vào danh sách từ yếu"""
        key = f"{language}_weak"
        if key not in self.progress_data:
            self.progress_data[key] = []
        
        if word not in self.progress_data[key]:
            self.progress_data[key].append(word)
        
        self._save_progress()
    
    def get_statistics(self, language):
        """Lấy thống kê cho một ngôn ngữ"""
        stats = {}
        for key in self.progress_data:
            if key.startswith(language):
                stats[key] = self.progress_data[key]
        return stats


class TextToSpeech:
    """Tính năng phát âm (dùng pyttsx3)"""
    
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.available = True
        except ImportError:
            print("⚠️  pyttsx3 chưa được cài. Cài bằng: pip install pyttsx3")
            self.available = False
    
    def speak(self, text, language="en"):
        """Phát âm một đoạn văn bản"""
        if not self.available:
            return False
        
        try:
            self.engine.setProperty('rate', 150)  # Tốc độ
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"❌ Lỗi phát âm: {e}")
            return False


class WeakWordMode:
    """Chế độ ôn tập từ yếu"""
    
    def __init__(self, weak_words):
        self.weak_words = weak_words
    
    def get_weak_word_quiz(self, num_questions):
        """Lấy câu hỏi từ từ yếu"""
        import random
        
        if len(self.weak_words) < num_questions:
            questions = self.weak_words
        else:
            questions = random.sample(self.weak_words, num_questions)
        
        return questions
    
    def print_weak_word_summary(self):
        """In tóm tắt từ yếu"""
        print("\n📍 DANH SÁCH TỪ YẾU")
        print("="*60)
        for idx, word in enumerate(self.weak_words, 1):
            print(f"{idx}. {word}")
        print(f"Tổng: {len(self.weak_words)} từ")
        print("="*60)


class QuizStatistics:
    """Thống kê chi tiết kết quả kiểm tra"""
    
    def __init__(self, results):
        self.results = results
    
    def get_accuracy_by_type(self):
        """Độ chính xác theo loại câu"""
        type_stats = {}
        for result in self.results:
            # Phân tích từng loại
            pass
        return type_stats
    
    def get_trend(self):
        """Xu hướng cải thiện"""
        if len(self.results) < 2:
            return "Chưa đủ dữ liệu"
        
        first_score = self.results[0]['score']
        last_score = self.results[-1]['score']
        
        if last_score > first_score:
            improvement = last_score - first_score
            return f"📈 Cải thiện {improvement:.1f} điểm"
        elif last_score < first_score:
            return f"📉 Giảm {first_score - last_score:.1f} điểm"
        else:
            return "➡️ Ổn định"


class ExportResults:
    """Xuất kết quả thành file"""
    
    @staticmethod
    def export_to_csv(results, filename="results.csv"):
        """Xuất sang CSV"""
        import csv
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Câu', 'Câu hỏi', 'Trả lời', 'Đáp án', 'Điểm'])
                
                for result in results:
                    writer.writerow([
                        result['question'],
                        result['text'],
                        result['user_answer'],
                        result['correct_answer'],
                        result['score']
                    ])
            
            print(f"✓ Xuất thành công: {filename}")
            return True
        except Exception as e:
            print(f"❌ Lỗi xuất file: {e}")
            return False
    
    @staticmethod
    def export_to_json(results, filename="results.json"):
        """Xuất sang JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Xuất thành công: {filename}")
            return True
        except Exception as e:
            print(f"❌ Lỗi xuất file: {e}")
            return False


# Hướng dẫn sử dụng các tính năng nâng cao

"""
CÁCH TÍCH HỢP CÁC TÍNH NĂNG NÀY VÀO main.py:

1. LƯỚI ĐỀ TỰ HỌC:
   from advanced_features import UserProgress
   
   progress = UserProgress("ten_hoc_vien")
   progress.record_result("English", "meaning", score=85, questions=10)

2. PHÁT ÂM:
   from advanced_features import TextToSpeech
   
   tts = TextToSpeech()
   tts.speak("Hello, how are you?")

3. ÔN TỬ YẾUCHẶU:
   from advanced_features import WeakWordMode
   
   weak_words = ["aunt", "love", "help"]
   weak_mode = WeakWordMode(weak_words)
   weak_mode.print_weak_word_summary()

4. XUẤT KẾT QUẢ:
   from advanced_features import ExportResults
   
   ExportResults.export_to_csv(results, "ket_qua.csv")
   ExportResults.export_to_json(results, "ket_qua.json")
"""
