"""
Engine kiểm tra: xử lý hỏi đáp, kiểm tra trả lời, cho phép sửa
"""

import random
from difflib import SequenceMatcher
from scorer import Scorer

class QuizEngine:
    def __init__(self, questions, language="English"):
        self.questions = questions
        self.language = language
        self.scorer = Scorer()
        self.current_question_idx = 0
        self.attempt = 1
    
    def shuffle_questions(self, num_questions):
        """Trộn và chọn số lượng câu cần thiết"""
        if num_questions > len(self.questions):
            num_questions = len(self.questions)
        
        self.questions = random.sample(self.questions, num_questions)
        return self.questions
    
    def get_current_question(self):
        """Lấy câu hỏi hiện tại"""
        if self.current_question_idx < len(self.questions):
            return self.questions[self.current_question_idx]
        return None
    
    def format_question(self, question, quiz_type="meaning"):
        """
        Định dạng câu hỏi theo loại
        Types:
        - meaning: Hỏi ý nghĩa tiếng Việt
        - example: Hỏi dịch ví dụ tiếng Anh
        - vietnamese: Hỏi dịch từ tiếng Việt sang tiếng Anh
        """
        if quiz_type == "meaning":
            return f"Từ '{question['word']}' có nghĩa là gì (tiếng Việt)?"
        elif quiz_type == "example":
            return f"Dịch ví dụ sau sang tiếng Việt:\n'{question['example_en']}'"
        elif quiz_type == "vietnamese":
            return f"Dịch sang tiếng Anh:\n'{question['example_vi']}'"
    
    def check_answer(self, user_answer, correct_answer, attempt=1):
        """
        Kiểm tra câu trả lời
        Trả về: (is_correct, feedback, score)
        """
        score, feedback = self.scorer.calculate_score(
            user_answer, correct_answer, attempt
        )
        
        is_correct = score >= 5  # Coi >= 5 là đúng
        return is_correct, feedback, score
    
    def get_hint(self, question):
        """Cung cấp gợi ý"""
        meaning = question.get('meaning', '')
        word = question.get('word', '')
        
        if len(meaning) > 3:
            hint = meaning[:3] + '*' * (len(meaning) - 3)
        else:
            hint = '*' * len(meaning)
        
        return f"Gợi ý: {hint} (Từ: {word})"
    
    def move_to_next_question(self):
        """Chuyển sang câu tiếp theo"""
        self.current_question_idx += 1
        self.attempt = 1
    
    def is_quiz_complete(self):
        """Kiểm tra xem kiểm tra đã hoàn tất chưa"""
        return self.current_question_idx >= len(self.questions)
    
    def get_progress(self):
        """Lấy tiến độ"""
        total = len(self.questions)
        current = self.current_question_idx + 1
        percentage = (self.current_question_idx / total) * 100
        return f"[{current}/{total}] {percentage:.0f}%"
    
    def suggest_correction(self, user_answer, correct_answer):
        """Gợi ý sửa lỗi"""
        similarity = SequenceMatcher(None, user_answer.lower(), 
                                    correct_answer.lower()).ratio()
        
        if similarity > 0.6:
            return f"Bạn viết gần đúng! Hãy kiểm tra lại chính tả."
        elif similarity > 0.3:
            return f"Bạn viết một số từ đúng. Hãy thử lại!"
        else:
            return f"Câu trả lời hoàn toàn khác. Đáp án là: {correct_answer}"
    
    def get_statistics(self):
        """Lấy thống kê"""
        return {
            'total_questions': len(self.questions),
            'answered': self.scorer.questions_answered,
            'total_points': self.scorer.total_points,
            'average_score': self.scorer.get_average_score()
        }
