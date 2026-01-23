"""
GUI VERSION - Giao diện đồ họa chatbot kiểm tra ngôn ngữ
Sử dụng tkinter (built-in Python)
Xử lý Excel trực tiếp mà không cần chuyển JSON
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import openpyxl
import random
from quiz_engine import QuizEngine
from scorer import Scorer
from pathlib import Path
import json


class LanguageQuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Chatbot Kiểm Tra Ngôn Ngữ")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Biến
        self.quiz_engine = None
        self.selected_file = None
        self.data = []
        self.current_question_idx = 0
        self.attempt = 1
        
        # Setup style
        self.root.configure(bg="#f0f0f0")
        style = ttk.Style()
        style.theme_use('clam')
        
        # Tạo notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Setup
        self.setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_tab, text="📋 Chuẩn bị")
        self._create_setup_tab()
        
        # Tab 2: Quiz
        self.quiz_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.quiz_tab, text="🎯 Kiểm tra")
        self._create_quiz_tab()
        
        # Tab 3: Results
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="📊 Kết quả")
        self._create_results_tab()
    
    def _create_setup_tab(self):
        """Tab chuẩn bị - chọn file Excel"""
        
        # Frame chọn file
        file_frame = ttk.LabelFrame(self.setup_tab, text="1️⃣ Chọn File Excel", padding=15)
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(file_frame, text="📁 Chọn File Excel...", 
                  command=self.select_excel_file, width=30).pack(pady=10)
        
        self.file_label = ttk.Label(file_frame, text="Chưa chọn file", 
                                    font=("Arial", 10), foreground="gray")
        self.file_label.pack(pady=5)
        
        # Frame lựa chọn
        options_frame = ttk.LabelFrame(self.setup_tab, text="2️⃣ Cấu hình Kiểm tra", padding=15)
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Chọn Sheet (nếu Excel có nhiều sheet)
        ttk.Label(options_frame, text="Chọn Sheet:").pack(anchor=tk.W)
        self.sheet_combo = ttk.Combobox(options_frame, state="readonly", width=40)
        self.sheet_combo.pack(pady=5)
        
        # Chọn loại kiểm tra
        ttk.Label(options_frame, text="Loại Kiểm tra:").pack(anchor=tk.W)
        self.quiz_type_var = tk.StringVar(value="meaning")
        quiz_types = [
            ("Meaning - Hỏi ý nghĩa", "meaning"),
            ("Example - Dịch ví dụ", "example"),
            ("Vietnamese - Dịch từ Việt", "vietnamese")
        ]
        for text, value in quiz_types:
            ttk.Radiobutton(options_frame, text=text, variable=self.quiz_type_var, 
                           value=value).pack(anchor=tk.W)
        
        # Chọn số câu
        ttk.Label(options_frame, text="Số Câu Kiểm tra:").pack(anchor=tk.W, pady=(10,0))
        self.num_questions_var = tk.IntVar(value=10)
        for num in [5, 10, 15, 20]:
            ttk.Radiobutton(options_frame, text=f"{num} câu", 
                           variable=self.num_questions_var, value=num).pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="Tất cả câu", 
                       variable=self.num_questions_var, value=999).pack(anchor=tk.W)
        
        # Nút bắt đầu
        ttk.Button(options_frame, text="▶️ BẮT ĐẦU KIỂM TRA", 
                  command=self.start_quiz).pack(pady=15, fill=tk.X)
    
    def _create_quiz_tab(self):
        """Tab kiểm tra"""
        
        # Progress
        progress_frame = ttk.Frame(self.quiz_tab)
        progress_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(progress_frame, text="Tiến độ:").pack(side=tk.LEFT)
        self.progress_label = ttk.Label(progress_frame, text="0/0", font=("Arial", 12, "bold"))
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Câu hỏi
        question_frame = ttk.LabelFrame(self.quiz_tab, text="❓ Câu Hỏi", padding=15)
        question_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.question_text = scrolledtext.ScrolledText(question_frame, height=6, wrap=tk.WORD)
        self.question_text.pack(fill=tk.BOTH, expand=True)
        self.question_text.config(state=tk.DISABLED)
        
        # Trả lời
        answer_frame = ttk.LabelFrame(self.quiz_tab, text="✏️ Trả Lời", padding=15)
        answer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(answer_frame, text="Câu trả lời:").pack(anchor=tk.W)
        self.answer_entry = ttk.Entry(answer_frame, width=60)
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", lambda e: self.submit_answer())
        
        # Nút hành động
        button_frame = ttk.Frame(answer_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="💬 Gợi Ý (h)", 
                  command=self.show_hint, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="👁️ Xem Đáp Án (c)", 
                  command=self.show_answer, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ Gửi (Enter)", 
                  command=self.submit_answer, width=15).pack(side=tk.LEFT, padx=5)
        
        # Feedback
        self.feedback_text = tk.Text(answer_frame, height=3, wrap=tk.WORD)
        self.feedback_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.feedback_text.config(state=tk.DISABLED)
    
    def _create_results_tab(self):
        """Tab kết quả"""
        
        self.results_text = scrolledtext.ScrolledText(self.results_tab, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.results_text.config(state=tk.DISABLED)
        
        # Nút export
        button_frame = ttk.Frame(self.results_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="💾 Lưu Kết Quả", 
                  command=self.save_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Kiểm Tra Lại", 
                  command=self.restart_quiz).pack(side=tk.LEFT, padx=5)
    
    def select_excel_file(self):
        """Chọn file Excel"""
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"✓ {Path(file_path).name}", foreground="green")
            self._load_excel_sheets()
    
    def _load_excel_sheets(self):
        """Load các sheet từ file Excel"""
        try:
            wb = openpyxl.load_workbook(self.selected_file, data_only=True)
            sheet_names = wb.sheetnames
            self.sheet_combo['values'] = sheet_names
            if sheet_names:
                self.sheet_combo.current(0)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở file Excel:\n{e}")
    
    def _read_excel_data(self, sheet_name):
        """Đọc dữ liệu từ Excel sheet"""
        try:
            wb = openpyxl.load_workbook(self.selected_file, data_only=True)
            ws = wb[sheet_name]
            
            # Kiểm tra header
            header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
            
            # Kiểm tra format chuẩn (phải có ít nhất 4 cột)
            if len(header_row) < 4:
                messagebox.showerror(
                    "Lỗi Format", 
                    f"❌ File Excel không đúng format!\n\n"
                    f"Cần 4 cột: Word | Meaning | Example EN | Example VI\n"
                    f"Hiện tại chỉ có: {len(header_row)} cột\n\n"
                    f"Vui lòng dùng template: python create_templates.py"
                )
                return []
            
            data = []
            question_id = 1
            error_rows = []
            
            # Bỏ qua dòng tiêu đề (dòng 1)
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                # Kiểm tra dòng trống
                if not row[0]:
                    continue
                
                # Kiểm tra có đủ 4 cột không
                if len(row) < 4:
                    error_rows.append(row_idx)
                    continue
                
                try:
                    item = {
                        "id": question_id,
                        "word": str(row[0]).strip() if row[0] else "",
                        "meaning": str(row[1]).strip() if row[1] else "",
                        "example_en": str(row[2]).strip() if row[2] else "",
                        "example_vi": str(row[3]).strip() if row[3] else ""
                    }
                    
                    # Kiểm tra dữ liệu hợp lệ
                    if item["word"] and item["meaning"]:
                        data.append(item)
                        question_id += 1
                except Exception as e:
                    error_rows.append(row_idx)
                    continue
            
            # Cảnh báo nếu có dòng lỗi
            if error_rows:
                messagebox.showwarning(
                    "Cảnh báo", 
                    f"⚠️ Bỏ qua {len(error_rows)} dòng lỗi: {error_rows[:5]}"
                )
            
            if not data:
                messagebox.showerror(
                    "Lỗi", 
                    "❌ Không có dữ liệu hợp lệ trong file Excel!\n\n"
                    "Kiểm tra:\n"
                    "1. Hàng 1 là header (Word, Meaning, Example EN, Example VI)\n"
                    "2. Cột A (Word) không được trống\n"
                    "3. Ít nhất 2 cột không trống: Meaning & Word"
                )
                return []
            
            return data
        except Exception as e:
            messagebox.showerror(
                "Lỗi", 
                f"❌ Lỗi khi đọc file Excel:\n{str(e)}\n\n"
                f"Vui lòng kiểm tra:\n"
                f"1. File có đúng format .xlsx không?\n"
                f"2. Header (hàng 1) có 4 cột không?\n"
                f"3. Dữ liệu bắt đầu từ hàng 2?"
            )
            return []
    
    def start_quiz(self):
        """Bắt đầu kiểm tra"""
        if not self.selected_file:
            messagebox.showwarning("Cảnh báo", "Hãy chọn file Excel trước!")
            return
        
        sheet_name = self.sheet_combo.get()
        if not sheet_name:
            messagebox.showwarning("Cảnh báo", "Hãy chọn Sheet!")
            return
        
        # Load dữ liệu từ Excel
        self.data = self._read_excel_data(sheet_name)
        
        if not self.data:
            messagebox.showerror("Lỗi", "Không có dữ liệu trong Sheet!")
            return
        
        # Tạo quiz engine
        self.quiz_engine = QuizEngine(self.data, sheet_name)
        
        # Chuẩn bị kiểm tra
        num_questions = self.num_questions_var.get()
        self.quiz_engine.shuffle_questions(num_questions if num_questions < 999 else len(self.data))
        
        self.current_question_idx = 0
        self.attempt = 1
        
        # Chuyển sang tab kiểm tra
        self.notebook.select(1)
        self.display_question()
    
    def display_question(self):
        """Hiển thị câu hỏi"""
        if self.current_question_idx >= len(self.quiz_engine.questions):
            self.show_results()
            return
        
        question = self.quiz_engine.questions[self.current_question_idx]
        quiz_type = self.quiz_type_var.get()
        
        # Format câu hỏi
        question_text = self.quiz_engine.format_question(question, quiz_type)
        
        # Cập nhật progress
        total = len(self.quiz_engine.questions)
        current = self.current_question_idx + 1
        self.progress_label.config(text=f"{current}/{total}")
        self.progress_bar['value'] = (current / total) * 100
        
        # Hiển thị câu hỏi
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert("1.0", f"Câu {current}/{total}:\n\n{question_text}")
        self.question_text.config(state=tk.DISABLED)
        
        # Xóa trường trả lời
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()
        
        # Xóa feedback
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.config(state=tk.DISABLED)
    
    def submit_answer(self):
        """Gửi câu trả lời"""
        user_answer = self.answer_entry.get().strip()
        
        if not user_answer:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập câu trả lời!")
            return
        
        question = self.quiz_engine.questions[self.current_question_idx]
        quiz_type = self.quiz_type_var.get()
        
        # Xác định đáp án đúng
        if quiz_type == "meaning":
            correct_answer = question.get('meaning', '')
        elif quiz_type == "example":
            correct_answer = question.get('example_vi', '')
        else:
            correct_answer = question.get('example_en', '')
        
        # Kiểm tra trả lời
        is_correct, feedback, score = self.quiz_engine.check_answer(
            user_answer, correct_answer, self.attempt
        )
        
        # Hiển thị feedback
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete("1.0", tk.END)
        
        feedback_msg = f"{feedback}\n"
        
        if is_correct:
            feedback_msg += f"✓ Bạn được {score}/10 điểm"
        else:
            if self.attempt < 3:
                suggestion = self.quiz_engine.suggest_correction(user_answer, correct_answer)
                feedback_msg += f"💬 {suggestion}\n"
                feedback_msg += f"(Lần {self.attempt}/3)"
            else:
                feedback_msg += f"📌 Đáp án: {correct_answer}\n"
                feedback_msg += f"Bạn được {score}/10 điểm"
        
        self.feedback_text.insert("1.0", feedback_msg)
        self.feedback_text.config(state=tk.DISABLED)
        
        # Lưu kết quả
        if self.attempt >= 3 or is_correct:
            if not is_correct:
                score = 0
            
            self.quiz_engine.scorer.add_result(
                self.current_question_idx + 1,
                f"Câu {self.current_question_idx + 1}",
                user_answer,
                correct_answer,
                score
            )
            
            # Chuyển sang câu tiếp theo
            self.current_question_idx += 1
            self.attempt = 1
            
            # Sau 1 giây, hiển thị câu tiếp theo
            self.root.after(2000, self.display_question)
        else:
            self.attempt += 1
            self.answer_entry.delete(0, tk.END)
    
    def show_hint(self):
        """Hiển thị gợi ý"""
        question = self.quiz_engine.questions[self.current_question_idx]
        hint = self.quiz_engine.get_hint(question)
        
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.insert("1.0", f"💡 {hint}")
        self.feedback_text.config(state=tk.DISABLED)
    
    def show_answer(self):
        """Hiển thị đáp án"""
        question = self.quiz_engine.questions[self.current_question_idx]
        quiz_type = self.quiz_type_var.get()
        
        if quiz_type == "meaning":
            correct_answer = question.get('meaning', '')
        elif quiz_type == "example":
            correct_answer = question.get('example_vi', '')
        else:
            correct_answer = question.get('example_en', '')
        
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.insert("1.0", f"📌 Đáp án: {correct_answer}\n(Bạn được 0 điểm)")
        self.feedback_text.config(state=tk.DISABLED)
        
        # Lưu kết quả với điểm 0
        self.quiz_engine.scorer.add_result(
            self.current_question_idx + 1,
            f"Câu {self.current_question_idx + 1}",
            "(xem đáp án)",
            correct_answer,
            0
        )
        
        # Chuyển sang câu tiếp theo sau 2 giây
        self.current_question_idx += 1
        self.attempt = 1
        self.root.after(2000, self.display_question)
    
    def show_results(self):
        """Hiển thị kết quả"""
        average, grade = self.quiz_engine.scorer.print_summary()
        
        # Cập nhật tab kết quả
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        results_content = "="*60 + "\n"
        results_content += "📊 KẾT QUẢ KIỂM TRA\n"
        results_content += "="*60 + "\n\n"
        
        total = self.quiz_engine.scorer.total_points
        num_questions = self.quiz_engine.scorer.questions_answered
        results_content += f"Tổng điểm: {total}/{num_questions * 10}\n"
        results_content += f"Điểm trung bình: {average:.1f}/100\n"
        results_content += f"Xếp loại: {grade}\n"
        results_content += "\n" + "="*60 + "\n"
        results_content += "CHI TIẾT KẾT QUẢ:\n"
        results_content += "="*60 + "\n\n"
        
        for result in self.quiz_engine.scorer.results:
            results_content += f"Câu {result['question']}\n"
            results_content += f"  Câu hỏi: {result['text'][:60]}...\n"
            results_content += f"  Trả lời: {result['user_answer']}\n"
            results_content += f"  Đáp án: {result['correct_answer']}\n"
            results_content += f"  Điểm: {result['score']}/10\n"
            results_content += "\n"
        
        self.results_text.insert("1.0", results_content)
        self.results_text.config(state=tk.DISABLED)
        
        # Chuyển sang tab kết quả
        self.notebook.select(2)
    
    def save_results(self):
        """Lưu kết quả"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                results_data = {
                    'total_points': self.quiz_engine.scorer.total_points,
                    'questions_answered': self.quiz_engine.scorer.questions_answered,
                    'average_score': self.quiz_engine.scorer.get_average_score(),
                    'grade': self.quiz_engine.scorer.get_grade(
                        self.quiz_engine.scorer.get_average_score()
                    ),
                    'results': self.quiz_engine.scorer.results
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Thành công", f"Kết quả đã lưu vào:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi lưu file:\n{e}")
    
    def restart_quiz(self):
        """Kiểm tra lại"""
        self.notebook.select(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = LanguageQuizGUI(root)
    root.mainloop()
