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
        
        user_answer = user_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        
        # Kiểm tra chính xác (loại bỏ khoảng trắng dư thừa)
        if user_answer == correct_answer:
            if attempt == 1:
                score = 10
                feedback = "✓ Hoàn hảo!"
            elif attempt == 2:
                score = 7
                feedback = "✓ Đúng, nhưng lần trước nên cảnh báo"
            else:
                score = 4
                feedback = "✓ Đúng rồi (lần thứ 3)"
        # Kiểm tra gần đúng (chứa từ khóa chính)
        elif self._is_similar(user_answer, correct_answer):
            if attempt == 1:
                score = 8
                feedback = "~ Gần đúng, xem lại lần nữa"
            elif attempt == 2:
                score = 5
                feedback = "~ Gần đúng"
            else:
                score = 2
                feedback = "~ Gần đúng (lần thứ 3)"
        else:
            score = 0
            feedback = "✗ Sai rồi"
        
        return score, feedback
    
    def _is_similar(self, answer1, answer2):
        """Kiểm tra hai câu trả lời có gần giống nhau không"""
        # Loại bỏ khoảng trắng và dấu câu
        import re
        answer1 = re.sub(r'[^\w\s]', '', answer1).split()
        answer2 = re.sub(r'[^\w\s]', '', answer2).split()
        
        # Nếu chứa ít nhất 70% từ giống nhau
        if len(answer2) > 0:
            common_words = len(set(answer1) & set(answer2))
            similarity = common_words / len(answer2)
            return similarity >= 0.7
        return False
    
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
