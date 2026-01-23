"""
Hệ thống chấm điểm và đánh giá
"""

class Scorer:
    def __init__(self):
        self.total_points = 0
        self.questions_answered = 0
        self.results = []
    
    def calculate_score(self, user_answer, correct_answer, attempt=1):
        """
        Tính điểm dựa trên câu trả lời
        attempt: lần thứ mấy trả lời (1-3)
        
        Quy tắc:
        - Lần 1, chính xác: 10 điểm
        - Lần 1, gần đúng: 7-9 điểm
        - Lần 2, chính xác: 7 điểm
        - Lần 2, gần đúng: 5-6 điểm
        - Lần 3, bất kỳ: 3-4 điểm
        - Sai hoàn toàn: 0 điểm
        """
        import re
        import unicodedata
        
        # Normalize: loại bỏ dấu thanh tiếng Việt + dấu câu
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
        
        # 🔍 DEBUG
        print(f"📝 User input: '{user_answer}' → '{user_normalized}'")
        print(f"✅ Correct: '{correct_answer}' → '{correct_normalized}'")
        print(f"🔀 Match: {user_normalized == correct_normalized}")
        
        # Kiểm tra chính xác
        if user_normalized == correct_normalized:
            if attempt == 1:
                score = 10
                feedback = "✅ Hoàn hảo!"
            elif attempt == 2:
                score = 7
                feedback = "✅ Đúng!"
            else:
                score = 4
                feedback = "✅ Đúng (lần thứ 3)"
        # Kiểm tra gần đúng (chứa từ khóa chính)
        elif self._is_similar(user_normalized, correct_normalized):
            if attempt == 1:
                score = 8
                feedback = "✔️ Gần đúng"
            elif attempt == 2:
                score = 5
                feedback = "✔️ Gần đúng"
            else:
                score = 2
                feedback = "✔️ Gần đúng (lần thứ 3)"
        else:
            score = 0
            feedback = "❌ Sai rồi"
        
        return score, feedback
    
    def _is_similar(self, answer1, answer2):
        """
        Kiểm tra hai câu trả lời có gần giống nhau không
        Input đã được normalize từ calculate_score(), không cần normalize lại
        Chỉ bảo "gần đúng" nếu chứa ≥95% từ khóa chính
        """
        # Input đã normalize: "yeu thich" (không dấu, không dấu câu)
        words1 = set(answer1.split())
        words2 = set(answer2.split())
        
        if len(words2) == 0 or len(words1) == 0:
            return False
        
        # Kiểm tra % từ khóa chính có trong câu trả lời
        common_words = len(words1 & words2)
        similarity_correct = common_words / len(words2)  # % từ đúng có trong câu trả lời
        
        # Chỉ bảo gần đúng nếu có ít nhất 95% từ khóa chính
        # (tức là chỉ khác/thiếu 1 chữ quan trọng, không phải khác dấu câu/khoảng trắng)
        return similarity_correct >= 0.95
    
    def add_result(self, question_num, question_text, user_answer, correct_answer, score):
        """Thêm kết quả một câu"""
        self.results.append({
            'question': question_num,
            'text': question_text,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'score': score
        })
        self.total_points += score
        self.questions_answered += 1
    
    def get_average_score(self):
        """Tính điểm trung bình"""
        if self.questions_answered == 0:
            return 0
        return (self.total_points / (self.questions_answered * 10)) * 100
    
    def get_grade(self, percentage):
        """Xác định xếp loại"""
        if percentage >= 90:
            return "A - Xuất sắc"
        elif percentage >= 80:
            return "B - Tốt"
        elif percentage >= 70:
            return "C - Khá"
        elif percentage >= 60:
            return "D - Đạt"
        else:
            return "F - Chưa đạt"
    
    def print_summary(self):
        """In tóm tắt kết quả"""
        print("\n" + "="*60)
        print("📊 KẾT QUẢ KIỂM TRA")
        print("="*60)
        
        average = self.get_average_score()
        grade = self.get_grade(average)
        
        print(f"Tổng điểm: {self.total_points}/{self.questions_answered * 10}")
        print(f"Điểm trung bình: {average:.1f}/100")
        print(f"Xếp loại: {grade}")
        print("="*60)
        
        return average, grade
    
    def print_detailed_results(self):
        """In chi tiết kết quả từng câu"""
        print("\n📋 CHI TIẾT KẾT QUẢ:")
        print("-"*60)
        for result in self.results:
            print(f"\nCâu {result['question']}: {result['text'][:50]}...")
            print(f"  Your answer: {result['user_answer']}")
            print(f"  Correct: {result['correct_answer']}")
            print(f"  Score: {result['score']}/10")
        print("-"*60)
