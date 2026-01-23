#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎓 CHATBOT KIỂM TRA NGÔN NGỮ
Ứng dụng kiểm tra tiếng Anh, Trung, Nhật tự động
"""

import os
import json
from quiz_engine import QuizEngine
from data_loader import DataLoader, create_sample_data
from scorer import Scorer

class LanguageQuizApp:
    def __init__(self):
        self.data_loader = DataLoader("data")
        self.quiz_engine = None
        self.language = None
        self.quiz_type = None
        
        # Kiểm tra và tạo folder data nếu cần
        if not os.path.exists("data"):
            os.makedirs("data")
            create_sample_data()
    
    def print_header(self):
        """In tiêu đề"""
        print("\n" + "="*60)
        print("  🎓 CHATBOT KIỂM TRA NGÔN NGỮ")
        print("  ✓ Tiếng Anh | ✓ Tiếng Trung | ✓ Tiếng Nhật")
        print("="*60 + "\n")
    
    def print_menu(self, options, title="Menu"):
        """In menu chọn"""
        print(f"\n📌 {title}:")
        for key, value in options.items():
            print(f"  {key}. {value}")
        print()
    
    def choose_language(self):
        """Chọn ngôn ngữ"""
        languages = {
            "1": ("English (Tiếng Anh)", "sample_english.json"),
            "2": ("Chinese (Tiếng Trung)", "sample_chinese.json"),
            "3": ("Japanese (Tiếng Nhật)", "sample_japanese.json")
        }
        
        self.print_menu(
            {k: v[0] for k, v in languages.items()},
            "Chọn ngôn ngữ"
        )
        
        choice = input("Nhập lựa chọn (1-3): ").strip()
        
        if choice in languages:
            self.language = languages[choice][0]
            data_file = languages[choice][1]
            
            # Nếu file không tồn tại, tạo file mẫu
            if not os.path.exists(os.path.join("data", data_file)):
                self._create_sample_data_file(data_file, choice)
            
            print(f"✓ Đã chọn: {self.language}\n")
            return data_file
        else:
            print("❌ Lựa chọn không hợp lệ!")
            return self.choose_language()
    
    def choose_quiz_type(self):
        """Chọn loại kiểm tra"""
        quiz_types = {
            "1": "meaning - Hỏi ý nghĩa (Từ → Tiếng Việt)",
            "2": "example - Hỏi dịch ví dụ",
            "3": "vietnamese - Dịch từ Tiếng Việt"
        }
        
        self.print_menu(quiz_types, "Chọn loại kiểm tra")
        
        choice = input("Nhập lựa chọn (1-3): ").strip()
        
        quiz_type_map = {"1": "meaning", "2": "example", "3": "vietnamese"}
        if choice in quiz_type_map:
            self.quiz_type = quiz_type_map[choice]
            print(f"✓ Loại kiểm tra: {quiz_types[choice]}\n")
            return self.quiz_type
        else:
            print("❌ Lựa chọn không hợp lệ!")
            return self.choose_quiz_type()
    
    def choose_num_questions(self):
        """Chọn số lượng câu"""
        options = {
            "1": "5 câu",
            "2": "10 câu",
            "3": "15 câu",
            "4": "20 câu",
            "5": "Tất cả câu"
        }
        
        self.print_menu(options, "Chọn số câu kiểm tra")
        
        choice = input("Nhập lựa chọn (1-5): ").strip()
        
        num_map = {"1": 5, "2": 10, "3": 15, "4": 20, "5": 999}
        if choice in num_map:
            print(f"✓ Số câu: {options[choice]}\n")
            return num_map[choice]
        else:
            print("❌ Lựa chọn không hợp lệ!")
            return self.choose_num_questions()
    
    def run_quiz(self, questions):
        """Chạy kiểm tra"""
        num_questions = self.choose_num_questions()
        
        self.quiz_engine.shuffle_questions(num_questions)
        questions = self.quiz_engine.questions
        
        print(f"\n{'='*60}")
        print(f"🎯 BẮT ĐẦU KIỂM TRA - {len(questions)} câu")
        print(f"{'='*60}\n")
        
        for idx, question in enumerate(questions, 1):
            self._ask_question(question, idx, len(questions))
        
        # In kết quả
        average, grade = self.quiz_engine.scorer.print_summary()
        
        # Hỏi có xem chi tiết không
        if input("\nXem chi tiết kết quả? (c/n): ").lower() == 'c':
            self.quiz_engine.scorer.print_detailed_results()
    
    def _ask_question(self, question, question_num, total):
        """Hỏi một câu"""
        # Format câu hỏi
        question_text = self.quiz_engine.format_question(question, self.quiz_type)
        
        # Xác định đáp án đúng
        if self.quiz_type == "meaning":
            correct_answer = question.get('meaning', '')
        elif self.quiz_type == "example":
            correct_answer = question.get('example_vi', '')
        else:  # vietnamese
            correct_answer = question.get('example_en', '')
        
        # In tiến độ
        progress = self.quiz_engine.get_progress()
        print(f"\n{progress}")
        print(f"Câu {question_num}/{total}:")
        print(f"─" * 60)
        print(question_text)
        print()
        
        attempt = 1
        max_attempts = 3
        correct_answered = False
        
        # Vòng lặp cho phép sửa lỗi
        while attempt <= max_attempts and not correct_answered:
            if attempt > 1:
                print(f"🔄 Lần thứ {attempt}:")
            
            # Lựa chọn: trả lời hoặc gợi ý
            print("  (h = gợi ý, c = xem đáp án)")
            user_input = input("  Trả lời: ").strip()
            
            if user_input.lower() == 'h':
                hint = self.quiz_engine.get_hint(question)
                print(f"💡 {hint}\n")
                continue
            elif user_input.lower() == 'c':
                print(f"📌 Đáp án: {correct_answer}\n")
                score = 0
                correct_answered = True
                break
            
            # Kiểm tra trả lời
            is_correct, feedback, score = self.quiz_engine.check_answer(
                user_input, correct_answer, attempt
            )
            
            print(f"{feedback}")
            
            if is_correct:
                correct_answered = True
                print(f"✓ Đúng rồi! Bạn được {score}/10 điểm")
            else:
                if attempt < max_attempts:
                    suggestion = self.quiz_engine.suggest_correction(
                        user_input, correct_answer
                    )
                    print(f"💬 {suggestion}")
                    print()
                else:
                    print(f"📌 Đáp án đúng: {correct_answer}")
                    print(f"Bạn được {score}/10 điểm")
            
            attempt += 1
        
        # Lưu kết quả
        if not correct_answered:
            score = 0
        
        self.quiz_engine.scorer.add_result(
            question_num,
            question_text,
            user_input if 'user_input' in locals() else '(xem đáp án)',
            correct_answer,
            score
        )
        
        self.quiz_engine.move_to_next_question()
    
    def _create_sample_data_file(self, filename, language_code):
        """Tạo file dữ liệu mẫu"""
        if language_code == "1":  # English
            data = [
                {
                    "id": 1,
                    "word": "aunt",
                    "meaning": "cô, dì, bác gái",
                    "example_en": "Is she your aunt?",
                    "example_vi": "Cô ấy là cô của bạn phải không?"
                },
                {
                    "id": 2,
                    "word": "love",
                    "meaning": "yêu, thích",
                    "example_en": "Do you love this song?",
                    "example_vi": "Bạn có yêu thích bài hát này không?"
                },
                {
                    "id": 3,
                    "word": "white",
                    "meaning": "màu trắng",
                    "example_en": "Is your shirt white?",
                    "example_vi": "Áo của bạn màu trắng phải không?"
                },
                {
                    "id": 4,
                    "word": "help",
                    "meaning": "giúp đỡ",
                    "example_en": "Can you help me?",
                    "example_vi": "Bạn có thể giúp tôi không?"
                },
                {
                    "id": 5,
                    "word": "hundred",
                    "meaning": "một trăm",
                    "example_en": "Do you have a hundred dollars?",
                    "example_vi": "Bạn có 100 đô không?"
                }
            ]
        elif language_code == "2":  # Chinese
            data = [
                {
                    "id": 1,
                    "word": "你好",
                    "meaning": "xin chào",
                    "example_en": "Nǐ hǎo",
                    "example_vi": "Bạn khỏe không?"
                },
                {
                    "id": 2,
                    "word": "谢谢",
                    "meaning": "cảm ơn",
                    "example_en": "Xièxie",
                    "example_vi": "Cảm ơn bạn"
                }
            ]
        else:  # Japanese
            data = [
                {
                    "id": 1,
                    "word": "こんにちは",
                    "meaning": "xin chào (ban ngày)",
                    "example_en": "Konnichiha",
                    "example_vi": "Xin chào"
                },
                {
                    "id": 2,
                    "word": "ありがとう",
                    "meaning": "cảm ơn",
                    "example_en": "Arigatou",
                    "example_vi": "Cảm ơn bạn"
                }
            ]
        
        filepath = os.path.join("data", filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def main(self):
        """Chương trình chính"""
        while True:
            self.print_header()
            
            # Chọn ngôn ngữ
            data_file = self.choose_language()
            
            # Load dữ liệu
            questions = self.data_loader.load_json(data_file)
            
            if not questions:
                print("❌ Không có dữ liệu. Hãy kiểm tra lại file.\n")
                continue
            
            # Chọn loại kiểm tra
            self.choose_quiz_type()
            
            # Tạo quiz engine
            self.quiz_engine = QuizEngine(questions, self.language)
            
            # Chạy kiểm tra
            self.run_quiz(questions)
            
            # Hỏi có tiếp tục không
            if input("\n\n🔄 Bạn có muốn kiểm tra lại không? (c/n): ").lower() != 'c':
                print("\n👋 Cảm ơn đã sử dụng ứng dụng!")
                break

if __name__ == "__main__":
    app = LanguageQuizApp()
    app.main()
