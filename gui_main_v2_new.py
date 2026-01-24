"""
GUI VERSION 2.2 - Language Quiz with Enhanced Voice (v3)
Giao diện đồ họa kiểm tra ngôn ngữ với Voice Quiz cải tiến
- gTTS (Google Text-to-Speech) cho đọc chuẩn
- Google Speech Recognition cho nhận dạng tốt
- Đọc 2 lần + đếm ngược + tự động lắng nghe
- Phát feedback bằng giọng nói (Đúng/Sai/Gần đúng)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import openpyxl
import random
import time
from quiz_engine import QuizEngine
from voice_quiz_v2 import VoiceQuizManager
from db_manager import StudyHistoryDB
from pathlib import Path
import json
from threading import Thread, Lock
import tkinter.font as tkFont
import winsound  # Để phát beep sound
from datetime import datetime  # 🕐 Để lưu timestamp


class LanguageQuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Language Quiz v2.2 - Multi-Language Voice -Kiểm tra đa ngôn ngữ 0986183806")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        
        # 🎨 Set icon cho app
        try:
            icon_path = Path(__file__).parent / "logo.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
                print(f"✅ Đã set icon: {icon_path.name}")
        except Exception as e:
            print(f"⚠️ Không thể set icon: {e}")
        
        # Biến
        self.quiz_engine = None
        self.voice_manager = VoiceQuizManager()
        self.study_db = StudyHistoryDB()  # 🎓 Spaced repetition database
        self.selected_file = None
        self.data = []
        self.current_question_idx = 0
        self.attempt = 1
        self.quiz_results = []
        self.is_listening = False
        self.quiz_type_str = "meaning"
        self.test_mode = 1  # 1: Read VN → Answer Foreign | 2: Read Foreign → Answer VN
        self.feedback_thread = None  # Track feedback TTS
        self.app_running = True  # Flag để dừng threads khi app đóng
        self.voice_question_lock = Lock()  # 🔒 Lock để đảm bảo chỉ 1 câu hỏi voice chạy tại 1 thời điểm
        self.instruction_shown = False  # Track xem instruction đã được đọc chưa
        
        # Config file
        self.config_file = Path(__file__).parent / "user_settings.json"
        self.user_settings = self._load_settings()
        
        # 🎨 Lưu path icon để dùng cho popup
        self.icon_path = Path(__file__).parent / "logo.ico"
        
        # Setup font cho đa ngôn ngữ
        self._setup_fonts()
        
        # Setup style - IMPROVED
        self.root.configure(bg="#f5f5f5")
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 10))
        style.configure('TLabelframe', background='#f5f5f5', font=('Segoe UI', 10, 'bold'))
        style.configure('TLabelframe.Label', foreground='#2c3e50', font=('Segoe UI', 10, 'bold'))
        style.configure('TButton', font=('Segoe UI', 10), padding=8)
        style.map('TButton',
                 background=[('active', '#3498db'), ('!active', '#ecf0f1')],
                 foreground=[('active', 'white'), ('!active', '#2c3e50')])
        style.configure('TNotebook', background='#ecf0f1', borderwidth=0)
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Segoe UI', 10, 'bold'))
        
        # Tạo notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Setup (luôn hiển thị)
        self.setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_tab, text="📋 Chuẩn bị")
        self._create_setup_tab()
        
        # Tab 2: File Manager (luôn hiển thị)
        self.files_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.files_tab, text="📚 Quản Lý File")
        self._create_files_manager_tab()
        
        # Tab Results (luôn hiển thị)
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="📊 Kết quả")
        self._create_results_tab()
        
        # Xử lý khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Tabs động (chỉ tạo khi cần)
        self.quiz_tab = None
        self.voice_quiz_tab = None
        
        # 🚀 Flag để dừng thread quiz cũ khi bắt đầu quiz mới
        self.quiz_active = False
        
        # Load file/sheet đã lưu
        self._load_previous_session()
    
    # ===== FONT SETUP =====
    
    def _setup_fonts(self):
        """Setup font chữ cho đa ngôn ngữ"""
        try:
            # Font cho Latin (English)
            self.font_latin = tkFont.Font(
                family="DejaVuSans",
                size=11,
                weight="normal"
            )
            
            # Font cho Trung/Hàn/Nhật
            self.font_cjk = tkFont.Font(
                family="SamsungGothicKorean",
                size=11,
                weight="normal"
            )
            
            # Font lớn cho title
            self.font_title = tkFont.Font(
                family="DejaVuSans",
                size=13,
                weight="bold"
            )
            
            print("✅ Font chữ đã setup:")
            print(f"   - Latin: DejaVuSans")
            print(f"   - CJK: SamsungGothicKorean")
        
        except Exception as e:
            print(f"⚠️ Lỗi setup font: {e}")
            # Fallback
            self.font_latin = tkFont.Font(size=11)
            self.font_cjk = tkFont.Font(size=11)
            self.font_title = tkFont.Font(size=13, weight="bold")
    
    def _load_settings(self):
        """Load user settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Không đọc được settings: {e}")
        return {
            "last_file": "", 
            "last_sheet": "", 
            "last_mic": 0,
            "last_camera": 0,
            "quiz_type": "meaning",
            "test_mode": 1,
            "start_question": 1,
            "end_question": 10,
            "shuffle": True,
            "en_voice": "female",
            "ja_voice": "female"
        }
    
    def _save_settings(self):
        """Save user settings to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Không lưu được settings: {e}")
    
    def _load_previous_session(self):
        """Load file and sheet from previous session"""
        try:
            # Load file & sheet
            last_file = self.user_settings.get("last_file", "")
            if last_file and Path(last_file).exists():
                self.selected_file = last_file
                self.file_label.config(text=f"✓ {Path(last_file).name}", foreground="green")
                
                wb = openpyxl.load_workbook(last_file, data_only=True)
                self.sheet_combo['values'] = wb.sheetnames
                
                last_sheet = self.user_settings.get("last_sheet", "")
                if last_sheet in wb.sheetnames:
                    self.sheet_combo.set(last_sheet)
                elif wb.sheetnames:
                    self.sheet_combo.current(0)
                
                print(f"✅ Đã load session trước: {Path(last_file).name} → {last_sheet}")
            
            # Load quiz settings
            self.quiz_type_var.set(self.user_settings.get("quiz_type", "meaning"))
            self.test_mode_var.set(self.user_settings.get("test_mode", 1))
            # 🔧 Cập nhật self.test_mode khi load (vì .set() không gọi callback)
            self.test_mode = self.user_settings.get("test_mode", 1)
            self.start_question_var.set(self.user_settings.get("start_question", 1))
            self.end_question_var.set(self.user_settings.get("end_question", 10))
            self.shuffle_var.set(self.user_settings.get("shuffle", True))
            self.en_voice_var.set(self.user_settings.get("en_voice", "female"))
            self.ja_voice_var.set(self.user_settings.get("ja_voice", "female"))
            self.faster_feedback_var.set(self.user_settings.get("faster_feedback", False))
            self.quiz_mode_var.set(self.user_settings.get("quiz_mode", "normal"))
            
        except Exception as e:
            print(f"⚠️ Không load được session trước: {e}")
    
    def _create_setup_tab(self):
        """Tab chuẩn bị - 2 COLUMN LAYOUT"""
        # Main container
        main_container = ttk.Frame(self.setup_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # LEFT COLUMN - Cài đặt (60% width)
        left_col = ttk.Frame(main_container)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # File Selection
        file_frame = ttk.LabelFrame(left_col, text="📁 File & Sheet", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_frame, text="Chọn File Excel", 
                  command=self.select_excel_file, width=20).grid(row=0, column=0, padx=5, pady=3)
        
        self.file_label = ttk.Label(file_frame, text="Chưa chọn", foreground="gray", font=("Segoe UI", 9))
        self.file_label.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(file_frame, text="Sheet:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        self.sheet_combo = ttk.Combobox(file_frame, state="readonly", width=35)
        self.sheet_combo.grid(row=2, column=0, columnspan=2, pady=3, sticky=tk.EW)
        
        # Microphone Settings
        mic_frame = ttk.LabelFrame(left_col, text="🎙️ Microphone", padding=10)
        mic_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mic_combo = ttk.Combobox(mic_frame, state="readonly", width=35)
        self.mic_combo.pack(fill=tk.X, pady=(0, 5))
        
        # Load microphones
        self.mic_device_indices = []
        try:
            from voice_quiz_v2 import VoiceManager
            mics = VoiceManager.list_microphones()
            mic_names = []
            for idx, name in mics:
                self.mic_device_indices.append(idx)
                mic_names.append(f"{name}")
            
            self.mic_combo['values'] = mic_names
            saved_mic_idx = self.user_settings.get("last_mic", 0)
            if saved_mic_idx < len(mic_names):
                self.mic_combo.current(saved_mic_idx)
            elif mic_names:
                self.mic_combo.current(0)
        except Exception as e:
            self.mic_combo['values'] = ["(Mặc định)"]
            self.mic_device_indices = [None]
            self.mic_combo.current(0)
        
        # Test button
        test_frame = ttk.Frame(mic_frame)
        test_frame.pack(fill=tk.X)
        
        ttk.Button(test_frame, text="🎙️ Test (5s)", command=self.test_microphone, width=12).pack(side=tk.LEFT)
        self.test_mic_bar = ttk.Progressbar(test_frame, length=150, mode='determinate', maximum=100)
        self.test_mic_bar.pack(side=tk.LEFT, padx=5)
        self.test_mic_label = ttk.Label(test_frame, text="", foreground="gray", font=("Segoe UI", 8))
        self.test_mic_label.pack(side=tk.LEFT)
        
        # Camera Settings (for Discord photo)
        cam_frame = ttk.LabelFrame(left_col, text="📷 Camera (Discord)", padding=10)
        cam_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.camera_combo = ttk.Combobox(cam_frame, state="readonly", width=35)
        self.camera_combo.pack(fill=tk.X, pady=(0, 5))
        
        # Load cameras
        self.camera_indices = []
        try:
            import cv2
            camera_names = []
            for i in range(10):  # Check first 10 camera indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.camera_indices.append(i)
                    camera_names.append(f"Camera {i}")
                    cap.release()
            
            if camera_names:
                self.camera_combo['values'] = camera_names
                saved_cam_idx = self.user_settings.get("last_camera", 0)
                if saved_cam_idx < len(camera_names):
                    self.camera_combo.current(saved_cam_idx)
                else:
                    self.camera_combo.current(0)
            else:
                self.camera_combo['values'] = ["(Không có camera)"]
                self.camera_indices = []
                self.camera_combo.current(0)
        except Exception as e:
            print(f"⚠️ Lỗi load camera: {e}")
            self.camera_combo['values'] = ["(Không có camera)"]
            self.camera_indices = []
            self.camera_combo.current(0)
        
        ttk.Label(cam_frame, text="Ảnh sẽ được gửi kèm kết quả lên Discord", 
                 font=("Segoe UI", 8), foreground="gray").pack(anchor=tk.W)
        
        # Quiz Settings
        quiz_frame = ttk.LabelFrame(left_col, text="⚙️ Cài đặt Quiz", padding=10)
        quiz_frame.pack(fill=tk.X, pady=(0, 10))  # Không expand để không chiếm hết chỗ
        
        # Quiz type
        ttk.Label(quiz_frame, text="Loại:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.quiz_type_var = tk.StringVar(value="meaning")
        for text, value in [("Nghĩa từ", "meaning"), ("Dịch câu", "example"), ("VN→EN", "vietnamese")]:
            ttk.Radiobutton(quiz_frame, text=text, variable=self.quiz_type_var, value=value).pack(anchor=tk.W, pady=1)
        
        ttk.Separator(quiz_frame, orient='horizontal').pack(fill=tk.X, pady=8)
        
        # Range - Chọn từ câu nào đến câu nào
        ttk.Label(quiz_frame, text="Phạm vi câu hỏi:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        range_frame = ttk.Frame(quiz_frame)
        range_frame.pack(fill=tk.X, pady=5)
        ttk.Label(range_frame, text="Từ:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.start_question_var = tk.IntVar(value=1)
        self.start_spin = ttk.Spinbox(range_frame, from_=1, to=1000, width=6, textvariable=self.start_question_var)
        self.start_spin.pack(side=tk.LEFT, padx=3)
        ttk.Label(range_frame, text="Đến:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10,0))
        self.end_question_var = tk.IntVar(value=10)
        self.end_spin = ttk.Spinbox(range_frame, from_=1, to=1000, width=6, textvariable=self.end_question_var)
        self.end_spin.pack(side=tk.LEFT, padx=3)
        
        # Shuffle
        self.shuffle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(quiz_frame, text="🔀 Trộn câu hỏi", variable=self.shuffle_var).pack(anchor=tk.W, pady=3)
        
        # RIGHT COLUMN - Voice Quiz (40% width)
        right_col = ttk.Frame(main_container)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(10, 0))
        
        # Voice Mode
        mode_frame = ttk.LabelFrame(right_col, text="🎤 Chế độ Voice Quiz", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.test_mode_var = tk.IntVar(value=1)
        ttk.Radiobutton(mode_frame, text="Mode 1: Bot đọc VN → User nói EN/CN/JP", 
                       variable=self.test_mode_var, value=1, command=self._on_test_mode_change).pack(anchor=tk.W, pady=3)
        ttk.Radiobutton(mode_frame, text="Mode 2: Bot đọc EN/CN/JP → User nói VN", 
                       variable=self.test_mode_var, value=2, command=self._on_test_mode_change).pack(anchor=tk.W, pady=3)
        
        # Voice Settings - Di chuyển từ left column
        voice_frame = ttk.LabelFrame(right_col, text="🎙️ Giọng đọc & Tùy chọn", padding=10)
        voice_frame.pack(fill=tk.X, pady=(0, 10))
        
        # English voice
        en_voice_frame = ttk.Frame(voice_frame)
        en_voice_frame.pack(fill=tk.X, pady=3)
        ttk.Label(en_voice_frame, text="English:", font=("Segoe UI", 9), width=10).pack(side=tk.LEFT)
        self.en_voice_var = tk.StringVar(value="female")
        ttk.Radiobutton(en_voice_frame, text="👩 Nữ (Joanna)", variable=self.en_voice_var, value="female").pack(side=tk.LEFT, padx=3)
        ttk.Radiobutton(en_voice_frame, text="👨 Nam (Matthew)", variable=self.en_voice_var, value="male").pack(side=tk.LEFT, padx=3)
        
        # Japanese voice
        ja_voice_frame = ttk.Frame(voice_frame)
        ja_voice_frame.pack(fill=tk.X, pady=3)
        ttk.Label(ja_voice_frame, text="日本語:", font=("Segoe UI", 9), width=10).pack(side=tk.LEFT)
        self.ja_voice_var = tk.StringVar(value="female")
        ttk.Radiobutton(ja_voice_frame, text="👩 Nữ (Mizuki)", variable=self.ja_voice_var, value="female").pack(side=tk.LEFT, padx=3)
        ttk.Radiobutton(ja_voice_frame, text="👨 Nam (Takumi)", variable=self.ja_voice_var, value="male").pack(side=tk.LEFT, padx=3)
        
        ttk.Separator(voice_frame, orient='horizontal').pack(fill=tk.X, pady=8)
        
        # Quiz mode
        ttk.Label(voice_frame, text="📚 Chế độ Quiz:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.quiz_mode_var = tk.StringVar(value="normal")
        ttk.Radiobutton(voice_frame, text="📖 Normal - Toàn bộ từ", 
                       variable=self.quiz_mode_var, value="normal").pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(voice_frame, text="🎯 Practice - Ôn tập từ yếu", 
                       variable=self.quiz_mode_var, value="practice").pack(anchor=tk.W, pady=2)
        
        # Faster Feedback Option
        self.faster_feedback_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(voice_frame, text="⚡ Phản hồi nhanh (chỉ text, bỏ TTS)", 
                       variable=self.faster_feedback_var).pack(anchor=tk.W, pady=5)
        
        # Start Buttons
        button_frame = ttk.LabelFrame(right_col, text="🚀 Bắt đầu", padding=15)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="▶️ KIỂM TRA THƯỜNG", 
                  command=self.start_quiz, width=25).pack(pady=5)
        ttk.Button(button_frame, text="🎤 VOICE QUIZ", 
                  command=self.start_voice_quiz, width=25).pack(pady=5)
        
        # Info
        info_frame = ttk.Frame(right_col)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(10,0))
        
        info_text = tk.Text(info_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 9), 
                           bg="#f9f9f9", relief=tk.FLAT, padx=10, pady=10)
        info_text.pack(fill=tk.BOTH, expand=True)
        info_text.insert(tk.END, "💡 HƯỚNG DẪN:\n\n")
        info_text.insert(tk.END, "1. Chọn file Excel và sheet\n")
        info_text.insert(tk.END, "2. Test microphone trước khi bắt đầu\n")
        info_text.insert(tk.END, "3. Chọn loại quiz và số câu\n")
        info_text.insert(tk.END, "4. Bấm 'Voice Quiz' để bắt đầu\n\n")
        info_text.insert(tk.END, "⚡ Nhận dạng giọng nói tức thì!")
        info_text.config(state=tk.DISABLED)
    
    def _create_quiz_tab(self):
        """Tab kiểm tra thường"""
        question_frame = ttk.LabelFrame(self.quiz_tab, text="❓ Câu hỏi", padding=10)
        question_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.progress_label = ttk.Label(question_frame, text="")
        self.progress_label.pack(anchor=tk.W)
        self.progress_bar = ttk.Progressbar(question_frame, length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.question_text = scrolledtext.ScrolledText(question_frame, height=6, width=60, font=("Arial", 12), wrap=tk.WORD)
        self.question_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.question_text.config(state=tk.DISABLED)
        
        answer_frame = ttk.LabelFrame(self.quiz_tab, text="💬 Trả lời", padding=10)
        answer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(answer_frame, text="Nhập câu trả lời:").pack(anchor=tk.W)
        self.answer_entry = ttk.Entry(answer_frame, width=60, font=("Arial", 11))
        self.answer_entry.pack(fill=tk.X, pady=5)
        self.answer_entry.bind('<Return>', lambda e: self.submit_answer())
        
        button_frame = ttk.Frame(answer_frame)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="💡 Gợi ý", command=self.show_hint, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✅ Nộp bài", command=self.submit_answer, width=15).pack(side=tk.LEFT, padx=5)
        
        feedback_frame = ttk.LabelFrame(self.quiz_tab, text="📝 Phản hồi", padding=10)
        feedback_frame.pack(fill=tk.X, padx=10, pady=10)
        self.feedback_text = scrolledtext.ScrolledText(feedback_frame, height=3, width=60, font=("Arial", 10), wrap=tk.WORD)
        self.feedback_text.pack(fill=tk.BOTH, expand=True)
        self.feedback_text.config(state=tk.DISABLED)
    
    def _create_voice_quiz_tab(self):
        """Tab Voice Quiz - REDESIGNED"""
        # Top: Info & Progress (compact)
        top_frame = ttk.Frame(self.voice_quiz_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="🎤 Trung tâm giáo dục quốc tế Việt Trung Nhật Anh | 💬 Zalo: 0986183806", 
                 font=("Arial", 9), foreground="gray").pack(anchor=tk.W)
        
        # Progress bar
        progress_frame = ttk.Frame(self.voice_quiz_tab)
        progress_frame.pack(fill=tk.X, padx=10, pady=(0,5))
        self.voice_progress_label = ttk.Label(progress_frame, text="Câu 1/10", font=("Arial", 9, "bold"))
        self.voice_progress_label.pack(anchor=tk.W)
        self.voice_progress_bar = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.voice_progress_bar.pack(fill=tk.X, pady=3)
        
        # Main content - 2 columns
        main_container = ttk.Frame(self.voice_quiz_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # LEFT: Question
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(left_frame, text="❓ Câu hỏi", font=("Arial", 11, "bold"), foreground="#2c3e50").pack(anchor=tk.W, pady=(0,5))
        self.voice_question_text = scrolledtext.ScrolledText(left_frame, height=10, width=40, 
                                                             font=("Arial", 12, "bold"), wrap=tk.WORD,
                                                             bg="#f9f9f9", relief=tk.FLAT)
        self.voice_question_text.pack(fill=tk.BOTH, expand=True)
        self.voice_question_text.config(state=tk.DISABLED)
        
        # 🎨 GIF Nhân vật động dưới câu hỏi
        gif_frame = ttk.Frame(left_frame)
        gif_frame.pack(fill=tk.X, pady=10)
        self.voice_gif_label = tk.Label(gif_frame, bg="#f9f9f9")
        self.voice_gif_label.pack()
        
        # Lưu frames + index animation
        self.gif_frames = []
        self.gif_frame_index = [0]
        self.gif_animating = [False]
        
        # RIGHT: Answer & Feedback
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Mic status
        ttk.Label(right_frame, text="🎙️ Câu trả lời", font=("Arial", 11, "bold"), foreground="#2c3e50").pack(anchor=tk.W, pady=(0,5))
        
        mic_frame = ttk.Frame(right_frame)
        mic_frame.pack(fill=tk.X, pady=5)
        self.mic_status_label = ttk.Label(mic_frame, text="🎙️ Mic: Sẵn sàng", font=("Arial", 9), foreground="green")
        self.mic_status_label.pack(side=tk.LEFT)
        self.mic_level_bar = ttk.Progressbar(mic_frame, length=100, mode='determinate', maximum=100)
        self.mic_level_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # User answer
        self.voice_answer_text = scrolledtext.ScrolledText(right_frame, height=3, width=30, 
                                                           font=("Arial", 10), wrap=tk.WORD,
                                                           bg="#e8f4f8", relief=tk.FLAT)
        self.voice_answer_text.pack(fill=tk.X, pady=5)
        self.voice_answer_text.config(state=tk.DISABLED)
        
        # Feedback
        ttk.Label(right_frame, text="💬 Feedback", font=("Arial", 11, "bold"), foreground="#2c3e50").pack(anchor=tk.W, pady=(10,5))
        self.voice_feedback_text = scrolledtext.ScrolledText(right_frame, height=5, width=30, 
                                                             font=("Arial", 10), wrap=tk.WORD,
                                                             bg="#f0f8f0", relief=tk.FLAT)
        self.voice_feedback_text.pack(fill=tk.BOTH, expand=True)
        self.voice_feedback_text.config(state=tk.DISABLED)
        
        # Buttons at bottom
        button_frame = ttk.Frame(self.voice_quiz_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="⏭️ CÂU TIẾP", command=self.voice_next_question, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ DỪNG", command=self.voice_stop_quiz, width=20).pack(side=tk.LEFT, padx=5)
    
    def _create_files_manager_tab(self):
        """Tab Quản Lý File - Manage multiple Excel files"""
        main_frame = ttk.Frame(self.files_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="📚 Quản Lý Tập Tin Từ Vựng", font=("Segoe UI", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="➕ Thêm File", command=self._add_file_to_manager, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Xóa", command=self._remove_file_from_manager, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⭐ Đặt làm Mặc định", command=self._set_default_file, width=15).pack(side=tk.LEFT, padx=5)
        
        # Files list frame
        list_frame = ttk.LabelFrame(main_frame, text="Danh sách file", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar + Listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 10))
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Bind double-click to load file
        self.files_listbox.bind("<Double-Button-1>", self._load_file_from_manager)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin", padding=10)
        info_frame.pack(fill=tk.X)
        
        self.files_info_label = ttk.Label(info_frame, text="(Chọn file để xem chi tiết)", foreground="gray")
        self.files_info_label.pack(anchor=tk.W)
        
        # Load file list
        self._refresh_files_list()
    
    def _add_file_to_manager(self):
        """Add new Excel file to manager - copy to app folder"""
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        
        if file_path:
            from shutil import copy2
            app_folder = Path(__file__).parent
            file_name = Path(file_path).name
            dest_path = app_folder / file_name
            
            # Copy file to app folder
            try:
                if str(dest_path) != file_path:
                    copy2(file_path, dest_path)
                    self._show_info(f"✅ Đã sao chép file vào thư mục app: {file_name}")
                else:
                    self._show_info(f"✅ File đã có trong thư mục app")
            except Exception as e:
                self._show_error(f"❌ Lỗi khi sao chép file:\n{e}")
                return
            
            # Load file
            self.selected_file = str(dest_path)
            self.file_label.config(text=file_name, foreground="green")
            self.user_settings["last_file"] = str(dest_path)
            self._save_settings()
            
            # Load sheets
            try:
                from openpyxl import load_workbook
                wb = load_workbook(str(dest_path), data_only=True)
                sheets = wb.sheetnames
                self.sheet_combo['values'] = sheets
                if sheets:
                    self.sheet_combo.current(0)
                    self.user_settings["last_sheet"] = sheets[0]
                    self._save_settings()
                
                self._refresh_files_list()
            except Exception as e:
                self._show_error(f"❌ Lỗi khi tải file:\n{e}")
    
    def _remove_file_from_manager(self):
        """Remove file from recently used or mark as not favorite"""
        selection = self.files_listbox.curselection()
        if not selection:
            self._show_error("Vui lòng chọn file để xóa khỏi danh sách")
            return
        
        item = self.files_listbox.get(selection[0])
        # Remove the star marker if present
        file_path = item.replace("⭐ ", "").strip()
        
        # Clear as default if it's the default file
        if self.user_settings.get("last_file", "").endswith(file_path):
            self.user_settings["last_file"] = ""
            self._save_settings()
        
        self._refresh_files_list()
        self._show_info(f"✅ Đã xóa khỏi danh sách: {file_path}")
    
    def _set_default_file(self):
        """Set selected file as default"""
        selection = self.files_listbox.curselection()
        if not selection:
            self._show_error("Vui lòng chọn file")
            return
        
        item = self.files_listbox.get(selection[0])
        file_name = item.replace("⭐ ", "").strip()
        
        app_folder = Path(__file__).parent
        data_folder = app_folder / "data"
        
        # Check if file exists in app folder or data folder
        file_path = app_folder / file_name
        if not file_path.exists():
            file_path = data_folder / file_name
        
        if file_path.exists():
            self.user_settings["last_file"] = str(file_path)
            self._save_settings()
            self._refresh_files_list()
            self._show_info(f"✅ Đặt mặc định: {file_name}")
        else:
            self._show_error(f"❌ Không tìm thấy file: {file_name}")
    
    def _load_file_from_manager(self, event=None):
        """Load file from manager (app folder or data folder)"""
        selection = self.files_listbox.curselection()
        if not selection:
            return
        
        item = self.files_listbox.get(selection[0])
        file_name = item.replace("⭐ ", "").strip()
        
        app_folder = Path(__file__).parent
        data_folder = app_folder / "data"
        
        # Check if file exists in app folder or data folder
        file_path = app_folder / file_name
        if not file_path.exists():
            file_path = data_folder / file_name
        
        if not file_path.exists():
            self._show_error(f"❌ Không tìm thấy file: {file_name}")
            return
        
        try:
            self.selected_file = str(file_path)
            self.file_label.config(text=file_name, foreground="green")
            
            # Load sheets
            from openpyxl import load_workbook
            wb = load_workbook(str(file_path), data_only=True)
            sheets = wb.sheetnames
            self.sheet_combo['values'] = sheets
            if sheets:
                self.sheet_combo.current(0)
            
            # Save settings
            self.user_settings["last_file"] = str(file_path)
            self.user_settings["last_sheet"] = sheets[0] if sheets else ""
            self._save_settings()
            
            self._show_info(f"✅ Đã tải: {file_name}")
        except Exception as e:
            self._show_error(f"❌ Lỗi khi tải file:\n{e}")
    
    def _refresh_files_list(self):
        """Refresh the files listbox - scan only app folder and data subfolder"""
        self.files_listbox.delete(0, tk.END)
        
        app_folder = Path(__file__).parent
        data_folder = app_folder / "data"
        
        # Collect all .xlsx files from app folder and data subfolder
        all_files = {}
        
        # Scan app folder
        if app_folder.exists():
            for file_path in sorted(app_folder.glob("*.xlsx")):
                if not file_path.name.startswith("~$"):  # Skip temp files
                    all_files[file_path.name] = str(file_path)
        
        # Scan data subfolder
        if data_folder.exists():
            for file_path in sorted(data_folder.glob("*.xlsx")):
                if not file_path.name.startswith("~$"):  # Skip temp files
                    all_files[file_path.name] = str(file_path)
        
        # Get default file
        default_file = self.user_settings.get("last_file", "")
        
        # Display files in listbox
        if all_files:
            for file_name in sorted(all_files.keys()):
                full_path = all_files[file_name]
                # Check if this is the default file
                if full_path == default_file:
                    self.files_listbox.insert(tk.END, f"⭐ {file_name}")
                else:
                    self.files_listbox.insert(tk.END, file_name)
        else:
            self.files_listbox.insert(tk.END, "(Chưa có file Excel nào)")
        
        # Update info
        if default_file and Path(default_file).exists():
            file_name = Path(default_file).name
            sheet = self.user_settings.get("last_sheet", "")
            self.files_info_label.config(
                text=f"Mặc định: {file_name} | Sheet: {sheet}",
                foreground="black"
            )
        else:
            self.files_info_label.config(
                text="(Chọn file để xem chi tiết)",
                foreground="gray"
            )
    
    def _create_results_tab(self):
        """Tab Results"""
        button_frame = ttk.Frame(self.results_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="💾 Lưu kết quả", command=self.save_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="� Xem kết quả cũ", command=self.load_previous_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="�🔄 Kiểm tra lại", command=self.restart_quiz).pack(side=tk.LEFT, padx=5)
        
        self.results_text = scrolledtext.ScrolledText(self.results_tab, font=("Arial", 10), wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.results_text.config(state=tk.DISABLED)
    
    # ===== METHODS =====
    
    def select_excel_file(self):
        """Chọn file Excel"""
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel", 
            filetypes=[("Excel", "*.xlsx"), ("All", "*.*")],
            initialdir=Path(self.user_settings.get("last_file", "")).parent if self.user_settings.get("last_file") else None
        )
        if file_path:
            # ✨ Auto-detect và convert nếu cần
            from file_converter import convert_file_auto, is_template_format
            import openpyxl
            
            try:
                # Kiểm tra format
                wb_temp = openpyxl.load_workbook(file_path)
                ws_temp = wb_temp.active
                
                if not is_template_format(ws_temp):
                    # Hỏi user có muốn convert không
                    response = messagebox.askyesno(
                        "Format không chuẩn",
                        f"⚠️ File '{Path(file_path).name}' không đúng format chuẩn.\n\n"
                        "Format chuẩn: Word | Meaning | Example EN | Example VI\n\n"
                        "🔄 Bạn có muốn tự động chuyển đổi sang format chuẩn không?"
                    )
                    
                    if response:
                        # Convert file
                        success, message, output_path = convert_file_auto(file_path)
                        
                        if success and output_path:
                            messagebox.showinfo("Thành công", message)
                            file_path = output_path  # Dùng file đã convert
                        else:
                            messagebox.showerror("Lỗi convert", message)
                            return
                    else:
                        messagebox.showwarning("Cảnh báo", 
                            "⚠️ File không chuẩn có thể gây lỗi khi học!\n\n"
                            "Bạn vẫn có thể thử tiếp, nhưng nên convert về format chuẩn.")
                
                wb_temp.close()
            except Exception as e:
                print(f"⚠️ Lỗi kiểm tra format: {e}")
            
            # Tiếp tục load file bình thường
            self.selected_file = file_path
            self.file_label.config(text=f"✓ {Path(file_path).name}", foreground="green")
            
            # Lưu settings
            self.user_settings["last_file"] = file_path
            self._save_settings()
            
            try:
                wb = openpyxl.load_workbook(file_path, data_only=True)
                self.sheet_combo['values'] = wb.sheetnames
                
                # Load sheet đã lưu
                saved_sheet = self.user_settings.get("last_sheet", "")
                if saved_sheet in wb.sheetnames:
                    self.sheet_combo.set(saved_sheet)
                elif wb.sheetnames:
                    self.sheet_combo.current(0)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi đọc file:\n{e}")
    
    def _read_excel_data(self, sheet_name):
        """Đọc dữ liệu từ Excel"""
        try:
            wb = openpyxl.load_workbook(self.selected_file, data_only=True)
            ws = wb[sheet_name]
            
            # Kiểm tra header để xác định format
            header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
            has_no_column = False
            word_col = 0
            meaning_col = 1
            example_en_col = 2
            example_vi_col = 3
            
            # Nếu cột đầu tiên là "No." hoặc số → có cột số thứ tự
            if header_row and (str(header_row[0]).lower() in ["no.", "no", "#", "stt"]):
                has_no_column = True
                word_col = 1
                meaning_col = 2
                example_en_col = 3
                example_vi_col = 4
            
            data = []
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if not row or not row[word_col]:
                    continue
                if len(row) < (example_vi_col + 1):
                    continue
                
                # Lưu số thứ tự thực tế trong Excel (row_idx - 1 vì header ở row 1)
                item = {
                    "id": len(data) + 1,
                    "excel_row": row_idx - 1,  # ✨ Số thứ tự trong Excel (1, 2, 3...)
                    "word": str(row[word_col]).strip() if row[word_col] else "",
                    "meaning": str(row[meaning_col]).strip() if row[meaning_col] else "",
                    "example_en": str(row[example_en_col]).strip() if row[example_en_col] else "",
                    "example_vi": str(row[example_vi_col]).strip() if row[example_vi_col] else ""
                }
                
                if item["word"] and item["meaning"]:
                    data.append(item)
            
            if not data:
                messagebox.showerror("Lỗi", "❌ Không có dữ liệu hợp lệ!")
                return []
            
            return data
        except Exception as e:
            messagebox.showerror("Lỗi", f"❌ Lỗi khi đọc Excel:\n{str(e)}")
            return []
    
    # ===== QUIZ THƯỜNG =====
    
    def start_quiz(self):
        """Bắt đầu kiểm tra thường"""
        if not self.selected_file:
            messagebox.showerror("Lỗi", "❌ Vui lòng chọn file Excel!")
            return
        
        # Lưu settings
        self.user_settings["last_sheet"] = self.sheet_combo.get()
        self.user_settings["quiz_type"] = self.quiz_type_var.get()
        self.user_settings["start_question"] = self.start_question_var.get()
        self.user_settings["end_question"] = self.end_question_var.get()
        self.user_settings["shuffle"] = self.shuffle_var.get()
        self._save_settings()
        
        self.data = self._read_excel_data(self.sheet_combo.get())
        if not self.data:
            return
        
        self.quiz_type_str = self.quiz_type_var.get()
        
        # Xử lý range - lấy tất cả câu trong khoảng
        start_idx = self.start_question_var.get() - 1
        end_idx = self.end_question_var.get()
        
        if start_idx < 0:
            start_idx = 0
        if end_idx > len(self.data):
            end_idx = len(self.data)
        if start_idx >= end_idx:
            messagebox.showerror("Lỗi", f"❌ Khoảng không hợp lệ!\n\nTổng số câu: {len(self.data)}")
            return
        
        selected_data = self.data[start_idx:end_idx]
        
        self.quiz_engine = QuizEngine(selected_data, language="English")
        
        if self.shuffle_var.get():
            self.quiz_engine.shuffle_questions(len(selected_data))  # Shuffle tất cả
        else:
            self.quiz_engine.questions = selected_data  # Lấy tất cả trong range
        
        self.quiz_engine.quiz_type = self.quiz_type_str
        
        self.current_question_idx = 0
        self.attempt = 1
        self.quiz_results = []
        
        # Tạo tab quiz nếu chưa có
        if self.quiz_tab is None:
            self.quiz_tab = ttk.Frame(self.notebook)
            self.notebook.insert(1, self.quiz_tab, text="🎯 Kiểm tra")
            self._create_quiz_tab()
        
        self.notebook.select(1)
        self.display_question()
    
    def display_question(self):
        """Hiển thị câu hỏi"""
        if self.current_question_idx >= len(self.quiz_engine.questions):
            self.show_results()
            return
        
        question = self.quiz_engine.questions[self.current_question_idx]
        question_text = self.quiz_engine.format_question(question, self.quiz_type_str)
        
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        
        # Chọn font phù hợp
        font = self._choose_font(question_text)
        self.question_text.config(font=font)
        
        self.question_text.insert(tk.END, question_text)
        self.question_text.config(state=tk.DISABLED)
        
        current = self.current_question_idx + 1
        total = len(self.quiz_engine.questions)
        self.progress_label.config(text=f"Câu {current}/{total} (Lần {self.attempt}/3)")
        self.progress_bar['value'] = (current / total) * 100
        
        self.answer_entry.delete(0, tk.END)
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete(1.0, tk.END)
        self.feedback_text.config(state=tk.DISABLED)
        
        self.answer_entry.focus()
    
    def submit_answer(self):
        """Nộp câu trả lời"""
        user_answer = self.answer_entry.get().strip()
        if not user_answer:
            messagebox.showwarning("Cảnh báo", "❌ Vui lòng nhập câu trả lời!")
            return
        
        question = self.quiz_engine.questions[self.current_question_idx]
        correct_answer = question.get("meaning") if self.quiz_type_str == "meaning" else \
                        question.get("example_en") if self.quiz_type_str == "example" else \
                        question.get("example_vi")
        
        is_correct, feedback, score, is_semantic = self.quiz_engine.check_answer(user_answer, correct_answer, self.attempt)
        
        question_num = question.get("excel_row", self.current_question_idx + 1)  # Số thứ tự từ Excel
        self.quiz_results.append({
            "question_num": question_num,  # ✨ Số thứ tự từ Excel
            "question": question.get("word"),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "score": score,
            "attempt": self.attempt
        })
        
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete(1.0, tk.END)
        semantic_note = " (✓ Đúng về mặt ý nghĩa)" if is_semantic else ""
        self.feedback_text.insert(tk.END, f"{feedback}{semantic_note}\n\n💡 Đáp án đúng: {correct_answer}")
        self.feedback_text.config(state=tk.DISABLED)
        
        if is_correct or self.attempt >= 3:
            self.root.after(2000, self.next_question)
        else:
            self.attempt += 1
            self.display_question()
    
    def next_question(self):
        """Câu tiếp theo"""
        self.current_question_idx += 1
        self.attempt = 1
        self.display_question()
    
    def show_hint(self):
        """Gợi ý"""
        question = self.quiz_engine.questions[self.current_question_idx]
        hint = self.quiz_engine.get_hint(question)
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete(1.0, tk.END)
        self.feedback_text.insert(tk.END, f"💡 Gợi ý: {hint}")
        self.feedback_text.config(state=tk.DISABLED)
    
    # ===== VOICE QUIZ =====
    
    def start_voice_quiz(self):
        """Bắt đầu Voice Quiz"""
        if not self.selected_file:
            messagebox.showerror("Lỗi", "❌ Vui lòng chọn file Excel!")
            return
        
        # Lưu ALL settings
        self.user_settings["last_sheet"] = self.sheet_combo.get()
        self.user_settings["last_mic"] = self.mic_combo.current()
        self.user_settings["last_camera"] = self.camera_combo.current()
        self.user_settings["quiz_type"] = self.quiz_type_var.get()
        self.user_settings["test_mode"] = self.test_mode_var.get()
        self.user_settings["start_question"] = self.start_question_var.get()
        self.user_settings["end_question"] = self.end_question_var.get()
        self.user_settings["shuffle"] = self.shuffle_var.get()
        self.user_settings["en_voice"] = self.en_voice_var.get()
        self.user_settings["ja_voice"] = self.ja_voice_var.get()
        self.user_settings["faster_feedback"] = self.faster_feedback_var.get()
        self.user_settings["quiz_mode"] = self.quiz_mode_var.get()
        self._save_settings()
        
        # 🎯 Check if Practice Mode
        quiz_mode = self.quiz_mode_var.get()
        
        if quiz_mode == "practice":
            # Practice Mode: Load weak words from database
            try:
                language = self._detect_language_from_file(Path(self.selected_file).name)
                weak_words = self.study_db.get_weak_words(language)
                
                if not weak_words:
                    messagebox.showinfo("Thông báo", f"✅ Tuyệt vời!\n\nKhông có từ nào cần ôn tập trong {language}.\n\nTất cả từ đều đã học tốt! 🎉")
                    return
                
                # Convert weak words to quiz format
                selected_data = []
                for weak_word_dict in weak_words:
                    # Format: {"word": word_text, "meaning": meaning, "language": lang, "wrong_count": X, "last_reviewed": timestamp}
                    selected_data.append({
                        "word": weak_word_dict["word"],
                        "meaning": f"[{weak_word_dict['wrong_count']}x sai] {weak_word_dict['word']}",  # Show mistake count
                        "language": weak_word_dict["language"],
                        "wrong_count": weak_word_dict["wrong_count"],
                        "last_reviewed": weak_word_dict["last_reviewed"],
                        "word_id": weak_word_dict["word_id"]
                    })
                
                num_questions = len(selected_data)
                mode_text = f"🎯 Ôn tập từ yếu: {num_questions} từ cần học lại"
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"❌ Lỗi khi tải từ yếu:\n{e}")
                return
        else:
            # Normal Mode: Load from file
            self.data = self._read_excel_data(self.sheet_combo.get())
            if not self.data:
                return
            
            # Xử lý range selection - lấy tất cả câu trong khoảng
            start_idx = self.start_question_var.get() - 1  # Convert to 0-based
            end_idx = self.end_question_var.get()
            
            # Validate range
            if start_idx < 0:
                start_idx = 0
            if end_idx > len(self.data):
                end_idx = len(self.data)
            if start_idx >= end_idx:
                messagebox.showerror("Lỗi", f"❌ Khoảng không hợp lệ!\nCâu bắt đầu phải < câu kết thúc.\n\nTổng số câu: {len(self.data)}")
                return
            
            # Slice data theo range - lấy TẤT CẢ
            selected_data = self.data[start_idx:end_idx]
            num_questions = len(selected_data)
            
            if self.shuffle_var.get():
                mode_text = f"🔀 Trộn {num_questions} câu"
            else:
                mode_text = f"📋 Theo thứ tự: câu {start_idx+1}-{end_idx}"
        
        self.quiz_type_str = self.quiz_type_var.get()
        self.quiz_engine = QuizEngine(selected_data, language="English")
        
        # Shuffle hoặc theo thứ tự (chỉ cho Normal mode)
        if quiz_mode == "normal":
            if self.shuffle_var.get():
                self.quiz_engine.shuffle_questions(num_questions)
            else:
                self.quiz_engine.questions = selected_data  # Lấy tất cả
        else:
            # Practice mode: không shuffle, toàn bộ weak words
            self.quiz_engine.questions = selected_data
        
        self.quiz_engine.quiz_type = self.quiz_type_str
        
        self.current_question_idx = 0
        self.quiz_results = []
        self.instruction_shown = False  # Reset instruction cho quiz mới
        self.quiz_mode = quiz_mode  # Store mode for use in quiz
        
        # 🚀 Dừng quiz cũ nếu đang chạy
        self.quiz_active = False
        time.sleep(0.1)  # Cho thread cũ kịp dừng
        
        # ✅ Đánh dấu quiz mới đang chạy
        self.quiz_active = True
        
        # Tạo tab voice quiz nếu chưa có
        if self.voice_quiz_tab is None:
            self.voice_quiz_tab = ttk.Frame(self.notebook)
            self.notebook.insert(1, self.voice_quiz_tab, text="🎤 Voice Quiz")
            self._create_voice_quiz_tab()
        
        # Select voice quiz tab (index 1 vì insert vào position 1)
        self.notebook.select(1)
        
        # ⚡ KHỞI TẠO MIC 1 LẦN (như Google Voice Input)
        mic_device_index = None
        try:
            combo_idx = self.mic_combo.current()
            if combo_idx >= 0 and combo_idx < len(self.mic_device_indices):
                mic_device_index = self.mic_device_indices[combo_idx]
        except:
            pass
        
        print("\n⚡ Khởi tạo microphone...")
        # Note: VoiceManager handles microphone initialization internally
        init_success = True  # Assume success, actual errors caught during listen_to_microphone
        
        # Hiển thị thông tin
        try:
            mic_name = self.mic_combo.get()
            status = "✅ Sẵn sàng" if init_success else "⚠️ Lỗi khởi tạo"
            messagebox.showinfo("Bắt đầu", f"🎤 Voice Quiz sẽ bắt đầu!\n\n🎙️ Mic: {mic_name}\n{status}\n{mode_text}\n\n⚡ Nhận dạng sẽ tức thì (không delay)!")
        except:
            messagebox.showinfo("Bắt đầu", f"🎤 Voice Quiz sẽ bắt đầu!\n\n{mode_text}\n\n⚡ Nhận dạng sẽ tức thì!")
        
        self.voice_display_question()
    
    def voice_display_question(self):
        """Hiển thị câu hỏi voice"""
        if self.current_question_idx >= len(self.quiz_engine.questions):
            self.voice_show_results()
            return
        
        question = self.quiz_engine.questions[self.current_question_idx]
        question_num = question.get("excel_row", self.current_question_idx + 1)  # Số thứ tự từ Excel
        
        # Format câu hỏi theo Mode và quiz type (để hiển thị text)
        quiz_lang = self._get_quiz_language_code()
        lang_name = "tiếng Anh" if quiz_lang == "English" else ("tiếng Trung" if quiz_lang == "Chinese" else "tiếng Nhật")
        
        if self.test_mode == 1:
            # Mode 1: Đọc VN → User trả lời foreign
            if self.quiz_type_str == "meaning":
                meaning_vi = question.get('meaning', '')
                question_text = f"Từ có nghĩa là '{meaning_vi}' trong {lang_name} là gì?"
            elif self.quiz_type_str == "example":
                example_vi = question.get('example_vi', '')
                question_text = f"Câu '{example_vi}' dịch sang {lang_name} là gì?"
            else:  # vietnamese
                example_vi = question.get('example_vi', '')
                question_text = f"Câu '{example_vi}' dịch sang {lang_name} là gì?"
        else:
            # Mode 2: Đọc foreign → User trả lời VN
            if self.quiz_type_str == "meaning":
                word = question.get('word', '')
                question_text = f"Từ '{word}' có nghĩa tiếng Việt là gì?"
            elif self.quiz_type_str == "example":
                example_en = question.get('example_en', '')
                question_text = f"Câu '{example_en}' dịch sang tiếng Việt là gì?"
            else:  # vietnamese
                example_en = question.get('example_en', '')
                question_text = f"Câu '{example_en}' dịch sang tiếng Việt là gì?"
        
        self.voice_question_text.config(state=tk.NORMAL)
        self.voice_question_text.delete(1.0, tk.END)
        
        # Chọn font phù hợp
        font = self._choose_font(question_text)
        self.voice_question_text.config(font=font)
        
        # ✨ Hiển thị số thứ tự câu
        self.voice_question_text.insert(tk.END, f"#{question_num} ❓ {question_text}")
        
        # 🎯 In thêm thông tin từ yếu (nếu là Practice Mode)
        if hasattr(self, 'quiz_mode') and self.quiz_mode == "practice":
            wrong_count = question.get('wrong_count', 0)
            last_reviewed = question.get('last_reviewed', '')
            practice_info = f"\n\n📊 Lần sai: {wrong_count}"
            if last_reviewed:
                practice_info += f" | Lần cuối: {last_reviewed}"
            self.voice_question_text.insert(tk.END, practice_info)
        
        self.voice_question_text.config(state=tk.DISABLED)
        
        current = self.current_question_idx + 1
        total = len(self.quiz_engine.questions)
        self.voice_progress_label.config(text=f"Câu {current}/{total}")
        self.voice_progress_bar['value'] = (current / total) * 100
        
        self.voice_answer_text.config(state=tk.NORMAL)
        self.voice_answer_text.delete(1.0, tk.END)
        self.voice_answer_text.config(state=tk.DISABLED)
        
        self.voice_feedback_text.config(state=tk.NORMAL)
        self.voice_feedback_text.delete(1.0, tk.END)
        self.voice_feedback_text.config(state=tk.DISABLED)
        
        # Phát câu hỏi 2 lần + đếm ngược + lắng nghe (thread)
        Thread(target=self._process_voice_question, args=(question_text,), daemon=True).start()
    
    def _process_voice_question(self, question_text):
        """Phát 2 lần (Tiếng Việt + tiếng nước ngoài) + đếm ngược + lắng nghe + feedback (thread)"""
        # 🔒 Acquire lock để đảm bảo chỉ 1 câu hỏi xử lý tại một thời điểm
        self.voice_question_lock.acquire()
        try:
            import time
            
            # 🚀 Kiểm tra quiz vẫn đang chạy không
            if not self.quiz_active:
                print("⏹️ Quiz đã dừng, bỏ qua câu hỏi này")
                return
            # Đặt lại voice preference mỗi lần câu hỏi (phòng reset)
            # Voice preferences saved in user_settings
            
            # Detect ngôn ngữ test hiện tại để ưu tiên STT
            language_stt = self._get_stt_language()
            quiz_lang_code = self._get_quiz_language_code()
            
            print(f"🌐 Quiz Language: {quiz_lang_code}")
            print(f"🎤 STT Language: {language_stt}")
            print(f"📋 Test Mode: {self.test_mode}")
            
            # Tách câu hỏi thành phần Vietnamese và Foreign language
            import re
            
            # Lấy question object để xác định quiz type
            question = self.quiz_engine.questions[self.current_question_idx]
            
            # Xử lý tách câu hỏi theo quiz type và mode
            if self.quiz_type_str == "meaning":
                word = question.get('word', '')
                meaning_vi = question.get('meaning', '')
                foreign_part = word
                meaning_part = meaning_vi
            elif self.quiz_type_str == "example":
                example_en = question.get('example_en', '')
                example_vi = question.get('example_vi', '')
                foreign_part = example_en
                meaning_part = example_vi
            else:  # vietnamese
                example_vi = question.get('example_vi', '')
                example_en = question.get('example_en', '')
                foreign_part = example_en  # Target foreign language
                meaning_part = example_vi  # Source Vietnamese
            
            # Mode 1: Đọc Tiếng Việt (gTTS) - User trả lời bằng Foreign language
            if self.test_mode == 1:
                # Chỉ đọc hướng dẫn ở câu đầu tiên
                if not self.instruction_shown:
                    quiz_lang = self._get_quiz_language_code()
                    lang_name = "tiếng Anh" if quiz_lang == "English" else ("tiếng Trung" if quiz_lang == "Chinese" else "tiếng Nhật")
                    
                    if self.quiz_type_str == "meaning":
                        instruction = f"Hãy dịch các từ sau sang {lang_name}"
                    elif self.quiz_type_str == "example":
                        instruction = f"Hãy dịch các câu sau sang {lang_name}"
                    else:  # vietnamese
                        instruction = f"Hãy dịch các câu sau sang {lang_name}"
                    
                    print(f"📢 [Instruction] {instruction}")
                    self._start_gif_animation()
                    self.voice_manager.voice_manager.speak_google_tts(instruction, language="vi")
                    self._stop_gif_animation()
                    time.sleep(0.5)
                    self.instruction_shown = True
                
                # Đọc nội dung câu (không hướng dẫn)
                print(f"📢 [Mode 1] Đọc câu hỏi VN: {meaning_part[:60]}...")
                self._start_gif_animation()  # 🎨 Bắt đầu animate
                self.voice_manager.voice_manager.speak_google_tts(meaning_part, language="vi")
                self._stop_gif_animation()  # 🎨 Dừng animate
                time.sleep(0.3)
            
            # Mode 2: Đọc Foreign language (Polly) + Câu hỏi VN (gTTS) - User trả lời bằng Tiếng Việt
            elif self.test_mode == 2:
                # Chỉ đọc hướng dẫn ở câu đầu tiên
                if not self.instruction_shown:
                    if self.quiz_type_str == "meaning":
                        instruction = "Hãy dịch các từ sau sang tiếng Việt"
                    elif self.quiz_type_str == "example":
                        instruction = "Hãy dịch các câu sau sang tiếng Việt"
                    else:  # vietnamese
                        instruction = "Hãy dịch các câu sau sang tiếng Việt"
                    
                    print(f"📢 [Instruction] {instruction}")
                    self._start_gif_animation()
                    self.voice_manager.voice_manager.speak_google_tts(instruction, language="vi")
                    self._stop_gif_animation()
                    time.sleep(0.5)
                    self.instruction_shown = True
                
                # Xác định ngôn ngữ TTS từ quiz language
                quiz_lang = self._get_quiz_language_code()
                lang_map = {
                    "English": "en",
                    "Chinese": "zh",
                    "Japanese": "ja"
                }
                tts_lang = lang_map.get(quiz_lang, "en")
                
                # Đọc từ/câu tiếng nước ngoài
                # Dùng Polly cho Anh/Trung/Nhật, gTTS cho Việt
                use_polly = quiz_lang in ["English", "Chinese", "Japanese"]
                
                if use_polly:
                    # Lấy voice choice từ UI
                    voice_choice = None
                    if quiz_lang == "English":
                        voice_choice = "Matthew" if self.en_voice_var.get() == "male" else "Joanna"
                    elif quiz_lang == "Japanese":
                        voice_choice = "Takumi" if self.ja_voice_var.get() == "male" else "Mizuki"
                    
                    print(f"📢 [Mode 2] Đọc {quiz_lang} (Polly - {voice_choice}): {foreign_part[:60]}...")
                    self.voice_manager.voice_manager.speak_with_polly(foreign_part, language=tts_lang, voice=voice_choice)
                else:
                    print(f"📢 [Mode 2] Đọc {quiz_lang} (gTTS): {foreign_part[:60]}...")
                    self.voice_manager.voice_manager.speak_google_tts(foreign_part, language=tts_lang)
                time.sleep(0.5)
            
            # Bỏ đếm ngược - Đọc xong câu hỏi → có thể trả lời ngay
            print("\n▶️ Sẵn sàng trả lời!")
            self._safe_update_answer("🎤 Sẵn sàng! Hãy nói ngay...")
            time.sleep(0.3)
            
            # 🚀 Kiểm tra lại quiz vẫn đang chạy
            if not self.quiz_active:
                print("⏹️ Quiz đã dừng, dừng xử lý")
                return
            
            # Lắng nghe (ưu tiên theo ngôn ngữ test)
            print(f"\n▶️ Lắng nghe câu trả lời ({language_stt})...")
            
            # Update mic status - GIẢ animation (vì listen là blocking)
            self.root.after(0, lambda: self.mic_status_label.config(text="🎙️ Đang nghe... NÓI TO VÀO MIC!", foreground="red"))
            
            # Lấy microphone index từ combo (dùng mapping)
            mic_device_index = None
            try:
                combo_idx = self.mic_combo.current()
                if combo_idx >= 0 and combo_idx < len(self.mic_device_indices):
                    mic_device_index = self.mic_device_indices[combo_idx]
            except:
                mic_device_index = None
            
            # Animate bar trong background thread
            def animate_mic_bar():
                for _ in range(30):  # 15s / 0.5s = 30
                    if not self.app_running:  # Kiểm tra app còn chạy không
                        break
                    level = random.randint(20, 80)
                    try:
                        self.root.after(0, lambda l=level: self.mic_level_bar.config(value=l))
                    except RuntimeError:
                        break  # Main loop đã dừng
                    time.sleep(0.5)
            
            Thread(target=animate_mic_bar, daemon=True).start()
            
            user_answer = self.voice_manager.voice_manager.listen_to_microphone(
                timeout=15, 
                language=language_stt,
                quiz_type=self.quiz_type_str  # "meaning", "example", hoặc "vietnamese"
            )
            
            # Reset mic status
            self.root.after(0, lambda: self.mic_status_label.config(text="🎙️ Sẵn sàng", foreground="gray"))
            self.root.after(0, lambda: self.mic_level_bar.config(value=0))
            
            if not user_answer:
                self._safe_show_feedback("❌ Không nhận dạng được. Hãy nói lại!")
                # 🚀 Tự động tiến tới câu tiếp (thay vì treo)
                time.sleep(2)
                if self.quiz_active:
                    self._safe_next_question()
                return
            
            # 🚀 Kiểm tra quiz vẫn đang chạy trước khi xử lý
            if not self.quiz_active:
                print("⏹️ Quiz đã dừng, bỏ qua xử lý câu trả lời")
                return
            
            # Hiển thị câu trả lời NGAY (LIVE) sau khi nhận dạng xong
            # ✅ Instant transcription: Show recognized text immediately
            self._safe_update_answer(f"✅ Đã nhận dạng:\n\n{user_answer}")
            
            # So sánh NGAY (bỏ sleep để nhanh hơn)
            question = self.quiz_engine.questions[self.current_question_idx]
            
            # Xác định correct_answer theo Mode và quiz type
            if self.test_mode == 1:
                # Mode 1: Đọc VN → User trả lời foreign language
                if self.quiz_type_str == "meaning":
                    correct_answer = question.get("word")  # Từ vựng (EN/ZH/JA)
                elif self.quiz_type_str == "example":
                    # Ưa chọn field phù hợp: example_zh cho Chinese, example_en cho English
                    quiz_lang = self._get_quiz_language_code()
                    if quiz_lang == "Chinese":
                        correct_answer = question.get("example_zh", question.get("example_en", ""))
                    else:
                        correct_answer = question.get("example_en", "")
                else:  # vietnamese
                    quiz_lang = self._get_quiz_language_code()
                    if quiz_lang == "Chinese":
                        correct_answer = question.get("example_zh", question.get("example_en", ""))
                    else:
                        correct_answer = question.get("example_en", "")
            else:
                # Mode 2: Đọc foreign language → User trả lời VN
                if self.quiz_type_str == "meaning":
                    correct_answer = question.get("meaning")  # Nghĩa tiếng Việt
                elif self.quiz_type_str == "example":
                    correct_answer = question.get("example_vi")  # Dịch tiếng Việt
                else:  # vietnamese
                    correct_answer = question.get("example_vi")  # Dịch tiếng Việt
            
            is_correct, similarity, _, is_semantic = self.voice_manager.compare_answers(user_answer, correct_answer)
            
            # Lưu kết quả
            score = min(10, int(similarity * 10)) if is_correct else max(0, int(similarity * 5))
            question_num = question.get("excel_row", self.current_question_idx + 1)  # Số thứ tự từ Excel
            self.quiz_results.append({
                "question_num": question_num,  # ✨ Số thứ tự từ Excel
                "question": question.get("word"),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "score": score,
                "attempt": 1
            })
            
            # Phát feedback - SONG SONG: Popup ngay + TTS chạy thread riêng (hoặc bỏ TTS nếu faster_feedback)
            use_faster_feedback = self.faster_feedback_var.get()
            
            if is_correct:
                # ⚡ CHẾ ĐỘ NHANH: Chỉ hiển thị "✅ Đúng" + popup + đến câu tiếp
                if use_faster_feedback:
                    self._safe_show_feedback("✅ Đúng!")
                    
                    # Popup đơn giản
                    popup_ref = [None]
                    def create_popup():
                        popup_ref[0] = self._show_manual_close_popup("✅ Đúng", f"✅ ĐÚNG RỒI!\n\nĐiểm: {score}/10")
                    self.root.after(0, create_popup)
                    
                    # Đóng popup NGAY lập tức + đến câu tiếp
                    def fast_next():
                        time.sleep(0.2)  # Hiển thị popup 0.2s
                        if popup_ref[0] and self.app_running:
                            try:
                                self.root.after(0, popup_ref[0].destroy)
                            except:
                                pass
                        time.sleep(0.1)
                        self._safe_next_question()
                    Thread(target=fast_next, daemon=True).start()
                    return
                
                # ✅ CHẾ ĐỘ BÌNH THƯỜNG: Phát TTS feedback ngắn gọn
                feedback_msg = "✅ Đúng!"
                popup_msg = f"✅ ĐÚNG RỒI!\n\n📝 Câu trả lời: {correct_answer}\n\n🎤 Bạn trả lời: {user_answer}\n📊 Điểm: {score}/10"
                self._safe_show_feedback(feedback_msg)
                
                # Hiển thị popup KHÔNG auto-close, để thread TTS tự đóng
                popup_ref = [None]
                def create_popup():
                    popup_ref[0] = self._show_manual_close_popup("🎉 Chính Xác", popup_msg)
                self.root.after(0, create_popup)
                
                # Phát TTS trong thread riêng, tự đóng popup khi xong
                def play_tts_async():
                    self.voice_manager.voice_manager.speak_google_tts("Đúng!", language="vi")
                    # Đóng popup sau khi TTS xong
                    time.sleep(0.3)
                    if popup_ref[0] and self.app_running:
                        try:
                            self.root.after(0, popup_ref[0].destroy)
                        except:
                            pass
                    # Next question sau 0.5s
                    time.sleep(0.5)
                    self._safe_next_question()
                Thread(target=play_tts_async, daemon=True).start()
                return  # Dừng luồng chính tại đây, để thread tự next
            else:
                # Xác định ngôn ngữ đọc correct_answer
                if self.test_mode == 1:
                    quiz_lang = self._get_quiz_language_code()
                    lang_map = {"English": "en", "Chinese": "zh", "Japanese": "ja"}
                    answer_lang = lang_map.get(quiz_lang, "en")
                else:
                    answer_lang = "vi"
                
                # Chuẩn bị feedback
                semantic_note = " (✓ Đúng về mặt ý nghĩa)" if is_semantic else ""
                if similarity >= 0.7:
                    feedback_text = "Gần đúng! Đáp án chính xác là:"
                    popup_title = "⚠️ Gần Đúng"
                    feedback_msg = f"⚠️ Gần đúng!{semantic_note}\n\n✨ {correct_answer}"
                else:
                    feedback_text = "Sai rồi! Câu trả lời đúng là:"
                    popup_title = "❌ Sai Rồi"
                    feedback_msg = f"❌ Sai rồi!\n\n✨ {correct_answer}"
                
                popup_msg = f"📝 Đáp án đúng:\n{correct_answer}\n\n🎤 Bạn trả lời:\n{user_answer}{semantic_note}\n\n📊 Điểm: {score}/10"
                self._safe_show_feedback(feedback_msg)
                
                # Hiển thị popup KHÔNG auto-close, để thread TTS tự đóng
                popup_ref = [None]
                def create_popup():
                    popup_ref[0] = self._show_manual_close_popup(popup_title, popup_msg)
                self.root.after(0, create_popup)
                
                # Phát TTS trong thread riêng, tự đóng popup khi xong
                use_polly = (answer_lang != "vi")
                def play_tts_async():
                    if use_faster_feedback:
                        # Chế độ nhanh: chỉ hiển thị 0.5s rồi đến câu tiếp
                        time.sleep(0.5)
                    else:
                        # Chế độ bình thường: phát TTS
                        self.voice_manager.voice_manager.speak_google_tts(feedback_text, language="vi")
                        
                        # Dùng Polly cho Anh/Trung/Nhật, gTTS cho Việt
                        if answer_lang in ["en", "zh", "ja"]:
                            # Lấy voice choice từ UI
                            voice_choice = None
                            if answer_lang == "en":
                                voice_choice = "Matthew" if self.en_voice_var.get() == "male" else "Joanna"
                            elif answer_lang == "ja":
                                voice_choice = "Takumi" if self.ja_voice_var.get() == "male" else "Mizuki"
                            
                            self.voice_manager.voice_manager.speak_with_polly(correct_answer, language=answer_lang, voice=voice_choice)
                        else:
                            self.voice_manager.voice_manager.speak_google_tts(correct_answer, language=answer_lang)
                        time.sleep(0.5)
                    
                    # Đóng popup
                    if popup_ref[0] and self.app_running:
                        try:
                            self.root.after(0, popup_ref[0].destroy)
                        except:
                            pass
                    # Next question
                    time.sleep(0.3)
                    self._safe_next_question()
                Thread(target=play_tts_async, daemon=True).start()
                return  # Dừng luồng chính tại đây, để thread tự next
        
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            self._safe_show_error(f"Lỗi: {e}")
        finally:
            # 🔒 Release lock khi xong
            self.voice_question_lock.release()
    
    # ===== THREAD-SAFE TKINTER WRAPPERS =====
    
    def _show_auto_close_popup(self, title, message, auto_close_after=3):
        """Hiển thị popup tự động đóng sau N giây"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("400x250")
        popup.resizable(False, False)
        
        # 🎨 Set icon cho popup
        try:
            if self.icon_path.exists():
                popup.iconbitmap(str(self.icon_path))
        except:
            pass
        
        # Center popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (400 // 2)
        y = (popup.winfo_screenheight() // 2) - (250 // 2)
        popup.geometry(f"400x250+{x}+{y}")
        
        # Frame chính
        main_frame = ttk.Frame(popup, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon và message
        msg_label = tk.Label(main_frame, text=message, font=("Arial", 11), 
                            justify=tk.LEFT, wraplength=350)
        msg_label.pack(pady=20)
        
        # Countdown label
        countdown_var = tk.StringVar(value=f"Tự động đóng sau {auto_close_after} giây...")
        countdown_label = ttk.Label(main_frame, textvariable=countdown_var, 
                                   font=("Arial", 9), foreground="gray")
        countdown_label.pack(pady=10)
        
        # Button đóng
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=popup.destroy, width=15).pack()
        
        # Auto-close countdown
        remaining = [auto_close_after]
        
        def countdown():
            if remaining[0] > 0:
                remaining[0] -= 1
                countdown_var.set(f"Tự động đóng sau {remaining[0]} giây...")
                popup.after(1000, countdown)
            else:
                popup.destroy()
        
        popup.after(1000, countdown)
        popup.focus_force()
        return popup
    
    def _show_manual_close_popup(self, title, message):
        """Hiển thị popup với hình ảnh nhân vật động (TTS thread sẽ tự đóng khi phát xong)"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("550x480")
        popup.resizable(False, False)
        
        # 🎨 Set icon cho popup
        try:
            if self.icon_path.exists():
                popup.iconbitmap(str(self.icon_path))
        except:
            pass
        
        # Center popup
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (550 // 2)
        y = (popup.winfo_screenheight() // 2) - (480 // 2)
        popup.geometry(f"550x480+{x}+{y}")
        
        # Xác định màu sắc dựa trên title
        if "Chính Xác" in title or "Đúng" in title:
            bg_color = "#d4edda"  # Xanh lá
            text_color = "#155724"  # Xanh đậm
            title_color = "#28a745"  # Xanh lá đậm
        else:
            bg_color = "#f8d7da"  # Đỏ nhạt
            text_color = "#721c24"  # Đỏ đậm
            title_color = "#dc3545"  # Đỏ
        
        popup.config(bg=bg_color)
        
        # Frame chính
        main_frame = tk.Frame(popup, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text=title, font=("Arial", 16, "bold"),
                              fg=title_color, bg=bg_color)
        title_label.pack(pady=(0, 10))
        
        # 🎨 Load + Display Animated GIF
        img_label = tk.Label(main_frame, bg=bg_color)
        img_label.pack(pady=10)
        
        gif_path = Path(__file__).parent / "anh1.gif"
        if gif_path.exists():
            try:
                from PIL import Image, ImageTk
                from PIL import ImageSequence
                
                # Load GIF
                gif_image = Image.open(gif_path)
                
                # Extract all frames
                frames = []
                for frame_idx in range(gif_image.n_frames):
                    gif_image.seek(frame_idx)
                    # Resize frame
                    frame = gif_image.convert("RGBA").copy()
                    frame.thumbnail((200, 150), Image.Resampling.LANCZOS)
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(frame)
                    frames.append(photo)
                
                # Animation loop
                frame_index = [0]
                def animate_gif():
                    if not popup.winfo_exists():
                        return
                    
                    img_label.config(image=frames[frame_index[0]])
                    frame_index[0] = (frame_index[0] + 1) % len(frames)
                    # Update mỗi 100ms (điều chỉnh tốc độ nếu cần)
                    popup.after(100, animate_gif)
                
                # Start animation
                animate_gif()
                
            except Exception as e:
                print(f"⚠️ Lỗi load GIF: {e}")
                error_label = tk.Label(main_frame, text="❌ Không load được GIF", 
                                      font=("Arial", 10), fg="red", bg=bg_color)
                error_label.pack()
        
        # Message
        msg_label = tk.Label(main_frame, text=message, font=("Arial", 12, "bold"),
                            fg=text_color, justify=tk.LEFT, wraplength=480, bg=bg_color)
        msg_label.pack(pady=10)
        
        # Hiển thị trạng thái
        status_label = tk.Label(main_frame, text="🔊 Đang phát giọng nói...",
                               font=("Arial", 10), fg="blue", bg=bg_color)
        status_label.pack(pady=8)
        
        # Button đóng
        btn_frame = tk.Frame(main_frame, bg=bg_color)
        btn_frame.pack(pady=12)
        
        close_btn = tk.Button(btn_frame, text="OK", command=popup.destroy,
                             font=("Arial", 11, "bold"), width=15,
                             bg=title_color, fg="white", cursor="hand2")
        close_btn.pack()
        
        popup.focus_force()
        return popup
        popup.focus_force()
        
        # Đợi popup đóng
        self.root.wait_window(popup)
    
    def _safe_show_feedback(self, message):
        """Thread-safe wrapper to show voice feedback"""
        try:
            if not self.app_running:
                return
            self.root.after(0, lambda msg=message: self._show_voice_feedback(msg))
        except RuntimeError as e:
            print(f"⚠️ Tkinter error (feedback): {message} - {e}")
    
    def _safe_update_answer(self, answer):
        """Thread-safe wrapper to update voice answer"""
        try:
            if not self.app_running:
                return
            self.root.after(0, lambda ans=answer: self._update_voice_answer(ans))
        except RuntimeError as e:
            print(f"⚠️ Tkinter error (answer update): {answer} - {e}")
    
    def _safe_next_question(self):
        """Thread-safe wrapper to move to next question"""
        try:
            if not self.app_running:
                return
            self.root.after(0, self.voice_next_question)
        except RuntimeError as e:
            print(f"⚠️ Tkinter error (next question): {e}")
    
    def _safe_show_error(self, error_msg):
        """Thread-safe wrapper to show error dialog"""
        try:
            if not self.app_running:
                return
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Lỗi", msg))
        except RuntimeError as e:
            print(f"⚠️ Tkinter error (error dialog): {error_msg} - {e}")
    
    def _on_test_mode_change(self):
        """Callback when test mode changes"""
        self.test_mode = self.test_mode_var.get()
        self.user_settings["test_mode"] = self.test_mode  # Lưu ngay lập tức
        self._save_settings()
        mode_name = "Mode 1: VN→Anh/Trung/Nhật" if self.test_mode == 1 else "Mode 2: Anh/Trung/Nhật→VN"
        print(f"✨ Chế độ Voice Quiz: {mode_name}")
    
    def test_microphone(self):
        """Test mic với real-time audio level"""
        try:
            # Lấy mic index
            combo_idx = self.mic_combo.current()
            mic_device_index = None
            if combo_idx >= 0 and combo_idx < len(self.mic_device_indices):
                mic_device_index = self.mic_device_indices[combo_idx]
            
            self.test_mic_label.config(text="🎙️ Đang test... Hãy nói vào mic!", foreground="red")
            self.test_mic_bar.config(value=0)
            
            def update_level(level):
                """Callback để update progress bar"""
                self.root.after(0, lambda: self.test_mic_bar.config(value=level))
            
            # Chạy test trong thread
            def run_test():
                success = self.voice_manager.voice_manager.test_microphone(
                    device_index=mic_device_index,
                    duration=5,
                    level_callback=update_level
                )
                
                if success:
                    self.root.after(0, lambda: self.test_mic_label.config(
                        text="✅ Mic hoạt động tốt!", foreground="green"
                    ))
                else:
                    self.root.after(0, lambda: self.test_mic_label.config(
                        text="❌ Mic không nhận được âm thanh!", foreground="red"
                    ))
                
                # Reset bar sau 2s
                self.root.after(2000, lambda: self.test_mic_bar.config(value=0))
            
            Thread(target=run_test, daemon=True).start()
        
        except Exception as e:
            self.test_mic_label.config(text=f"❌ Lỗi: {e}", foreground="red")
            print(f"❌ Test mic error: {e}")
    
    # ===== GIF ANIMATION =====
    
    def _load_gif_frames(self):
        """Load GIF frames một lần duy nhất"""
        if self.gif_frames:
            return  # Đã load rồi
        
        try:
            from PIL import Image, ImageTk
            gif_path = Path(__file__).parent / "anh1.gif"
            
            if not gif_path.exists():
                return
            
            # Load GIF
            gif_image = Image.open(gif_path)
            
            # Extract all frames
            for frame_idx in range(gif_image.n_frames):
                gif_image.seek(frame_idx)
                frame = gif_image.convert("RGBA").copy()
                frame.thumbnail((150, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame)
                self.gif_frames.append(photo)
        except Exception as e:
            print(f"⚠️ Lỗi load GIF: {e}")
    
    def _animate_gif_question(self):
        """Animate GIF khi đang đọc câu hỏi"""
        if not self.gif_frames or not self.gif_animating[0]:
            return
        
        try:
            self.voice_gif_label.config(image=self.gif_frames[self.gif_frame_index[0]])
            self.gif_frame_index[0] = (self.gif_frame_index[0] + 1) % len(self.gif_frames)
            
            # Update mỗi 100ms
            if self.gif_animating[0]:
                self.root.after(100, self._animate_gif_question)
        except Exception as e:
            print(f"⚠️ Lỗi animate GIF: {e}")
    
    def _start_gif_animation(self):
        """Bắt đầu animate GIF"""
        self._load_gif_frames()
        if self.gif_frames:
            self.gif_animating[0] = True
            self.gif_frame_index[0] = 0
            self._animate_gif_question()
    
    def _stop_gif_animation(self):
        """Dừng animate GIF"""
        self.gif_animating[0] = False
    
    # ===== HELPER METHODS =====
    
    def _get_quiz_language_code(self):
        """Get ngôn ngữ quiz từ sheet name hoặc file name"""
        try:
            sheet_name = self.sheet_combo.get().lower()
            
            # Detect từ tên sheet
            if "english" in sheet_name or "anh" in sheet_name or "eng" in sheet_name:
                return "English"
            elif "chinese" in sheet_name or "trung" in sheet_name or "中文" in sheet_name or "china" in sheet_name:
                return "Chinese"
            elif "japanese" in sheet_name or "nhật" in sheet_name or "日本" in sheet_name or "japan" in sheet_name:
                return "Japanese"
            
            # Default English
            return "English"
        except:
            return "English"
    
    def _get_stt_language(self):
        """Map ngôn ngữ quiz → STT language code (xem xét test mode + quiz type)"""
        # Mode 2: Chatbot đọc foreign → User trả lời Vietnamese
        if self.test_mode == 2:
            return "vi-VN"
        
        # Mode 1: Chatbot đọc Vietnamese → User trả lời foreign language
        # Tất cả quiz types trong Mode 1 đều yêu cầu trả lời bằng foreign language
        quiz_lang = self._get_quiz_language_code()
        
        stt_map = {
            "English": "en-US",      # English - USA
            "Chinese": "zh-CN",      # Chinese - Simplified
            "Japanese": "ja-JP",     # Japanese
        }
        
        stt_lang = stt_map.get(quiz_lang, "en-US")
        return stt_lang
    
    def _choose_font(self, text):
        """Chọn font phù hợp với nội dung (Latin vs CJK)"""
        # Kiểm tra nếu có ký tự CJK (Trung/Hàn/Nhật)
        for char in text:
            code = ord(char)
            # Trung Quốc: 4E00-9FFF
            # Hàn Quốc: AC00-D7AF
            # Nhật: 3040-309F, 30A0-30FF
            if (0x4E00 <= code <= 0x9FFF) or \
               (0xAC00 <= code <= 0xD7AF) or \
               (0x3040 <= code <= 0x309F) or \
               (0x30A0 <= code <= 0x30FF):
                return self.font_cjk
        
        # Mặc định dùng font Latin
        return self.font_latin
    
    
    def _update_voice_answer(self, answer):
        """Cập nhật câu trả lời"""
        self.voice_answer_text.config(state=tk.NORMAL)
        self.voice_answer_text.delete(1.0, tk.END)
        self.voice_answer_text.insert(tk.END, f"🎤 Bạn nói: {answer}")
        self.voice_answer_text.config(state=tk.DISABLED)
    
    def _show_voice_feedback(self, feedback_msg):
        """Hiển thị feedback"""
        self.voice_feedback_text.config(state=tk.NORMAL)
        self.voice_feedback_text.delete(1.0, tk.END)
        self.voice_feedback_text.insert(tk.END, feedback_msg)
        self.voice_feedback_text.config(state=tk.DISABLED)
    
    def voice_next_question(self):
        """Câu tiếp theo (Voice) - kiểm tra xem quiz kết thúc chưa"""
        self.current_question_idx += 1
        
        # 🚀 Kiểm tra quiz đã hết câu hỏi chưa
        if self.current_question_idx >= len(self.quiz_engine.questions):
            print("✅ Kết thúc quiz!")
            self.voice_show_results()  # Show results + dialog nhập tên
            return
        
        self.voice_display_question()
    
    def voice_stop_quiz(self):
        """Dừng Voice Quiz"""
        self.quiz_active = False  # 🚀 Dừng thread
        if messagebox.askyesno("Xác nhận", "❌ Dừng kiểm tra?"):
            self.voice_show_results()
    
    def voice_show_results(self):
        """Hiển thị kết quả + hỏi tên user để lưu"""
        # 👤 Tạo custom dialog với icon
        dialog = tk.Toplevel(self.root)
        dialog.title("Lưu Kết Quả")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        
        # 🎨 Set icon cho dialog
        try:
            if self.icon_path.exists():
                dialog.iconbitmap(str(self.icon_path))
        except:
            pass
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame chính
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="👤 Nhập tên của bạn:", font=("Arial", 10)).pack(anchor=tk.W, pady=(0, 5))
        
        entry = ttk.Entry(frame, width=30, font=("Arial", 10))
        entry.insert(0, "Test Phuong Anh")  # ✨ Default name
        entry.pack(fill=tk.X, pady=(0, 15))
        entry.focus()
        entry.select_range(0, tk.END)  # Select all text for easy editing
        
        user_name = [None]  # Để lưu kết quả từ dialog
        
        def on_ok():
            user_name[0] = entry.get().strip()
            if not user_name[0]:
                messagebox.showwarning("Cảnh báo", "⚠️ Vui lòng nhập tên!")
                return
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="OK", command=on_ok, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel, width=12).pack(side=tk.LEFT, padx=5)
        
        self.root.wait_window(dialog)
        
        # Nếu user nhập tên thì lưu tự động
        if user_name[0]:
            # 🕐 Thêm timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Thêm tên và thời gian vào mỗi kết quả
            for result in self.quiz_results:
                result["user_name"] = user_name[0]
                result["timestamp"] = timestamp
            
            # 💾 Tự động lưu file JSON
            self._auto_save_results(user_name[0], timestamp)
            
            # 📤 Gửi kết quả lên Discord
            self._send_to_discord(user_name[0], timestamp)
            
            print(f"✅ Lưu kết quả với tên: {user_name[0]}, Thời gian: {timestamp}")
        
        self.show_results()
        self.notebook.select(self.results_tab)
    
    # ===== RESULTS =====
    
    def show_results(self):
        """Hiển thị kết quả"""
        if not self.quiz_results or len(self.quiz_results) == 0:
            messagebox.showinfo("Kết quả", "Không có kết quả để hiển thị!")
            return
        
        # 👤 Lấy tên user và timestamp từ kết quả (nếu có)
        user_name = self.quiz_results[0].get("user_name", "Unknown")
        timestamp = self.quiz_results[0].get("timestamp", "")
        
        total_points = sum(r.get("score", 0) for r in self.quiz_results)
        num_questions = len(self.quiz_results)
        avg_score = (total_points / (num_questions * 10)) * 100 if num_questions > 0 else 0
        
        if avg_score >= 90:
            grade = "A - Xuất sắc"
        elif avg_score >= 80:
            grade = "B - Tốt"
        elif avg_score >= 70:
            grade = "C - Khá"
        elif avg_score >= 60:
            grade = "D - Đạt"
        else:
            grade = "F - Chưa đạt"
        
        report = f"""
═══════════════════════════════════════════════════════════════
📊 KẾT QUẢ KIỂM TRA
═══════════════════════════════════════════════════════════════

👤 Học sinh: {user_name}
🕐 Thời gian: {timestamp}

📈 TỔNG HỢP:
   Điểm trung bình: {avg_score:.1f}/100
   Xếp loại: {grade}
   Tổng điểm: {total_points}/{num_questions * 10}

📋 CHI TIẾT TỪNG CÂU:
"""
        for result in self.quiz_results:
            question_num = result.get('question_num', '?')  # Lấy số thứ tự từ Excel
            report += f"\n{question_num}. {result['question']} (Lần {result['attempt']})\n"
            report += f"   Bạn trả lời: {result['user_answer']}\n"
            report += f"   Đáp án: {result['correct_answer']}\n"
            report += f"   Điểm: {result['score']}/10\n"
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, report)
        self.results_text.config(state=tk.DISABLED)
        
        # 🗑️ XÓA TABS QUIZ ĐI (quay về 2 tabs ban đầu)
        if self.quiz_tab is not None:
            try:
                self.notebook.forget(self.quiz_tab)
                self.quiz_tab = None
            except:
                pass
        
        if self.voice_quiz_tab is not None:
            try:
                self.notebook.forget(self.voice_quiz_tab)
                self.voice_quiz_tab = None
            except:
                pass
        
        # Chuyển về tab Results
        self.notebook.select(self.results_tab)
    
    def _auto_save_results(self, user_name, timestamp):
        """💾 Tự động lưu kết quả vào file + database"""
        try:
            # Tạo folder nếu chưa có
            results_dir = Path(__file__).parent / "results"
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Tạo tên file: [user_name]_[timestamp].json
            safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '_', '-')).strip()
            timestamp_file = timestamp.replace(" ", "_").replace(":", "-")
            file_name = f"{safe_name}_{timestamp_file}.json"
            file_path = results_dir / file_name
            
            # Lưu file JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.quiz_results, f, ensure_ascii=False, indent=2)
            
            # 🎓 Log answers to database for spaced repetition
            try:
                if self.selected_file:
                    file_name_only = Path(self.selected_file).name
                    sheet_name = self.sheet_combo.get() if hasattr(self, 'sheet_combo') else "Sheet1"
                    language = self._detect_language_from_file(file_name_only)
                    
                    for result in self.quiz_results:
                        word = result.get("question", "").strip()
                        if word:
                            # Add word to DB
                            word_id = self.study_db.add_or_update_word(word, language)
                            
                            # Log the answer
                            is_correct = result.get("score", 0) > 0
                            self.study_db.log_answer(word_id, is_correct, file_name_only, sheet_name)
                            
                            # 🎯 If in Practice Mode and correct: clear the next_review_date
                            if hasattr(self, 'quiz_mode') and self.quiz_mode == "practice" and is_correct:
                                try:
                                    from datetime import datetime
                                    # Mark as completed (no next review needed)
                                    cursor = self.study_db.conn.cursor()
                                    cursor.execute(
                                        "UPDATE words SET next_review_date = NULL WHERE word_id = ?",
                                        (word_id,)
                                    )
                                    self.study_db.conn.commit()
                                    print(f"✅ Từ '{word}' đã hoàn thành - xóa next_review_date")
                                except Exception as e:
                                    print(f"⚠️ Lỗi khi cập nhật review date: {e}")
                    
                    print(f"✅ Đã log {len(self.quiz_results)} answers to database")
            except Exception as db_err:
                print(f"⚠️ Lỗi khi log database: {db_err}")
            
            print(f"✅ Đã lưu tự động: {file_path}")
        except Exception as e:
            print(f"⚠️ Lỗi lưu tự động: {e}")
    
    def _send_to_discord(self, user_name, timestamp):
        """📤 Gửi kết quả và ảnh lên Discord webhook"""
        try:
            import requests
            import io
            import os
            from dotenv import load_dotenv
            
            # Load Discord webhook URL from .env
            load_dotenv()
            webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
            
            if not webhook_url:
                print("⚠️ DISCORD_WEBHOOK_URL không tìm thấy trong .env file")
                return
            
            # Tính toán thống kê
            total_points = sum(r.get("score", 0) for r in self.quiz_results)
            num_questions = len(self.quiz_results)
            avg_score = (total_points / (num_questions * 10)) * 100 if num_questions > 0 else 0
            
            if avg_score >= 90:
                grade = "A - Xuất sắc 🌟"
            elif avg_score >= 80:
                grade = "B - Tốt 👍"
            elif avg_score >= 70:
                grade = "C - Khá 👌"
            elif avg_score >= 60:
                grade = "D - Đạt ✓"
            else:
                grade = "F - Chưa đạt 📚"
            
            # Lấy thông tin file và phạm vi câu hỏi
            file_name = os.path.basename(self.selected_file) if hasattr(self, 'selected_file') and self.selected_file else "Unknown"
            start_q = self.start_question_var.get()
            end_q = self.end_question_var.get()
            
            # Tạo nội dung message
            message_content = f"""
📊 **KẾT QUẢ KIỂM TRA**
═══════════════════════════════════════
👤 **Học sinh:** {user_name}
🕐 **Thời gian:** {timestamp}
📁 **File:** {file_name}
📝 **Phạm vi:** từ câu {start_q} đến câu {end_q}

📈 **TỔNG HỢP:**
   • Điểm trung bình: **{avg_score:.1f}/100**
   • Xếp loại: **{grade}**
   • Tổng điểm: **{total_points}/{num_questions * 10}**

📋 **CHI TIẾT ({num_questions} câu):**
"""
            
            # Thêm 5 câu đầu tiên
            for idx, result in enumerate(self.quiz_results[:5], 1):
                question_num = result.get('question_num', idx)
                score = result.get('score', 0)
                emoji = "✅" if score >= 8 else "⚠️" if score >= 5 else "❌"
                message_content += f"\n{emoji} **#{question_num}** {result['question']}: {score}/10"
            
            if num_questions > 5:
                message_content += f"\n... và {num_questions - 5} câu khác"
            
            # Chụp ảnh từ camera
            photo_data = None
            try:
                import cv2
                import numpy as np
                
                # Lấy camera index
                cam_idx = 0
                if self.camera_indices:
                    combo_idx = self.camera_combo.current()
                    if combo_idx >= 0 and combo_idx < len(self.camera_indices):
                        cam_idx = self.camera_indices[combo_idx]
                
                cap = cv2.VideoCapture(cam_idx)
                if cap.isOpened():
                    # Đọc vài frame để camera ổn định
                    for _ in range(5):
                        cap.read()
                    
                    ret, frame = cap.read()
                    if ret:
                        # Convert to JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                        photo_data = buffer.tobytes()
                        print("✅ Đã chụp ảnh từ camera")
                    cap.release()
            except Exception as cam_err:
                print(f"⚠️ Không thể chụp ảnh: {cam_err}")
            
            # Gửi lên Discord
            files = {}
            if photo_data:
                files['file'] = ('photo.jpg', io.BytesIO(photo_data), 'image/jpeg')
            
            payload = {
                'content': message_content,
                'username': 'Quiz Bot 🎓'
            }
            
            response = requests.post(webhook_url, data=payload, files=files if files else None)
            
            if response.status_code == 204 or response.status_code == 200:
                print(f"✅ Đã gửi kết quả lên Discord{'(+ảnh)' if photo_data else ''}")
            else:
                print(f"⚠️ Discord webhook failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Lỗi gửi Discord: {e}")
    
    def save_results(self):
        """Lưu kết quả"""
        if not self.quiz_results:
            messagebox.showwarning("Cảnh báo", "❌ Không có kết quả để lưu!")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json"), ("All", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.quiz_results, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("Thành công", f"✅ Kết quả đã lưu:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"❌ Lỗi khi lưu:\n{e}")
    
    def load_previous_results(self):
        """📂 Load kết quả cũ từ folder results/"""
        try:
            results_dir = Path(__file__).parent / "results"
            
            # Kiểm tra folder tồn tại
            if not results_dir.exists():
                messagebox.showinfo("Thông báo", "📂 Chưa có kết quả được lưu.\n\nFolder: results/")
                return
            
            # Liệt kê tất cả file JSON
            json_files = sorted(results_dir.glob("*.json"), reverse=True)
            
            if not json_files:
                messagebox.showinfo("Thông báo", "📂 Chưa có kết quả được lưu trong folder results/")
                return
            
            # Tạo dialog chọn file
            file_names = [f.name for f in json_files]
            
            # Simple selection dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("📂 Chọn Kết Quả Cũ")
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            
            # Set icon
            try:
                if self.icon_path.exists():
                    dialog.iconbitmap(str(self.icon_path))
            except:
                pass
            
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="📂 Chọn file kết quả:", font=("Arial", 10)).pack(anchor=tk.W, padx=10, pady=10)
            
            # Listbox to show files
            listbox = tk.Listbox(dialog, height=12, font=("Arial", 9))
            listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
            for fname in file_names:
                listbox.insert(tk.END, fname)
            
            if file_names:
                listbox.select_set(0)
            
            selected_file = [None]
            
            def on_load():
                sel = listbox.curselection()
                if sel:
                    selected_file[0] = json_files[sel[0]]
                    dialog.destroy()
            
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(fill=tk.X, padx=10, pady=5)
            ttk.Button(btn_frame, text="Xem", command=on_load, width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Đóng", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
            
            self.root.wait_window(dialog)
            
            # Load file nếu user chọn
            if selected_file[0]:
                with open(selected_file[0], 'r', encoding='utf-8') as f:
                    loaded_results = json.load(f)
                
                # Display kết quả
                self._display_loaded_results(loaded_results)
                self.notebook.select(self.results_tab)
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"❌ Lỗi khi load kết quả:\n{e}")
            print(f"⚠️ Error: {e}")
    
    def _display_loaded_results(self, loaded_results):
        """Hiển thị kết quả đã load"""
        if not loaded_results:
            return
        
        # Lấy tên user và timestamp
        user_name = loaded_results[0].get("user_name", "Unknown")
        timestamp = loaded_results[0].get("timestamp", "")
        
        total_points = sum(r.get("score", 0) for r in loaded_results)
        num_questions = len(loaded_results)
        avg_score = (total_points / (num_questions * 10)) * 100 if num_questions > 0 else 0
        
        if avg_score >= 90:
            grade = "A - Xuất sắc"
        elif avg_score >= 80:
            grade = "B - Tốt"
        elif avg_score >= 70:
            grade = "C - Khá"
        elif avg_score >= 60:
            grade = "D - Đạt"
        else:
            grade = "F - Chưa đạt"
        
        report = f"""
═══════════════════════════════════════════════════════════════
📊 KẾT QUẢ KIỂM TRA (ĐÃ LƯU)
═══════════════════════════════════════════════════════════════

👤 Học sinh: {user_name}
🕐 Thời gian: {timestamp}

📈 TỔNG HỢP:
   Điểm trung bình: {avg_score:.1f}/100
   Xếp loại: {grade}
   Tổng điểm: {total_points}/{num_questions * 10}

📋 CHI TIẾT TỪNG CÂU:
"""
        for result in loaded_results:
            question_num = result.get('question_num', '?')  # Lấy số thứ tự từ Excel
            report += f"\n{question_num}. {result['question']} (Lần {result['attempt']})\n"
            report += f"   Bạn trả lời: {result['user_answer']}\n"
            report += f"   Đáp án: {result['correct_answer']}\n"
            report += f"   Điểm: {result['score']}/10\n"
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, report)
        self.results_text.config(state=tk.DISABLED)
    
    def restart_quiz(self):
        """Kiểm tra lại"""
        self.notebook.select(0)
    
    def _show_info(self, message):
        """Show info message dialog"""
        messagebox.showinfo("Thông báo", message, parent=self.root)
    
    def _show_error(self, message):
        """Show error message dialog"""
        messagebox.showerror("Lỗi", message, parent=self.root)
    
    def _detect_language_from_file(self, filename: str) -> str:
        """Detect language from filename"""
        filename_lower = filename.lower()
        
        # Check for language keywords
        if any(kw in filename_lower for kw in ['english', 'anh', '_en_', 'e2']):
            return "English"
        elif any(kw in filename_lower for kw in ['japanese', 'nhật', '_ja_', 'j1', 'j2']):
            return "Japanese"
        elif any(kw in filename_lower for kw in ['chinese', 'hán', 'trung quốc', '_zh_', 'ch']):
            return "Chinese"
        elif any(kw in filename_lower for kw in ['vietnamese', 'việt', '_vn_']):
            return "Vietnamese"
        else:
            # Default based on first word
            return "Unknown"
    
    def _on_closing(self):
        """Xử lý khi đóng cửa sổ"""
        self.app_running = False  # Dừng tất cả background threads
        
        # Close database
        try:
            if hasattr(self, 'study_db'):
                self.study_db.close()
                print("✅ Database closed")
        except:
            pass
        
        time.sleep(0.5)  # Đợi threads dừng (tăng từ 0.3 → 0.5)
        try:
            self.root.destroy()
        except:
            pass  # Nếu destroy thất bại thì bỏ qua


def main():
    root = tk.Tk()
    app = LanguageQuizGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
