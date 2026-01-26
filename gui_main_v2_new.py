f"""
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
import sqlite3
from quiz_engine import QuizEngine
from voice_quiz_v2 import VoiceQuizManager
from db_manager import StudyHistoryDB
from pathlib import Path
import json
import threading
from threading import Thread, Lock
import tkinter.font as tkFont
import winsound  # Để phát beep sound
from datetime import datetime  # 🕐 Để lưu timestamp


class LanguageQuizGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Language Quiz v2.2 - Multi-Language Voice -Kiểm tra đa ngôn ngữ 0986183806")
        self.root.geometry("1400x1000")
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
        
        # 📚 Smart Review Database
        try:
            from smart_review_db import SmartReviewDB
            self.smart_review_db = SmartReviewDB()
            print("✅ Smart Review System initialized!")
        except Exception as e:
            print(f"⚠️ Smart Review DB error: {e}")
            self.smart_review_db = None
        
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
        
        # Tab 3: Multiple Choice Practice (luôn hiển thị)
        self.practice_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.practice_tab, text="📱 Practice (ABC)")
        self.practice_quiz_engine = None
        self.practice_questions = []
        self.practice_current_idx = 0
        self.practice_results = []
        self.practice_paused = False
        self._create_practice_tab()
        
        # Tab 4: Flashcard Mode (luôn hiển thị)
        self.flashcard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.flashcard_tab, text="🃏 Flashcard")
        self.flashcard_data = []
        self.flashcard_current_idx = 0
        self.flashcard_showing_answer = False
        self._create_flashcard_tab()
        
        # Tab 5: Dashboard (luôn hiển thị)
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="📈 Dashboard")
        self._create_dashboard_tab()
        
        # Tab Results (luôn hiển thị)
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="📊 Kết quả")
        self._create_results_tab()
        
        # Tab Guide (luôn hiển thị)
        self.guide_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.guide_tab, text="💡 Hướng dẫn")
        self._create_guide_tab()
        
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
        
        # Row 0: File button và Settings button
        file_row = ttk.Frame(file_frame)
        file_row.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=3)
        
        ttk.Button(file_row, text="Chọn File Excel", 
                  command=self.select_excel_file, width=20).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(file_row, text="⚙️ Cài đặt API", 
                  command=self.open_settings_dialog, width=15).pack(side=tk.LEFT)
        
        self.file_label = ttk.Label(file_frame, text="Chưa chọn", foreground="gray", font=("Segoe UI", 9))
        self.file_label.grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.W)
        
        ttk.Label(file_frame, text="Sheet:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=(5,0))
        self.sheet_combo = ttk.Combobox(file_frame, state="readonly", width=35)
        self.sheet_combo.grid(row=3, column=0, columnspan=2, pady=3, sticky=tk.EW)
        
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
        
        # Quiz type với thời gian
        ttk.Label(quiz_frame, text="Loại:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.quiz_type_var = tk.StringVar(value="meaning")
        
        # Thời gian cho từng loại quiz (mặc định: Nghĩa từ-4s, Dịch câu-12s, VN→EN-12s)
        self.time_limits = {
            "meaning": tk.IntVar(value=4),
            "example": tk.IntVar(value=12),
            "vietnamese": tk.IntVar(value=12)
        }
        
        # Radio buttons với combobox thời gian
        for text, value in [("Nghĩa từ", "meaning"), ("Dịch câu", "example"), ("VN→EN", "vietnamese")]:
            row_frame = ttk.Frame(quiz_frame)
            row_frame.pack(fill=tk.X, pady=1)
            
            ttk.Radiobutton(row_frame, text=text, variable=self.quiz_type_var, value=value).pack(side=tk.LEFT)
            
            ttk.Label(row_frame, text="⏱️", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10,2))
            time_combo = ttk.Combobox(row_frame, textvariable=self.time_limits[value], 
                                     values=[2,4,6,8,10,12,15,20,30], width=4, state="normal")
            time_combo.pack(side=tk.LEFT, padx=2)
            ttk.Label(row_frame, text="giây", font=("Segoe UI", 8), foreground="gray").pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(quiz_frame, orient='horizontal').pack(fill=tk.X, pady=8)
        
        # Auto timing mode
        ttk.Label(quiz_frame, text="⏱️ Chế độ thời gian:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.auto_timing_var = tk.BooleanVar(value=False)
        timing_frame = ttk.Frame(quiz_frame)
        timing_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(timing_frame, text="📌 Thủ công (cố định)", 
                       variable=self.auto_timing_var, value=False).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(timing_frame, text="🤖 Tự động (theo độ dài câu)", 
                       variable=self.auto_timing_var, value=True).pack(anchor=tk.W, pady=2)
        
        ttk.Label(quiz_frame, text="   💡 Auto: chatbot tính thời gian cho từng câu", 
                 font=("Segoe UI", 8), foreground="gray").pack(anchor=tk.W)
        
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
        
        # Ngôn ngữ Chatbot (hướng dẫn, phản hồi)
        bot_lang_frame = ttk.Frame(voice_frame)
        bot_lang_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(bot_lang_frame, text="🤖 Chatbot:", font=("Segoe UI", 9, "bold"), width=10).pack(side=tk.LEFT)
        self.bot_language_var = tk.StringVar(value="vi")
        bot_lang_combo = ttk.Combobox(bot_lang_frame, textvariable=self.bot_language_var, 
                                     values=["Tiếng Việt", "Tiếng Anh", "Tiếng Trung", "Tiếng Nhật"], 
                                     state="readonly", width=15)
        bot_lang_combo.pack(side=tk.LEFT, padx=3)
        bot_lang_combo.current(0)  # Mặc định Tiếng Việt
        ttk.Label(bot_lang_frame, text="(Hướng dẫn & phản hồi)", font=("Segoe UI", 8), foreground="gray").pack(side=tk.LEFT, padx=3)
        
        ttk.Separator(voice_frame, orient='horizontal').pack(fill=tk.X, pady=8)
        
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
        
        # Voice Speed Control
        speed_frame = ttk.Frame(voice_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="🔊 Tốc độ:", font=("Segoe UI", 9), width=10).pack(side=tk.LEFT)
        self.voice_speed_var = tk.DoubleVar(value=1.0)
        
        # Speed slider: 0.5x to 2.0x
        self.voice_speed_slider = ttk.Scale(
            speed_frame, from_=0.5, to=2.0, variable=self.voice_speed_var,
            orient=tk.HORIZONTAL, length=150,
            command=self._update_speed_label
        )
        self.voice_speed_slider.pack(side=tk.LEFT, padx=5)
        
        self.voice_speed_label = ttk.Label(speed_frame, text="1.0x", font=("Segoe UI", 9, "bold"), width=5)
        self.voice_speed_label.pack(side=tk.LEFT)
        
        # Preset buttons
        ttk.Button(speed_frame, text="0.5x", width=4, 
                  command=lambda: self._set_voice_speed(0.5)).pack(side=tk.LEFT, padx=2)
        ttk.Button(speed_frame, text="1x", width=4, 
                  command=lambda: self._set_voice_speed(1.0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(speed_frame, text="1.5x", width=4, 
                  command=lambda: self._set_voice_speed(1.5)).pack(side=tk.LEFT, padx=2)
        
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
        
        # Range - Chọn từ câu nào đến câu nào (di chuyển từ left column)
        range_frame_container = ttk.LabelFrame(right_col, text="📝 Phạm vi câu hỏi", padding=10)
        range_frame_container.pack(fill=tk.X, pady=(0, 10))
        
        range_frame = ttk.Frame(range_frame_container)
        range_frame.pack(fill=tk.X)
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
        ttk.Checkbutton(range_frame_container, text="🔀 Trộn câu hỏi", variable=self.shuffle_var).pack(anchor=tk.W, pady=(5,0))
        
        # Start Buttons - HORIZONTAL LAYOUT
        button_frame = ttk.LabelFrame(right_col, text="🚀 Bắt đầu", padding=10)
        button_frame.pack(fill=tk.X)
        
        # Grid 2 columns
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        tk.Button(button_frame, text="▶️ KIỂM TRA\nTHƯỜNG", 
                 command=self.start_quiz, font=("Segoe UI", 11, "bold"),
                 bg="#2196f3", fg="white", height=3, cursor="hand2"
                 ).grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        
        tk.Button(button_frame, text="🎤 VOICE\nQUIZ", 
                 command=self.start_voice_quiz, font=("Segoe UI", 11, "bold"),
                 bg="#4caf50", fg="white", height=3, cursor="hand2"
                 ).grid(row=0, column=1, sticky="nsew", padx=3, pady=3)
        
        # Pause button (only for Voice Quiz)
        self.voice_pause_btn = tk.Button(
            button_frame, text="⏸️ Tạm dừng", 
            command=self._toggle_voice_pause, font=("Segoe UI", 10),
            bg="#ff9800", fg="white", state=tk.DISABLED, cursor="hand2"
        )
        self.voice_pause_btn.grid(row=1, column=0, columnspan=2, sticky="ew", padx=3, pady=(3,0))
        
        # Info - compact version at bottom
        info_frame = ttk.Frame(right_col)
        info_frame.pack(fill=tk.X, pady=(10,0))
        
        info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, font=("Segoe UI", 8), 
                           bg="#f9f9f9", relief=tk.FLAT, padx=8, pady=8)
        info_text.pack(fill=tk.X)
        info_text.insert(tk.END, "💡 Chọn file Excel → Test mic → Chọn loại quiz → Voice Quiz\n")
        info_text.insert(tk.END, "⚡ Auto timing: chatbot tự tính thời gian cho từng câu")
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
        
        # Question header with speaker button
        question_header = ttk.Frame(left_frame)
        question_header.pack(fill=tk.X, pady=(0,5))
        
        ttk.Label(question_header, text="❓ Câu hỏi", font=("Arial", 11, "bold"), foreground="#2c3e50").pack(side=tk.LEFT)
        
        # 🔊 Speaker button to repeat question
        self.speak_question_btn = tk.Button(
            question_header, text="🔊", font=("Arial", 16),
            bg="#3498db", fg="white", activebackground="#2980b9",
            relief=tk.RAISED, borderwidth=2, cursor="hand2",
            command=self._speak_current_question,
            state=tk.DISABLED
        )
        self.speak_question_btn.pack(side=tk.RIGHT, padx=5)
        
        self.voice_question_text = scrolledtext.ScrolledText(left_frame, height=10, width=40, 
                                                             font=("Arial", 12, "bold"), wrap=tk.WORD,
                                                             bg="#f9f9f9", relief=tk.FLAT)
        self.voice_question_text.pack(fill=tk.BOTH, expand=True)
        self.voice_question_text.config(state=tk.DISABLED)
        
        # ⏱️ Countdown timer (số to)
        self.countdown_label = tk.Label(left_frame, text="", font=("Arial", 48, "bold"), 
                                       fg="#e74c3c", bg="#f9f9f9")
        self.countdown_label.pack(pady=10)
        
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
        
        # Buttons at bottom - with pause button and increased height
        button_frame = ttk.Frame(self.voice_quiz_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create buttons with custom style for better visibility
        style = ttk.Style()
        style.configure('Voice.TButton', font=('Segoe UI', 11))
        
        self.voice_quiz_pause_btn = ttk.Button(
            button_frame, text="⏸️ TẠM DỪNG", 
            command=self._toggle_voice_quiz_pause, 
            width=20, style='Voice.TButton'
        )
        self.voice_quiz_pause_btn.pack(side=tk.LEFT, padx=5, ipady=8)
        
        ttk.Button(
            button_frame, text="⏭️ CÂU TIẾP", 
            command=self.voice_next_question, 
            width=20, style='Voice.TButton'
        ).pack(side=tk.LEFT, padx=5, ipady=8)
        
        ttk.Button(
            button_frame, text="❌ DỪNG", 
            command=self.voice_stop_quiz, 
            width=20, style='Voice.TButton'
        ).pack(side=tk.LEFT, padx=5, ipady=8)
    
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
    
    def _create_dashboard_tab(self):
        """📈 Tab Dashboard - Thống kê và biểu đồ tiến độ học tập"""
        main_frame = ttk.Frame(self.dashboard_tab, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="📈 Learning Dashboard", 
                 font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
        
        # Top Row: Stats Cards
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Card 1: Total Words
        card1 = tk.Frame(stats_frame, bg="#e3f2fd", relief=tk.RAISED, borderwidth=2)
        card1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(card1, text="📚", font=("Arial", 24), bg="#e3f2fd").pack(pady=(10,5))
        self.dashboard_total_label = tk.Label(card1, text="0", font=("Segoe UI", 28, "bold"), 
                                               bg="#e3f2fd", fg="#1565c0")
        self.dashboard_total_label.pack()
        tk.Label(card1, text="Tổng số từ", font=("Segoe UI", 10), bg="#e3f2fd").pack(pady=(0,10))
        
        # Card 2: Mastered
        card2 = tk.Frame(stats_frame, bg="#c8e6c9", relief=tk.RAISED, borderwidth=2)
        card2.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(card2, text="✅", font=("Arial", 24), bg="#c8e6c9").pack(pady=(10,5))
        self.dashboard_mastered_label = tk.Label(card2, text="0", font=("Segoe UI", 28, "bold"), 
                                                  bg="#c8e6c9", fg="#2e7d32")
        self.dashboard_mastered_label.pack()
        tk.Label(card2, text="Đã thành thạo", font=("Segoe UI", 10), bg="#c8e6c9").pack(pady=(0,10))
        
        # Card 3: In Progress
        card3 = tk.Frame(stats_frame, bg="#fff9c4", relief=tk.RAISED, borderwidth=2)
        card3.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(card3, text="📝", font=("Arial", 24), bg="#fff9c4").pack(pady=(10,5))
        self.dashboard_progress_label = tk.Label(card3, text="0", font=("Segoe UI", 28, "bold"), 
                                                  bg="#fff9c4", fg="#f57f17")
        self.dashboard_progress_label.pack()
        tk.Label(card3, text="Đang học", font=("Segoe UI", 10), bg="#fff9c4").pack(pady=(0,10))
        
        # Card 4: Weak
        card4 = tk.Frame(stats_frame, bg="#ffcdd2", relief=tk.RAISED, borderwidth=2)
        card4.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        tk.Label(card4, text="⚠️", font=("Arial", 24), bg="#ffcdd2").pack(pady=(10,5))
        self.dashboard_weak_label = tk.Label(card4, text="0", font=("Segoe UI", 28, "bold"), 
                                              bg="#ffcdd2", fg="#c62828")
        self.dashboard_weak_label.pack()
        tk.Label(card4, text="Cần ôn tập", font=("Segoe UI", 10), bg="#ffcdd2").pack(pady=(0,10))
        
        # Charts Container
        charts_frame = ttk.Frame(main_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left: Pie Chart Frame
        pie_frame = ttk.LabelFrame(charts_frame, text="📊 Phân bố mức độ thành thạo", padding=10)
        pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.pie_chart_canvas = tk.Canvas(pie_frame, bg="white", width=350, height=300)
        self.pie_chart_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right: Bar Chart Frame
        bar_frame = ttk.LabelFrame(charts_frame, text="📈 Tiến độ theo ngày", padding=10)
        bar_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        self.bar_chart_canvas = tk.Canvas(bar_frame, bg="white", width=350, height=300)
        self.bar_chart_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🔄 Cập nhật", 
                  command=self._refresh_dashboard, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Export Stats", 
                  command=self.export_smart_review_stats, width=15).pack(side=tk.LEFT, padx=5)
        
        # Initial draw
        self._draw_empty_charts()
    
    def _draw_empty_charts(self):
        """Vẽ biểu đồ trống ban đầu"""
        # Empty pie chart
        self.pie_chart_canvas.delete("all")
        self.pie_chart_canvas.create_text(175, 150, text="Chưa có dữ liệu\n\nHãy làm quiz trước!", 
                                          font=("Segoe UI", 12), fill="#888888", justify=tk.CENTER)
        
        # Empty bar chart
        self.bar_chart_canvas.delete("all")
        self.bar_chart_canvas.create_text(175, 150, text="Chưa có dữ liệu\n\nHãy làm quiz trước!", 
                                          font=("Segoe UI", 12), fill="#888888", justify=tk.CENTER)
    
    def _refresh_dashboard(self):
        """Cập nhật Dashboard với dữ liệu mới nhất"""
        if not self.smart_review_db:
            messagebox.showwarning("Cảnh báo", "⚠️ Smart Review chưa khởi tạo!")
            return
        
        try:
            user_name = "Default"
            file_path = str(self.selected_file) if hasattr(self, 'selected_file') and self.selected_file else ""
            
            # Get stats
            stats = self.smart_review_db.get_mastery_stats(file_path, user_name)
            
            # Update cards
            total = stats.get('total', 0)
            mastered = stats.get('mastered', 0)
            good = stats.get('good', 0) - mastered  # Good but not mastered
            weak = stats.get('weak', 0)
            
            self.dashboard_total_label.config(text=str(total))
            self.dashboard_mastered_label.config(text=str(mastered))
            self.dashboard_progress_label.config(text=str(good))
            self.dashboard_weak_label.config(text=str(weak))
            
            # Draw Pie Chart
            self._draw_pie_chart(mastered, good, weak)
            
            # Draw Bar Chart (progress over time)
            self._draw_bar_chart()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"❌ Không thể tải dữ liệu: {str(e)}")
    
    def _draw_pie_chart(self, mastered, good, weak):
        """Vẽ biểu đồ tròn phân bố mức độ"""
        self.pie_chart_canvas.delete("all")
        
        total = mastered + good + weak
        if total == 0:
            self.pie_chart_canvas.create_text(175, 150, text="Không có dữ liệu", 
                                              font=("Segoe UI", 12), fill="#888888")
            return
        
        # Pie chart parameters
        cx, cy = 175, 130
        radius = 100
        
        # Data
        data = [
            (mastered, "#4caf50", "Thành thạo"),
            (good, "#ffc107", "Đang học"),
            (weak, "#f44336", "Cần ôn")
        ]
        
        start_angle = 0
        for value, color, label in data:
            if value == 0:
                continue
            extent = (value / total) * 360
            
            # Draw slice
            self.pie_chart_canvas.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start_angle, extent=extent, fill=color, outline="white", width=2
            )
            
            # Draw label
            import math
            mid_angle = math.radians(start_angle + extent / 2)
            label_x = cx + (radius + 30) * math.cos(mid_angle)
            label_y = cy - (radius + 30) * math.sin(mid_angle)
            percent = int(value * 100 / total)
            self.pie_chart_canvas.create_text(label_x, label_y, 
                                              text=f"{label}\n{percent}%", 
                                              font=("Segoe UI", 9, "bold"), fill=color)
            
            start_angle += extent
        
        # Legend
        legend_y = 260
        for i, (value, color, label) in enumerate(data):
            x = 60 + i * 120
            self.pie_chart_canvas.create_rectangle(x-10, legend_y-5, x+10, legend_y+5, fill=color, outline="")
            self.pie_chart_canvas.create_text(x+40, legend_y, text=f"{label}: {value}", 
                                              font=("Segoe UI", 9), anchor=tk.W)
    
    def _draw_bar_chart(self):
        """Vẽ biểu đồ cột tiến độ theo ngày"""
        self.bar_chart_canvas.delete("all")
        
        # Get study sessions from database
        try:
            if not self.smart_review_db:
                raise Exception("No database")
            
            # Get last 7 days data
            import sqlite3
            from datetime import datetime, timedelta
            
            conn = sqlite3.connect(self.smart_review_db.db_path)
            cursor = conn.cursor()
            
            # Get daily stats for last 7 days
            days_data = []
            for i in range(6, -1, -1):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                cursor.execute("""
                    SELECT COUNT(*) FROM question_history 
                    WHERE DATE(last_attempt_date) = ?
                """, (date,))
                count = cursor.fetchone()[0]
                days_data.append((date[-5:], count))  # MM-DD format
            
            conn.close()
            
            if not any(d[1] for d in days_data):
                self.bar_chart_canvas.create_text(175, 150, text="Chưa có hoạt động\n\nHãy làm quiz!", 
                                                  font=("Segoe UI", 12), fill="#888888", justify=tk.CENTER)
                return
            
            # Draw bars
            max_val = max(d[1] for d in days_data) or 1
            bar_width = 35
            gap = 10
            start_x = 30
            chart_height = 200
            bottom_y = 250
            
            for i, (label, value) in enumerate(days_data):
                x = start_x + i * (bar_width + gap)
                bar_height = (value / max_val) * chart_height if max_val > 0 else 0
                
                # Bar
                color = "#2196f3" if i < 6 else "#4caf50"  # Today is green
                self.bar_chart_canvas.create_rectangle(
                    x, bottom_y - bar_height, x + bar_width, bottom_y,
                    fill=color, outline=""
                )
                
                # Value on top
                if value > 0:
                    self.bar_chart_canvas.create_text(
                        x + bar_width/2, bottom_y - bar_height - 10,
                        text=str(value), font=("Segoe UI", 9, "bold"), fill=color
                    )
                
                # Date label
                self.bar_chart_canvas.create_text(
                    x + bar_width/2, bottom_y + 15,
                    text=label, font=("Segoe UI", 8), fill="#666666"
                )
            
            # Y axis
            self.bar_chart_canvas.create_line(25, 30, 25, bottom_y, fill="#cccccc", width=1)
            
        except Exception as e:
            self.bar_chart_canvas.create_text(175, 150, text=f"Lỗi: {str(e)}", 
                                              font=("Segoe UI", 10), fill="#f44336")
    
    def _create_results_tab(self):
        """Tab Results với Top Scores"""
        # Top frame: Buttons
        button_frame = ttk.Frame(self.results_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="💾 Lưu kết quả", command=self.save_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📂 Xem kết quả cũ", command=self.load_previous_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Kiểm tra lại", command=self.restart_quiz).pack(side=tk.LEFT, padx=5)
        
        # 📊 Smart Review Stats button
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(button_frame, text="📊 Smart Review Stats", 
                  command=self.export_smart_review_stats,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        # Container split: Results + Leaderboard
        content_frame = ttk.Frame(self.results_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        # Left: Results text
        results_frame = ttk.LabelFrame(content_frame, text="📋 Kết quả chi tiết", padding=5)
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, font=("Arial", 10), wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.config(state=tk.DISABLED)
        
        # Right: Leaderboard
        leaderboard_frame = ttk.LabelFrame(content_frame, text="🏆 Top Điểm Cao", padding=10)
        leaderboard_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5,0), ipadx=10)
        
        # Leaderboard listbox
        self.leaderboard_list = tk.Listbox(
            leaderboard_frame, font=("Courier New", 10), 
            bg="#fffef0", width=35, height=20
        )
        self.leaderboard_list.pack(fill=tk.BOTH, expand=True)
        
        # Load leaderboard
        self._load_leaderboard()
    
    def _create_practice_tab(self):
        """Tab Multiple Choice Practice - luyện tập không cần micro"""
        # Container chính
        main_frame = ttk.Frame(self.practice_tab, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title - nhỏ gọn
        title_label = ttk.Label(main_frame, text="📱 Multiple Choice Practice", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 5))
        
        # Settings Frame - COMPACT
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Cài đặt", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Row 1: File, Type, Range - ALL IN ONE ROW
        compact_row = ttk.Frame(settings_frame)
        compact_row.pack(fill=tk.X, pady=3)
        
        ttk.Label(compact_row, text="File:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.practice_file_label = ttk.Label(compact_row, text="Chưa chọn", 
                                             foreground="#2196f3", font=("Segoe UI", 9))
        self.practice_file_label.pack(side=tk.LEFT, padx=(3,10))
        ttk.Button(compact_row, text="📂 Chọn File", command=self._practice_select_file, 
                  width=10).pack(side=tk.RIGHT, padx=2)
        ttk.Button(compact_row, text="▶️ Bắt Đầu Practice", command=self._start_practice_quiz, 
                  style="Accent.TButton", width=18).pack(side=tk.RIGHT, padx=2)
        
        # Row 2: Quiz Type + Range + Pause
        type_range_row = ttk.Frame(settings_frame)
        type_range_row.pack(fill=tk.X, pady=3)
        
        ttk.Label(type_range_row, text="Loại:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.practice_quiz_type_var = tk.StringVar(value="meaning")
        ttk.Radiobutton(type_range_row, text="💬 Nghĩa từ", variable=self.practice_quiz_type_var, 
                       value="meaning").pack(side=tk.LEFT, padx=3)
        ttk.Radiobutton(type_range_row, text="📝 Dịch câu", variable=self.practice_quiz_type_var, 
                       value="example").pack(side=tk.LEFT, padx=3)
        
        ttk.Label(type_range_row, text="   Câu:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.practice_start_var = tk.IntVar(value=1)
        ttk.Spinbox(type_range_row, from_=1, to=1000, textvariable=self.practice_start_var, 
                   width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(type_range_row, text="-", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.practice_end_var = tk.IntVar(value=10)
        ttk.Spinbox(type_range_row, from_=1, to=1000, textvariable=self.practice_end_var, 
                   width=5).pack(side=tk.LEFT, padx=2)
        
        # Pause button
        self.practice_pause_btn = tk.Button(
            type_range_row, text="⏸️ Tạm dừng", font=("Segoe UI", 9),
            bg="#ff9800", fg="white", command=self._toggle_practice_pause,
            state=tk.DISABLED, cursor="hand2", width=12
        )
        self.practice_pause_btn.pack(side=tk.RIGHT, padx=5)
        
        # Progress Frame - compact
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Progress label and timer on same row
        progress_row = ttk.Frame(progress_frame)
        progress_row.pack(fill=tk.X)
        
        self.practice_progress_label = ttk.Label(progress_row, text="Chưa bắt đầu", 
                                                 font=("Segoe UI", 10))
        self.practice_progress_label.pack(side=tk.LEFT)
        
        # Timer label (countdown)
        self.practice_timer_label = ttk.Label(progress_row, text="", 
                                              font=("Segoe UI", 10, "bold"),
                                              foreground="#ff5722")
        self.practice_timer_label.pack(side=tk.RIGHT)
        
        self.practice_progress_bar = ttk.Progressbar(progress_frame, mode='determinate', 
                                                     length=600)
        self.practice_progress_bar.pack(fill=tk.X, pady=5)
        
        # Question Frame - COMPACT KHÔNG CUỘN
        question_frame = ttk.LabelFrame(main_frame, text="❓ Câu hỏi", padding=8)
        question_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Header row with speaker button
        question_header = ttk.Frame(question_frame)
        question_header.pack(fill=tk.X, pady=(0,5))
        
        self.practice_speak_btn = tk.Button(
            question_header, text="🔊", font=("Arial", 14),
            bg="#3498db", fg="white",
            command=self._speak_practice_question,
            state=tk.DISABLED, cursor="hand2"
        )
        self.practice_speak_btn.pack(side=tk.LEFT, padx=3)
        
        # Question text - Dùng Label thay vì ScrolledText
        self.practice_question_label = tk.Label(
            question_frame, 
            text="",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f8ff", fg="#1565c0",
            wraplength=1300, justify=tk.LEFT,
            padx=10, pady=10, anchor=tk.W
        )
        self.practice_question_label.pack(fill=tk.X)
        
        # Answer Buttons Frame (4 buttons in 2x2 grid)
        answers_frame = ttk.LabelFrame(main_frame, text="🎯 Chọn đáp án", padding=10)
        answers_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Grid configuration
        answers_frame.columnconfigure(0, weight=1)
        answers_frame.columnconfigure(1, weight=1)
        answers_frame.rowconfigure(0, weight=1)
        answers_frame.rowconfigure(1, weight=1)
        
        # A and B buttons (first row)
        self.practice_btn_a = tk.Button(
            answers_frame, text="A", font=("Segoe UI", 11),
            bg="#bbdefb", fg="#000000", activebackground="#64b5f6", activeforeground="#000000",
            relief=tk.RAISED, borderwidth=2,
            command=lambda: self._practice_submit_answer("A"), state=tk.DISABLED,
            cursor="hand2", wraplength=650, justify=tk.LEFT, padx=8, pady=5
        )
        self.practice_btn_a.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        
        self.practice_btn_b = tk.Button(
            answers_frame, text="B", font=("Segoe UI", 11),
            bg="#c8e6c9", fg="#000000", activebackground="#81c784", activeforeground="#000000",
            relief=tk.RAISED, borderwidth=2,
            command=lambda: self._practice_submit_answer("B"), state=tk.DISABLED,
            cursor="hand2", wraplength=650, justify=tk.LEFT, padx=8, pady=5
        )
        self.practice_btn_b.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)
        
        # C and D buttons (second row)
        self.practice_btn_c = tk.Button(
            answers_frame, text="C", font=("Segoe UI", 11),
            bg="#ffe0b2", fg="#000000", activebackground="#ffb74d", activeforeground="#000000",
            relief=tk.RAISED, borderwidth=2,
            command=lambda: self._practice_submit_answer("C"), state=tk.DISABLED,
            cursor="hand2", wraplength=650, justify=tk.LEFT, padx=8, pady=5
        )
        self.practice_btn_c.grid(row=1, column=0, sticky="nsew", padx=3, pady=3)
        
        self.practice_btn_d = tk.Button(
            answers_frame, text="D", font=("Segoe UI", 11),
            bg="#f8bbd0", fg="#000000", activebackground="#f06292", activeforeground="#000000",
            relief=tk.RAISED, borderwidth=2,
            command=lambda: self._practice_submit_answer("D"), state=tk.DISABLED,
            cursor="hand2", wraplength=650, justify=tk.LEFT, padx=8, pady=5
        )
        self.practice_btn_d.grid(row=1, column=1, sticky="nsew", padx=3, pady=3)
        
        # Feedback Frame
        feedback_frame = ttk.LabelFrame(main_frame, text="💬 Phản hồi", padding=5)
        feedback_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.practice_feedback_text = scrolledtext.ScrolledText(
            feedback_frame, 
            wrap=tk.WORD, 
            height=2,
            font=("Segoe UI", 10),
            bg="#fffef0",
            state=tk.DISABLED
        )
        self.practice_feedback_text.pack(fill=tk.BOTH, expand=True)
        
        # ⌨️ Keyboard shortcuts hint
        keyboard_hint = ttk.Label(main_frame, 
                                  text="⌨️ Phím tắt: A, B, C, D", 
                                  font=("Segoe UI", 9, "italic"),
                                  foreground="gray")
        keyboard_hint.pack(pady=(5, 0))
        
        # Bind keyboard events for A/B/C/D
        self.practice_tab.bind("<KeyPress-a>", lambda e: self._practice_submit_answer("A") if self.practice_btn_a['state'] == tk.NORMAL else None)
        self.practice_tab.bind("<KeyPress-A>", lambda e: self._practice_submit_answer("A") if self.practice_btn_a['state'] == tk.NORMAL else None)
        self.practice_tab.bind("<KeyPress-b>", lambda e: self._practice_submit_answer("B") if self.practice_btn_b['state'] == tk.NORMAL else None)
        self.practice_tab.bind("<KeyPress-B>", lambda e: self._practice_submit_answer("B") if self.practice_btn_b['state'] == tk.NORMAL else None)
        self.practice_tab.bind("<KeyPress-c>", lambda e: self._practice_submit_answer("C") if self.practice_btn_c['state'] == tk.NORMAL else None)
        self.practice_tab.bind("<KeyPress-C>", lambda e: self._practice_submit_answer("C") if self.practice_btn_c['state'] == tk.NORMAL else None)
        self.practice_tab.bind("<KeyPress-d>", lambda e: self._practice_submit_answer("D") if self.practice_btn_d['state'] == tk.NORMAL else None)
        self.practice_tab.bind("<KeyPress-D>", lambda e: self._practice_submit_answer("D") if self.practice_btn_d['state'] == tk.NORMAL else None)
        
        # Focus tab when clicked to enable keyboard shortcuts
        self.practice_tab.focus_set()
        
        # 📂 Load practice file from settings
        if "practice_file" in self.user_settings and self.user_settings["practice_file"]:
            practice_file = self.user_settings["practice_file"]
            if Path(practice_file).exists():
                self.practice_selected_file = practice_file
                self.practice_file_label.config(
                    text=Path(practice_file).name,
                    foreground="green"
                )
        
        # 📂 Load flashcard file from settings
        if "flashcard_file" in self.user_settings and self.user_settings["flashcard_file"]:
            flashcard_file = self.user_settings["flashcard_file"]
            if Path(flashcard_file).exists():
                self.flashcard_file = flashcard_file
    
    def _create_flashcard_tab(self):
        """🃏 Tab Flashcard Mode - Học từ với thẻ lật"""
        main_frame = ttk.Frame(self.flashcard_tab, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="🃏 Flashcard Mode", 
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))
        
        # Settings Row
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Cài đặt", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        settings_row = ttk.Frame(settings_frame)
        settings_row.pack(fill=tk.X)
        
        ttk.Label(settings_row, text="File:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        
        # Hiển thị tên file đã lưu nếu có
        saved_file = self.user_settings.get("flashcard_file", "")
        if saved_file and Path(saved_file).exists():
            display_name = Path(saved_file).name
            display_color = "green"
        else:
            display_name = "Chưa chọn"
            display_color = "#2196f3"
        
        self.flashcard_file_label = ttk.Label(settings_row, text=display_name, 
                                               foreground=display_color, font=("Segoe UI", 9))
        self.flashcard_file_label.pack(side=tk.LEFT, padx=(3, 10))
        ttk.Button(settings_row, text="📂 Chọn File", 
                  command=self._flashcard_select_file, width=10).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(settings_row, text="   Câu:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.flashcard_start_var = tk.IntVar(value=1)
        ttk.Spinbox(settings_row, from_=1, to=1000, textvariable=self.flashcard_start_var, 
                   width=5).pack(side=tk.LEFT, padx=2)
        ttk.Label(settings_row, text="-").pack(side=tk.LEFT)
        self.flashcard_end_var = tk.IntVar(value=20)
        ttk.Spinbox(settings_row, from_=1, to=1000, textvariable=self.flashcard_end_var, 
                   width=5).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(settings_row, text="▶️ Bắt Đầu", 
                  command=self._start_flashcard, width=12).pack(side=tk.RIGHT, padx=3)
        
        # Progress Row
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.flashcard_progress_label = ttk.Label(progress_frame, text="Chưa bắt đầu", 
                                                   font=("Segoe UI", 10))
        self.flashcard_progress_label.pack(side=tk.LEFT)
        
        self.flashcard_stats_label = ttk.Label(progress_frame, text="", 
                                                font=("Segoe UI", 10, "bold"),
                                                foreground="#4caf50")
        self.flashcard_stats_label.pack(side=tk.RIGHT)
        
        self.flashcard_progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=600)
        self.flashcard_progress_bar.pack(fill=tk.X, pady=3)
        
        # ============ FLASHCARD DISPLAY ============
        card_frame = ttk.Frame(main_frame)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # The Card (clickable to flip)
        self.flashcard_canvas = tk.Canvas(card_frame, bg="#ffffff", highlightthickness=2,
                                          highlightbackground="#3498db", cursor="hand2")
        self.flashcard_canvas.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # Card content - Front (Word)
        self.flashcard_front_frame = tk.Frame(self.flashcard_canvas, bg="#e3f2fd")
        self.flashcard_front_label = tk.Label(
            self.flashcard_front_frame, text="Click để bắt đầu",
            font=("Segoe UI", 28, "bold"), bg="#e3f2fd", fg="#1565c0",
            wraplength=600, justify=tk.CENTER
        )
        self.flashcard_front_label.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
        
        # Speaker button for front
        self.flashcard_speak_btn = tk.Button(
            self.flashcard_front_frame, text="🔊", font=("Arial", 20),
            bg="#3498db", fg="white", command=self._speak_flashcard_word,
            cursor="hand2"
        )
        self.flashcard_speak_btn.pack(pady=10)
        
        # Card content - Back (Meaning + Example)
        self.flashcard_back_frame = tk.Frame(self.flashcard_canvas, bg="#e8f5e9")
        self.flashcard_meaning_label = tk.Label(
            self.flashcard_back_frame, text="",
            font=("Segoe UI", 18, "bold"), bg="#e8f5e9", fg="#2e7d32",
            wraplength=600, justify=tk.CENTER
        )
        self.flashcard_meaning_label.pack(expand=True, pady=10)
        
        self.flashcard_example_label = tk.Label(
            self.flashcard_back_frame, text="",
            font=("Segoe UI", 14), bg="#e8f5e9", fg="#555555",
            wraplength=600, justify=tk.CENTER
        )
        self.flashcard_example_label.pack(expand=True, pady=10)
        
        # Show front initially
        self.flashcard_front_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Bind click to flip
        self.flashcard_canvas.bind("<Button-1>", self._flip_flashcard)
        self.flashcard_front_frame.bind("<Button-1>", self._flip_flashcard)
        self.flashcard_front_label.bind("<Button-1>", self._flip_flashcard)
        
        # ============ CONTROL BUTTONS ============
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Navigation buttons
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT, padx=10)
        
        self.flashcard_prev_btn = tk.Button(
            nav_frame, text="⬅️ Trước", font=("Segoe UI", 12, "bold"),
            bg="#90a4ae", fg="white", command=self._flashcard_prev,
            state=tk.DISABLED, width=10, cursor="hand2"
        )
        self.flashcard_prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.flashcard_flip_btn = tk.Button(
            nav_frame, text="🔄 Lật thẻ", font=("Segoe UI", 12, "bold"),
            bg="#9c27b0", fg="white", command=lambda: self._flip_flashcard(None),
            state=tk.DISABLED, width=10, cursor="hand2"
        )
        self.flashcard_flip_btn.pack(side=tk.LEFT, padx=5)
        
        self.flashcard_next_btn = tk.Button(
            nav_frame, text="Tiếp ➡️", font=("Segoe UI", 12, "bold"),
            bg="#90a4ae", fg="white", command=self._flashcard_next,
            state=tk.DISABLED, width=10, cursor="hand2"
        )
        self.flashcard_next_btn.pack(side=tk.LEFT, padx=5)
        
        # Known/Unknown buttons
        rating_frame = ttk.Frame(control_frame)
        rating_frame.pack(side=tk.RIGHT, padx=10)
        
        self.flashcard_unknown_btn = tk.Button(
            rating_frame, text="❌ Chưa thuộc", font=("Segoe UI", 12, "bold"),
            bg="#f44336", fg="white", command=lambda: self._rate_flashcard(False),
            state=tk.DISABLED, width=12, cursor="hand2"
        )
        self.flashcard_unknown_btn.pack(side=tk.LEFT, padx=5)
        
        self.flashcard_known_btn = tk.Button(
            rating_frame, text="✅ Đã thuộc", font=("Segoe UI", 12, "bold"),
            bg="#4caf50", fg="white", command=lambda: self._rate_flashcard(True),
            state=tk.DISABLED, width=12, cursor="hand2"
        )
        self.flashcard_known_btn.pack(side=tk.LEFT, padx=5)
        
        # Keyboard shortcuts info
        shortcut_label = ttk.Label(main_frame, 
            text="⌨️ Phím tắt: Space=Lật | ←/→=Trước/Sau | K=Thuộc | U=Chưa thuộc",
            font=("Segoe UI", 9), foreground="#888888")
        shortcut_label.pack(pady=5)
        
        # Bind keyboard shortcuts
        self.root.bind("<space>", lambda e: self._flip_flashcard(None) if self.notebook.index(self.notebook.select()) == 3 else None)
        self.root.bind("<Left>", lambda e: self._flashcard_prev() if self.notebook.index(self.notebook.select()) == 3 else None)
        self.root.bind("<Right>", lambda e: self._flashcard_next() if self.notebook.index(self.notebook.select()) == 3 else None)
        self.root.bind("<k>", lambda e: self._rate_flashcard(True) if self.notebook.index(self.notebook.select()) == 3 else None)
        self.root.bind("<u>", lambda e: self._rate_flashcard(False) if self.notebook.index(self.notebook.select()) == 3 else None)
    
    def _flashcard_select_file(self):
        """Chọn file Excel cho Flashcard"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")],
            initialdir=str(Path(__file__).parent / "data")
        )
        if file_path:
            self.flashcard_file = file_path
            self.flashcard_file_label.config(text=Path(file_path).name, foreground="green")
            # Lưu vào settings
            self.user_settings["flashcard_file"] = file_path
            self._save_settings()
    
    def _start_flashcard(self):
        """Bắt đầu Flashcard session"""
        if not hasattr(self, 'flashcard_file') or not self.flashcard_file:
            messagebox.showwarning("Cảnh báo", "⚠️ Vui lòng chọn file Excel trước!")
            return
        
        try:
            # Load data from Excel
            from openpyxl import load_workbook
            wb = load_workbook(self.flashcard_file, data_only=True)
            ws = wb.active
            
            # Đọc header để xác định cấu trúc cột
            header_row = [str(cell.value).lower() if cell.value else "" for cell in ws[1]]
            
            # Tìm cột word (có thể là cột B nếu cột A là số thứ tự)
            word_col = 0
            meaning_col = 1
            example_en_col = 2
            example_vi_col = 3
            
            # Check if first column is number (STT)
            for i, h in enumerate(header_row):
                if any(kw in h for kw in ['word', 'từ', '単語', '词', 'vocabulary']):
                    word_col = i
                    meaning_col = i + 1
                    example_en_col = i + 2
                    example_vi_col = i + 3
                    break
            
            # Nếu cột A là số hoặc "stt", bắt đầu từ cột B
            if header_row[0] in ['stt', 'no', 'no.', 'số', '#', ''] or header_row[0].isdigit():
                word_col = 1
                meaning_col = 2
                example_en_col = 3
                example_vi_col = 4
            
            start_row = self.flashcard_start_var.get() + 1  # +1 for header
            end_row = self.flashcard_end_var.get() + 1
            
            self.flashcard_data = []
            for row in ws.iter_rows(min_row=start_row, max_row=end_row, values_only=True):
                word_val = row[word_col] if len(row) > word_col else None
                if word_val:  # Has word
                    self.flashcard_data.append({
                        "word": str(word_val) if word_val else "",
                        "meaning": str(row[meaning_col]) if len(row) > meaning_col and row[meaning_col] else "",
                        "example_en": str(row[example_en_col]) if len(row) > example_en_col and row[example_en_col] else "",
                        "example_vi": str(row[example_vi_col]) if len(row) > example_vi_col and row[example_vi_col] else "",
                        "known": False
                    })
            
            if not self.flashcard_data:
                messagebox.showwarning("Cảnh báo", "⚠️ Không có dữ liệu trong phạm vi đã chọn!")
                return
            
            # Reset state
            self.flashcard_current_idx = 0
            self.flashcard_showing_answer = False
            self.flashcard_known_count = 0
            self.flashcard_unknown_count = 0
            
            # Enable buttons
            self.flashcard_prev_btn.config(state=tk.NORMAL)
            self.flashcard_flip_btn.config(state=tk.NORMAL)
            self.flashcard_next_btn.config(state=tk.NORMAL)
            self.flashcard_known_btn.config(state=tk.NORMAL)
            self.flashcard_unknown_btn.config(state=tk.NORMAL)
            
            # Display first card
            self._display_flashcard()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"❌ Không thể đọc file: {str(e)}")
    
    def _display_flashcard(self):
        """Hiển thị thẻ flashcard hiện tại"""
        if not self.flashcard_data:
            return
        
        card = self.flashcard_data[self.flashcard_current_idx]
        
        # Update progress
        current = self.flashcard_current_idx + 1
        total = len(self.flashcard_data)
        self.flashcard_progress_label.config(text=f"Thẻ {current}/{total}")
        self.flashcard_progress_bar['value'] = (current / total) * 100
        
        # Update stats
        self.flashcard_stats_label.config(
            text=f"✅ {self.flashcard_known_count}  |  ❌ {self.flashcard_unknown_count}"
        )
        
        # Update card content
        self.flashcard_front_label.config(text=card["word"])
        self.flashcard_meaning_label.config(text=f"💬 {card['meaning']}")
        
        example_text = ""
        if card["example_en"]:
            example_text = f"📝 {card['example_en']}"
        if card["example_vi"]:
            example_text += f"\n🔄 {card['example_vi']}"
        self.flashcard_example_label.config(text=example_text)
        
        # Show front side
        self.flashcard_showing_answer = False
        self.flashcard_front_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.flashcard_back_frame.place_forget()
        
        # Update card background based on known status
        if card.get("known"):
            self.flashcard_front_frame.config(bg="#c8e6c9")
            self.flashcard_front_label.config(bg="#c8e6c9", fg="#2e7d32")
        else:
            self.flashcard_front_frame.config(bg="#e3f2fd")
            self.flashcard_front_label.config(bg="#e3f2fd", fg="#1565c0")
    
    def _flip_flashcard(self, event):
        """Lật thẻ flashcard"""
        if not self.flashcard_data:
            return
        
        if self.flashcard_showing_answer:
            # Show front
            self.flashcard_front_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.flashcard_back_frame.place_forget()
        else:
            # Show back
            self.flashcard_back_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.flashcard_front_frame.place_forget()
        
        self.flashcard_showing_answer = not self.flashcard_showing_answer
    
    def _flashcard_prev(self):
        """Chuyển về thẻ trước"""
        if self.flashcard_current_idx > 0:
            self.flashcard_current_idx -= 1
            self._display_flashcard()
    
    def _flashcard_next(self):
        """Chuyển sang thẻ tiếp theo"""
        if self.flashcard_current_idx < len(self.flashcard_data) - 1:
            self.flashcard_current_idx += 1
            self._display_flashcard()
        else:
            # End of deck - show summary
            self._show_flashcard_summary()
    
    def _rate_flashcard(self, known: bool):
        """Đánh giá thẻ: đã thuộc hoặc chưa thuộc"""
        if not self.flashcard_data:
            return
        
        card = self.flashcard_data[self.flashcard_current_idx]
        
        # Update count
        if known and not card.get("known"):
            self.flashcard_known_count += 1
            if card.get("marked_unknown"):
                self.flashcard_unknown_count -= 1
        elif not known and not card.get("marked_unknown"):
            self.flashcard_unknown_count += 1
            if card.get("known"):
                self.flashcard_known_count -= 1
        
        card["known"] = known
        card["marked_unknown"] = not known
        
        # Auto next
        self._flashcard_next()
    
    def _show_flashcard_summary(self):
        """Hiển thị tổng kết Flashcard session"""
        total = len(self.flashcard_data)
        known = self.flashcard_known_count
        unknown = self.flashcard_unknown_count
        not_rated = total - known - unknown
        
        summary = f"""
🎉 HOÀN THÀNH FLASHCARD SESSION!

📊 Kết quả:
   ✅ Đã thuộc: {known}/{total} ({known*100//total if total > 0 else 0}%)
   ❌ Chưa thuộc: {unknown}/{total} ({unknown*100//total if total > 0 else 0}%)
   ⏭️ Bỏ qua: {not_rated}/{total}

💡 Mẹo: Ôn lại các từ chưa thuộc thường xuyên!
"""
        messagebox.showinfo("🃏 Flashcard - Kết quả", summary)
    
    def _speak_flashcard_word(self):
        """Phát âm từ trong flashcard - hỗ trợ nhiều ngôn ngữ"""
        if not self.flashcard_data:
            return
        
        card = self.flashcard_data[self.flashcard_current_idx]
        word = card.get("word", "")
        
        if not word:
            return
        
        # Xác định ngôn ngữ từ tên file
        file_name = getattr(self, 'flashcard_file', '').lower()
        if 'chinese' in file_name or 'zh' in file_name or 'hán' in file_name:
            lang_code = "zh-cn"
        elif 'japanese' in file_name or 'ja' in file_name or 'nhật' in file_name:
            lang_code = "ja"
        else:
            lang_code = "en"
        
        def speak_async():
            try:
                from gtts import gTTS
                import tempfile
                import os
                from pygame import mixer
                
                # Get speed
                speed = getattr(self, 'voice_speed_var', None)
                slow = speed.get() < 0.8 if speed else False
                
                tts = gTTS(text=word, lang=lang_code, slow=slow)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    temp_path = f.name
                tts.save(temp_path)
                
                mixer.init()
                mixer.music.load(temp_path)
                mixer.music.play()
                while mixer.music.get_busy():
                    import time
                    time.sleep(0.1)
                mixer.quit()
                os.unlink(temp_path)
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
                # Fallback to winsound beep
                try:
                    import winsound
                    winsound.Beep(440, 200)
                except:
                    pass
        
        import threading
        threading.Thread(target=speak_async, daemon=True).start()
    
    def _create_guide_tab(self):
        """⚡ Tab hướng dẫn chi tiết"""
        # Main container with logo on right
        main_container = ttk.Frame(self.guide_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Right side - Logo
        right_frame = ttk.Frame(main_container)
        right_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        try:
            logo_path = Path(__file__).parent / "logo.bmp"
            if logo_path.exists():
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                # Resize to larger size for guide tab
                logo_img = logo_img.resize((120, 120), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = ttk.Label(right_frame, image=logo_photo)
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(pady=(10, 0))
                
                # App name below logo
                app_name = ttk.Label(right_frame, 
                                    text="Language Quiz\nv2.2", 
                                    font=("Segoe UI", 11, "bold"),
                                    justify=tk.CENTER,
                                    foreground="#2c3e50")
                app_name.pack(pady=(10, 0))
        except Exception as e:
            print(f"⚠️ Không load được logo: {e}")
        
        # Left side - Guide content
        guide_container = ttk.Frame(main_container)
        guide_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        guide_text = scrolledtext.ScrolledText(
            guide_container, 
            wrap=tk.WORD, 
            font=("Segoe UI", 10),
            bg="#f9f9f9",
            padx=20,
            pady=20
        )
        guide_text.pack(fill=tk.BOTH, expand=True)
        
        # Guide content
        content = """🎓 HƯỚNG DẪN SỬ DỤNG LANGUAGE QUIZ v2.2
══════════════════════════════════════════════════════════════

📝 CÁC BƯỚC CƠ BẢN:

1️⃣ CHỌN FILE VÀ SHEET:
   - Nhấn "Chon File Excel" để chọn file từ vựng của bạn
   - Chọn sheet từ dropdown (ví dụ: "English", "Chinese H3p2", v.v.)
   - File Excel cần có các cột: No.	Word	Meaning	Example EN	Example VI
   - File chuẩn trên rồi thì k cần convert. 
   - Các file excel chưa convert (import sẽ tự động Convert) phải có định dạng kiểu : B1-từ vựng B2- nghĩa tiếng việt của từ đó
       D1-câu tương ứng với từ ở B1, D2- nghĩa tiếng Việt của câu đó. Tiếp cứ như vậy :
       B3-từ vựng B4- nghĩa tiếng việt của từ đó
       D3-câu tương ứng với từ ở B1, D4- nghĩa tiếng Việt của câu đó. Tiếp cứ như vậy :.................
2️⃣ KIỂM TRA MICROPHONE:
   - Chọn microphone từ danh sách
   - Nhấn "Test (5s)" để kiểm tra mic hoạt động
   - Nói to vào mic, thanh xanh sẽ nén lên nếu mic hoạt động tốt

3️⃣ CHỌN CẤU HÌNH QUIZ:

   🎯 Loại câu hỏi:
   • Nghĩa từ: Dịch từ vựng đơn (mặc định 4 giây)
   • Dịch câu: Dịch câu hoàn chỉnh (mặc định 12 giây)
   • VN→EN: Dịch từ tiếng Việt sang tiếng Anh

   ⏱️ Chế độ thời gian:
   • 📌 Thủ công: Thời gian cố định cho toàn bài (tùy chỉnh được)
   • 🤖 Tự động: Chatbot tính thời gian cho từng câu dựa vào độ dài đáp án
   
   📝 Phạm vi câu hỏi:
   • Từ câu: Bắt đầu từ câu số mấy (mặc định: 1)
   • Đến câu: Kết thúc ở câu số mấy (mặc định: 10)
   • 🔀 Trộn câu hỏi: Tạo thứ tự ngẫu nhiên

4️⃣ CHỌN CHẾ ĐỘ VOICE QUIZ:

   🎤 Mode 1: Bot đọc VN → User nói EN/CN/JP
   - Chatbot đọc tiếng Việt
   - Bạn trả lời bằng tiếng Anh/Trung/Nhật
   
   🎤 Mode 2: Bot đọc EN/CN/JP → User nói VN
   - Chatbot đọc tiếng nước ngoài
   - Bạn trả lời bằng tiếng Việt

5️⃣ CHỌN GIỌNG ĐỌC & NGÔN NGỮ CHATBOT:

   🔊 Giọng đọc:
   • English: Nữ (Joanna) hoặc Nam (Matthew)
   • 日本語: Nữ (Mizuki) hoặc Nam (Takumi)
   
   🤖 Ngôn ngữ Chatbot:
   • Tiếng Việt: Hướng dẫn và phản hồi bằng tiếng Việt
   • Tiếng Anh: Instructions and feedback in English
   • Tiếng Trung: 中文说明和反馈
   • Tiếng Nhật: 日本語での説明とフィードバック

6️⃣ BẮT ĐẦU VOICE QUIZ:

   • Nhấn nút "🎤 VOICE QUIZ"
   • Chatbot sẽ:
     1. Đọc hướng dẫn (1 lần, bằng ngôn ngữ chatbot đã chọn)
     2. Đọc câu hỏi (tiếng Việt hoặc tiếng nước ngoài)
     3. Phát beep sound để báo hiệu
     4. Bắt đầu đếm ngược thời gian
     5. Lắng nghe câu trả lời của bạn
   
   • NÓI TO VÀO MIC khi thấy số đếm ngược!
   • Câu trả lời sẽ được hiển thị ngay sau khi nhận dạng

⭐ TÍNH NĂNG ĐẶC BIỆT:

🎯 Chế độ Quiz:
   • 📖 Normal: Kiểm tra toàn bộ từ trong phạm vi đã chọn
   • 🎯 Practice: Ôn tập từ yếu (dựa vào lịch sử làm bài)

⚡ Phản hồi nhanh:
   • Tích vào "Phản hồi nhanh (chỉ text, bỏ TTS)"
   • Chỉ hiển thị text, không phát giọng nói phản hồi
   • Tiết kiệm thời gian cho bài kiểm tra nhanh

📊 Kết quả:
   • Sau khi hoàn thành quiz, nhập tên để lưu kết quả
   • Chatbot sẽ phát phản hồi theo điểm số:
     - ≥ 90%: "Xuất sắc!" / "Excellent!" / "太棒了！" / "素晴らしい！"
     - ≥ 75%: "Tốt lắm!" / "Good job!" / "很好！" / "良くできました！"
     - ≥ 60%: "Khá đấy!" / "Not bad!" / "不错！" / "悪くないです！"
     - < 60%: "Cần cố gắng hơn!" / "Need more effort!"
   • Kết quả được lưu vào file JSON
   • Ảnh từ camera (nếu có) sẽ được gửi lên Discord

══════════════════════════════════════════════════════════════

🔧 KHẮC PHỤC SỰ CỐ PHỔ BIẾN:

❌ Microphone không hoạt động:
   1. Kiểm tra kết nối microphone
   2. Thử Test mic trước khi bắt đầu
   3. Chọn microphone khác từ danh sách
   4. Kiểm tra Windows Sound Settings

❌ Không nhận dạng được giọng nói:
   1. NÓI TO HƠN vào mic
   2. Phát âm rõ ràng, từ từ
   3. Giảm tiếng ồn xung quanh
   4. Mic nên cách miệng 5-10cm

❌ File Excel bị lỗi:
   1. Đảm bảo file có các cột: word, meaning, example_en, example_vi
   2. Không để dòng trống ở giữa dữ liệu
   3. Lưu file dạng .xlsx (Excel 2007+)

❌ Chatbot phát âm không chuẩn:
   1. Đổi sang giọng AWS Polly (cho Anh/Trung/Nhật)
   2. Chọn giọng nam hoặc nữ tùy thích
   3. Kiểm tra kết nối internet (cho gTTS)

══════════════════════════════════════════════════════════════

� CẤU TRÚC FILE EXCEL MẪU:

┌─────────┬─────────────┬──────────────────┬──────────────────┬──────────────────┐
│ No.     │ Word        │ Meaning          │ Example EN       │ Example VI       │
├─────────┼─────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 1       │ hello       │ xin chào         │ Hello, how are   │ Xin chào, bạn    │
│         │             │                  │ you?             │ khỏe không?      │
├─────────┼─────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 2       │ thank you   │ cảm ơn           │ Thank you very   │ Cảm ơn bạn rất   │
│         │             │                  │ much             │ nhiều            │
├─────────┼─────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 3       │ goodbye     │ tạm biệt         │ Goodbye, see you │ Tạm biệt, hẹn    │
│         │             │                  │ later            │ gặp lại          │
└─────────┴─────────────┴──────────────────┴──────────────────┴──────────────────┘

* Đối với tiếng Trung: Example ZH thay cho Example EN
* Đối với tiếng Nhật: Example JA thay cho Example EN
* Cột No. chứa số thứ tự (1, 2, 3...)

══════════════════════════════════════════════════════════════

📞 HỖ TRỢ: 0986183806
✨ Chúc bạn học tập hiệu quả với Language Quiz!
"""
        
        guide_text.insert("1.0", content)
        guide_text.config(state=tk.DISABLED)
        
        # Add buttons for sample files at bottom
        button_frame = ttk.Frame(guide_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(button_frame, text="📁 File mẫu:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        def open_sample_file(lang):
            """Open sample file in Excel"""
            sample_files = {
                "English": "TEMPLATE_ENGLISH.xlsx",
                "Chinese": "TEMPLATE_CHINESE.xlsx",
                "Japanese": "TEMPLATE_JAPANESE.xlsx"
            }
            file_path = Path(__file__).parent / "data" / sample_files.get(lang, "")
            if file_path.exists():
                import os
                os.startfile(file_path)
            else:
                messagebox.showinfo("File mẫu", f"File mẫu {lang} chưa có trong thư mục data/\nĐường dẫn: {file_path}")
        
        ttk.Button(button_frame, text="🇬🇧 English", 
                  command=lambda: open_sample_file("English"), width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🇨🇳 Chinese", 
                  command=lambda: open_sample_file("Chinese"), width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🇯🇵 Japanese", 
                  command=lambda: open_sample_file("Japanese"), width=12).pack(side=tk.LEFT, padx=2)
        
        # Add documentation links section
        doc_frame = ttk.Frame(guide_container)
        doc_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(doc_frame, text="📚 Tài liệu hướng dẫn:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        def open_doc_file(filename):
            """Open documentation file"""
            file_path = Path(__file__).parent / filename
            if file_path.exists():
                import os
                os.startfile(file_path)
            else:
                messagebox.showwarning("Không tìm thấy", f"File {filename} không tồn tại!")
        
        # Row 1: Main docs
        doc_row1 = ttk.Frame(doc_frame)
        doc_row1.pack(fill=tk.X, pady=2)
        
        ttk.Button(doc_row1, text="📖 README", 
                  command=lambda: open_doc_file("README.md"), width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(doc_row1, text="🚀 QUICK START", 
                  command=lambda: open_doc_file("QUICK_START.txt"), width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(doc_row1, text="❓ FAQ", 
                  command=lambda: open_doc_file("FAQ.txt"), width=18).pack(side=tk.LEFT, padx=2)
        
        # Row 2: Detailed guides
        doc_row2 = ttk.Frame(doc_frame)
        doc_row2.pack(fill=tk.X, pady=2)
        
        ttk.Button(doc_row2, text="📋 Excel Guide", 
                  command=lambda: open_doc_file("EXCEL_GUIDE.txt"), width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(doc_row2, text="🎙️ Voice Guide", 
                  command=lambda: open_doc_file("VOICE_QUIZ_GUIDE.txt"), width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(doc_row2, text="🔧 Setup Guide", 
                  command=lambda: open_doc_file("SETUP_GUIDE.md"), width=18).pack(side=tk.LEFT, padx=2)
        
        # Row 3: Advanced features
        doc_row3 = ttk.Frame(doc_frame)
        doc_row3.pack(fill=tk.X, pady=2)
        
        ttk.Button(doc_row3, text="🔄 File Converter", 
                  command=lambda: open_doc_file("FILE_CONVERTER_GUIDE.md"), width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(doc_row3, text="💬 Discord Setup", 
                  command=lambda: open_doc_file("DISCORD_SETUP.md"), width=18).pack(side=tk.LEFT, padx=2)
        ttk.Button(doc_row3, text="📝 Release Notes", 
                  command=lambda: open_doc_file("RELEASE_NOTES_v2.2.3.md"), width=18).pack(side=tk.LEFT, padx=2)

    
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
                        "Format chuẩn: No. | Word | Meaning | Example EN | Example VI\n\n"
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
        
        # 📚 Check quiz mode: normal vs practice (weak questions)
        quiz_mode = self.quiz_mode_var.get()
        
        if quiz_mode == "practice":
            # 🎯 Practice Mode: Lấy câu yếu từ Smart Review DB
            if not self.smart_review_db or not hasattr(self, 'selected_file'):
                messagebox.showerror("Lỗi", "❌ Smart Review chưa khởi tạo!")
                return
            
            try:
                user_name = "Default"  # Hoặc lấy từ settings
                weak_questions = self.smart_review_db.get_weak_questions(
                    file_path=str(self.selected_file),
                    user_name=user_name,
                    limit=20  # Lấy tối đa 20 câu yếu
                )
                
                if not weak_questions:
                    messagebox.showinfo(
                        "Practice Mode", 
                        "🎉 Chưa có câu yếu nào!\n\n" +
                        "Lý do:\n" +
                        "• Bạn chưa làm quiz lần nào\n" +
                        "• Hoặc bạn đã học tốt tất cả câu!\n\n" +
                        "👉 Hãy làm Normal Quiz trước để hệ thống ghi nhận câu yếu."
                    )
                    return
                
                # Map weak questions back to data
                weak_ids = {q['question_id'] for q in weak_questions}
                
                # DEBUG: Print để check
                print(f"🔍 DEBUG: Weak IDs from DB: {weak_ids}")
                print(f"🔍 DEBUG: Total data rows: {len(self.data)}")
                if self.data:
                    print(f"🔍 DEBUG: Sample data excel_row: {self.data[0].get('excel_row', 'NOT FOUND')}")
                
                selected_data = []
                for q in self.data:
                    excel_row = q.get("excel_row")
                    if excel_row is None:
                        # Fallback: use index + 2 (because Excel starts at row 2)
                        excel_row = self.data.index(q) + 2
                    if excel_row in weak_ids:
                        selected_data.append(q)
                
                if not selected_data:
                    messagebox.showwarning(
                        "Practice Mode", 
                        f"⚠️ Tìm thấy {len(weak_questions)} câu yếu trong DB\n" +
                        f"Nhưng không khớp với file hiện tại!\n\n" +
                        f"Weak IDs: {list(weak_ids)[:5]}...\n\n" +
                        "Có thể bạn đã đổi file Excel hoặc thứ tự câu hỏi đã thay đổi.\n" +
                        "👉 Hãy làm lại Normal Quiz với file này."
                    )
                    return
                    
                messagebox.showinfo("Practice Mode", f"🎯 Tìm thấy {len(selected_data)} câu yếu cần ôn tập!")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"❌ Không thể tải câu yếu:\n{str(e)}")
                import traceback
                traceback.print_exc()
                return
        else:
            # 📖 Normal Mode: Lấy theo range
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
            # Practice Mode: Load weak words from database + match with Excel file
            try:
                # 📂 First, load Excel file to get full data (word + meaning + examples)
                self.data = self._read_excel_data(self.sheet_combo.get())
                if not self.data:
                    messagebox.showerror("Lỗi", "❌ Không đọc được file Excel!")
                    return
                
                # 🔍 Get weak words from database
                all_weak_words = []
                for lang in ["English", "Japanese", "Chinese", "Vietnamese"]:
                    weak_words = self.study_db.get_weak_words(lang)
                    all_weak_words.extend(weak_words)
                
                if not all_weak_words:
                    messagebox.showinfo("Thông báo", 
                        "✅ Tuyệt vời!\n\n"
                        "Không có từ nào cần ôn tập.\n\n"
                        "Tất cả từ đều đã học tốt! 🎉\n\n"
                        "💡 Mẹo: Hãy thử chế độ Normal để học từ mới.")
                    return
                
                # 🔗 Match weak words with Excel data to get full info
                weak_word_texts = {w["word"].strip().lower() for w in all_weak_words}
                
                selected_data = []
                for excel_row in self.data:
                    word_in_excel = excel_row.get("word", "").strip().lower()
                    if word_in_excel in weak_word_texts:
                        # Found matching word in Excel - has full data!
                        selected_data.append(excel_row)
                        print(f"✅ Matched weak word: '{excel_row.get('word')}' with meaning: '{excel_row.get('meaning', 'N/A')}'")
                
                if not selected_data:
                    messagebox.showwarning(
                        "Practice Mode",
                        f"⚠️ Tìm thấy {len(all_weak_words)} từ yếu trong database\n"
                        f"Nhưng không có từ nào khớp với file Excel hiện tại!\n\n"
                        f"💡 Giải pháp:\n"
                        f"• Chọn đúng file Excel mà bạn đã học trước đó\n"
                        f"• Hoặc làm Normal Quiz với file này để tạo dữ liệu mới"
                    )
                    return
                
                num_questions = len(selected_data)
                
                # Thống kê theo ngôn ngữ
                lang_stats = {}
                for word in selected_data:
                    lang = word.get("language", "Unknown")
                    lang_stats[lang] = lang_stats.get(lang, 0) + 1
                
                stats_text = ", ".join([f"{lang}: {count}" for lang, count in lang_stats.items()])
                
                messagebox.showinfo("Chế độ Ôn tập", 
                    f"🎯 CHẾ ĐỘ PRACTICE\n\n"
                    f"📚 Tổng số từ yếu: {num_questions}\n\n"
                    f"🌐 Phân bố:\n{stats_text}\n\n"
                    f"💡 Hãy cố gắng trả lời đúng để cải thiện!\n\n"
                    f"👉 Nhấn OK để bắt đầu Voice Quiz ôn tập!")
                
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
        
        # 🔊 Save current question and enable speaker button
        self.current_voice_question = question
        self.speak_question_btn.config(state=tk.NORMAL)
        
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
            
            # 🚀 Check if paused before processing
            while hasattr(self, 'voice_quiz_paused') and self.voice_quiz_paused:
                if not self.quiz_active:
                    print("⏹️ Quiz đã dừng khi đang tạm dừng")
                    return
                time.sleep(0.5)  # Wait while paused
            
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
                    bot_lang = self._get_bot_language_code()
                    
                    # ⚡ Dictionary các câu hướng dẫn đa ngôn ngữ
                    instructions = {
                        "vi": {
                            "meaning": f"Hãy dịch các từ sau sang tiếng {quiz_lang}",
                            "example": f"Hãy dịch các câu sau sang tiếng {quiz_lang}",
                            "vietnamese": f"Hãy dịch các câu sau sang tiếng {quiz_lang}"
                        },
                        "en": {
                            "meaning": f"Translate the following words to {quiz_lang}",
                            "example": f"Translate the following sentences to {quiz_lang}",
                            "vietnamese": f"Translate the following sentences to {quiz_lang}"
                        },
                        "zh": {
                            "meaning": f"把下面的词译成{quiz_lang}",
                            "example": f"把下面的句子译成{quiz_lang}",
                            "vietnamese": f"把下面的句子译成{quiz_lang}"
                        },
                        "ja": {
                            "meaning": f"次の単語を{quiz_lang}に訳してください",
                            "example": f"次の文を{quiz_lang}に訳してください",
                            "vietnamese": f"次の文を{quiz_lang}に訳してください"
                        }
                    }
                    
                    instruction = instructions.get(bot_lang, instructions["vi"]).get(self.quiz_type_str, instructions["vi"]["meaning"])
                    
                    print(f"📢 [Instruction - {bot_lang}] {instruction}")
                    self._start_gif_animation()
                    self.voice_manager.voice_manager.speak_google_tts(instruction, language=bot_lang)
                    self._stop_gif_animation()
                    time.sleep(0.5)
                    self.instruction_shown = True
                
                # Đọc nội dung câu (không hướng dẫn)
                # Mode 1: Câu hỏi luôn là tiếng Việt, nên dùng voice 'vi'
                print(f"📢 [Mode 1] Đọc câu hỏi VN: {meaning_part[:60]}...")
                self._start_gif_animation()  # 🎨 Bắt đầu animate
                self.voice_manager.voice_manager.speak_google_tts(meaning_part, language='vi')
                self._stop_gif_animation()  # 🎨 Dừng animate
                time.sleep(0.3)
            
            # Mode 2: Đọc Foreign language (Polly) + Câu hỏi VN (gTTS) - User trả lời bằng Tiếng Việt
            elif self.test_mode == 2:
                # Chỉ đọc hướng dẫn ở câu đầu tiên
                if not self.instruction_shown:
                    bot_lang = self._get_bot_language_code()
                    
                    # ⚡ Dictionary các câu hướng dẫn đa ngôn ngữ
                    instructions = {
                        "vi": {
                            "meaning": "Hãy dịch các từ sau sang tiếng Việt",
                            "example": "Hãy dịch các câu sau sang tiếng Việt",
                            "vietnamese": "Hãy dịch các câu sau sang tiếng Việt"
                        },
                        "en": {
                            "meaning": "Translate the following words to Vietnamese",
                            "example": "Translate the following sentences to Vietnamese",
                            "vietnamese": "Translate the following sentences to Vietnamese"
                        },
                        "zh": {
                            "meaning": "把下面的词译成越南语",
                            "example": "把下面的句子译成越南语",
                            "vietnamese": "把下面的句子译成越南语"
                        },
                        "ja": {
                            "meaning": "次の単語をベトナム語に訳してください",
                            "example": "次の文をベトナム語に訳してください",
                            "vietnamese": "次の文をベトナム語に訳してください"
                        }
                    }
                    
                    instruction = instructions.get(bot_lang, instructions["vi"]).get(self.quiz_type_str, instructions["vi"]["meaning"])
                    
                    print(f"📢 [Instruction - {bot_lang}] {instruction}")
                    self._start_gif_animation()
                    self.voice_manager.voice_manager.speak_google_tts(instruction, language=bot_lang)
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
            
            # ✨ Phát âm thanh "tút" - báo hiệu bắt đầu ngay
            try:
                import winsound
                winsound.Beep(1000, 200)  # 1000Hz, 200ms
            except:
                pass
            
            print("\n▶️ Sẵn sàng! Hãy nói NGAY!")
            self._safe_update_answer("🎤 NÓI NGAY! 🔴")
            time.sleep(0.2)
            
            # 🚀 Kiểm tra lại quiz vẫn đang chạy
            if not self.quiz_active:
                print("⏹️ Quiz đã dừng, dừng xử lý")
                return
            
            # Lắng nghe (ưu tiên theo ngôn ngữ test)
            print(f"\n▶️ Lắng nghe câu trả lời ({language_stt})...")
            
            # Update mic status
            self.root.after(0, lambda: self.mic_status_label.config(text="🎙️ Đang nghe... NÓI TO VÀO MIC!", foreground="red"))
            
            # Xác định correct_answer TRƯỚC để tính auto timeout
            question = self.quiz_engine.questions[self.current_question_idx]
            
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
                    correct_answer = question.get("example_vi")  # Dịch câu VN (example_vi)
            else:
                # Mode 2: Đọc Foreign → User trả lời Vietnamese
                if self.quiz_type_str == "meaning":
                    correct_answer = question.get("meaning")  # Nghĩa tiếng Việt
                elif self.quiz_type_str == "example":
                    correct_answer = question.get("example_vi")  # Dịch câu VN
                else:  # vietnamese
                    correct_answer = question.get("example_vi")  # Dịch tiếng Việt
            
            # Lấy timeout: Auto hoặc Manual
            quiz_type = self.quiz_type_var.get()
            
            if self.auto_timing_var.get():
                # 🤖 Chế độ tự động: tính theo độ dài đáp án
                listen_timeout = self._calculate_auto_timeout(correct_answer, quiz_type)
            else:
                # 📌 Chế độ thủ công: lấy từ combobox
                listen_timeout = self.time_limits[quiz_type].get()
            
            print(f"⏱️ Thời gian trả lời: {listen_timeout} giây")
            
            # Lấy microphone index từ combo (dùng mapping)
            mic_device_index = None
            try:
                combo_idx = self.mic_combo.current()
                if combo_idx >= 0 and combo_idx < len(self.mic_device_indices):
                    mic_device_index = self.mic_device_indices[combo_idx]
            except:
                mic_device_index = None
            
            # ✨ Đếm ngược TRONG LÚC NGHE (thread riêng)
            def countdown_during_listening():
                for i in range(listen_timeout, 0, -1):
                    if not self.quiz_active or not self.app_running:
                        return
                    try:
                        self.root.after(0, lambda sec=i: self.countdown_label.config(text=str(sec)))
                    except (RuntimeError, tk.TclError):
                        break  # Main loop đã dừng
                    time.sleep(1)
                # Xóa countdown khi hết giờ
                try:
                    self.root.after(0, lambda: self.countdown_label.config(text=""))
                except (RuntimeError, tk.TclError):
                    pass
            
            Thread(target=countdown_during_listening, daemon=True).start()
            
            # Animate bar trong background thread
            def animate_mic_bar():
                for _ in range(listen_timeout * 2):  # Chạy theo timeout
                    if not self.app_running:
                        break
                    # Check if paused
                    if hasattr(self, 'voice_quiz_paused') and self.voice_quiz_paused:
                        time.sleep(0.5)
                        continue
                    level = random.randint(20, 80)
                    try:
                        self.root.after(0, lambda l=level: self.mic_level_bar.config(value=l))
                    except RuntimeError:
                        break
                    time.sleep(0.5)
            
            Thread(target=animate_mic_bar, daemon=True).start()
            
            user_answer = self.voice_manager.voice_manager.listen_to_microphone(
                timeout=listen_timeout,  # ✨ Dùng thời gian từ combobox
                language=language_stt,
                quiz_type=self.quiz_type_str
            )
            
            # Reset mic status và xóa countdown
            self.root.after(0, lambda: self.mic_status_label.config(text="🎙️ Sẵn sàng", foreground="gray"))
            self.root.after(0, lambda: self.mic_level_bar.config(value=0))
            self.root.after(0, lambda: self.countdown_label.config(text=""))
            
            if not user_answer:
                self._safe_show_feedback("❌ Không nhận dạng được. Hãy nói lại!")
                
                # Lưu kết quả với điểm 0 (correct_answer đã được xác định ở trên)
                question_num = question.get("excel_row", self.current_question_idx + 1)
                self.quiz_results.append({
                    "question_num": question_num,
                    "question": question.get("word"),
                    "user_answer": "(Không trả lời)",
                    "correct_answer": correct_answer,
                    "score": 0,  # ❌ 0 điểm
                    "attempt": 1
                })
                
                # � Save to Smart Review DB
                if self.smart_review_db and hasattr(self, 'selected_file'):
                    try:
                        user_name = self.quiz_results[0].get("user_name", "Unknown") if self.quiz_results else "Unknown"
                        self.smart_review_db.save_question_result(
                            file_path=str(self.selected_file),
                            question_id=question_num,
                            question_text=question.get("word", ""),
                            correct_answer=correct_answer,
                            user_name=user_name,
                            quiz_type=self.quiz_type_str,
                            test_mode=self.test_mode,
                            is_correct=False,
                            user_answer="(Không trả lời)",
                            score=0
                        )
                    except Exception as e:
                        print(f"⚠️ Smart Review save error: {e}")
                
                # �🚀 Tự động tiến tới câu tiếp (thay vì treo)
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
            
            # So sánh NGAY (correct_answer đã được xác định ở trên)
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
            
            # 📚 Save to Smart Review DB
            if self.smart_review_db and hasattr(self, 'selected_file'):
                try:
                    user_name = self.quiz_results[0].get("user_name", "Unknown") if self.quiz_results else "Unknown"
                    self.smart_review_db.save_question_result(
                        file_path=str(self.selected_file),
                        question_id=question_num,
                        question_text=question.get("word", ""),
                        correct_answer=correct_answer,
                        user_name=user_name,
                        quiz_type=self.quiz_type_str,
                        test_mode=self.test_mode,
                        is_correct=is_correct,
                        user_answer=user_answer,
                        score=score
                    )
                except Exception as e:
                    print(f"⚠️ Smart Review save error: {e}")
            
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
                    bot_lang = self._get_bot_language_code()
                    # ⚡ Feedback đa ngôn ngữ
                    feedback_texts = {
                        "vi": "Đúng!",
                        "en": "Correct!",
                        "zh": "对了！",
                        "ja": "正解！"
                    }
                    feedback_tts = feedback_texts.get(bot_lang, "Đúng!")
                    self.voice_manager.voice_manager.speak_google_tts(feedback_tts, language=bot_lang)
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
                bot_lang = self._get_bot_language_code()
                semantic_note = " (✓ Đúng về mặt ý nghĩa)" if is_semantic else ""
                
                # ⚡ Feedback đa ngôn ngữ
                feedback_dict = {
                    "vi": {
                        "near": "Gần đúng! Đáp án chính xác là:",
                        "wrong": "Sai rồi! Câu trả lời đúng là:"
                    },
                    "en": {
                        "near": "Almost correct! The exact answer is:",
                        "wrong": "Wrong! The correct answer is:"
                    },
                    "zh": {
                        "near": "差不多！正确答案是：",
                        "wrong": "错了！正确答案是："
                    },
                    "ja": {
                        "near": "もう少し！正しい答えは：",
                        "wrong": "間違い！正しい答えは："
                    }
                }
                
                if similarity >= 0.7:
                    feedback_text = feedback_dict.get(bot_lang, feedback_dict["vi"])["near"]
                    popup_title = "⚠️ Gần Đúng"
                    feedback_msg = f"⚠️ Gần đúng!{semantic_note}\n\n✨ {correct_answer}"
                else:
                    feedback_text = feedback_dict.get(bot_lang, feedback_dict["vi"])["wrong"]
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
                    # Check pause state before TTS
                    while hasattr(self, 'voice_quiz_paused') and self.voice_quiz_paused:
                        if not self.quiz_active:
                            return
                        time.sleep(0.5)
                    
                    if use_faster_feedback:
                        # Chế độ nhanh: chỉ hiển thị 0.5s rồi đến câu tiếp
                        time.sleep(0.5)
                    else:
                        # Chế độ bình thường: phát TTS
                        self.voice_manager.voice_manager.speak_google_tts(feedback_text, language=bot_lang)
                        
                        # Check pause before speaking answer
                        while hasattr(self, 'voice_quiz_paused') and self.voice_quiz_paused:
                            if not self.quiz_active:
                                return
                            time.sleep(0.5)
                        
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
    
    def _calculate_auto_timeout(self, correct_answer, quiz_type):
        """
        Tính toán thời gian trả lời tự động dựa trên độ dài đáp án
        
        Args:
            correct_answer: Đáp án đúng
            quiz_type: Loại quiz ("meaning", "example", "vietnamese")
        
        Returns:
            int: Thời gian timeout (giây)
        """
        if not correct_answer:
            return 5  # Default fallback
        
        # Đếm số từ và ký tự
        word_count = len(correct_answer.split())
        char_count = len(correct_answer)
        
        if quiz_type == "meaning":
            # Nghĩa từ: thường ngắn (1-3 từ)
            # Công thức: 1.5s/từ + 2s buffer
            timeout = int(word_count * 1.5 + 2)
            # Giới hạn: 3-10 giây
            timeout = max(3, min(10, timeout))
        else:
            # Câu dài (example/vietnamese): thường 5-15 từ
            # Công thức: 0.8s/từ + 2s buffer
            timeout = int(word_count * 0.8 + 2)
            # Giới hạn: 6-20 giây
            timeout = max(6, min(20, timeout))
        
        print(f"🤖 Auto timeout: {word_count} từ ({char_count} ký tự) → {timeout}s")
        return timeout
    
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
    
    def _get_bot_language_code(self):
        """⚡ Lấy mã ngôn ngữ của chatbot từ combobox"""
        bot_lang_display = self.bot_language_var.get()
        lang_map = {
            "Tiếng Việt": "vi",
            "Tiếng Anh": "en",
            "Tiếng Trung": "zh",
            "Tiếng Nhật": "ja"
        }
        return lang_map.get(bot_lang_display, "vi")
    
    def _get_bot_language_code(self):
        """⚡ Lấy mã ngôn ngữ của chatbot từ combobox"""
        bot_lang_display = self.bot_language_var.get()
        lang_map = {
            "Tiếng Việt": "vi",
            "Tiếng Anh": "en",
            "Tiếng Trung": "zh",
            "Tiếng Nhật": "ja"
        }
        return lang_map.get(bot_lang_display, "vi")
    
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
            # � Tính điểm trung bình
            total_points = sum(r.get("score", 0) for r in self.quiz_results)
            num_questions = len(self.quiz_results)
            avg_score = (total_points / (num_questions * 10)) * 100 if num_questions > 0 else 0
            
            # 🎤 Phát feedback đa ngôn ngữ dựa trên điểm
            bot_lang = self._get_bot_language_code()
            
            # ⚡ Dictionary feedback theo mức điểm
            feedback_messages = {
                "vi": {
                    "excellent": "Xuất sắc! Bạn đã làm rất tốt!",  # >= 90
                    "good": "Tốt lắm! Bạn đang tiến bộ!",  # >= 75
                    "pass": "Khá đấy! Hãy tiếp tục cố gắng!",  # >= 60
                    "fail": "Cần cố gắng hơn nữa! Đừng bỏ cuộc!"  # < 60
                },
                "en": {
                    "excellent": "Excellent! You did very well!",
                    "good": "Good job! You're making progress!",
                    "pass": "Not bad! Keep trying!",
                    "fail": "Need more effort! Don't give up!"
                },
                "zh": {
                    "excellent": "太棒了！你做得非常好！",
                    "good": "很好！你在进步！",
                    "pass": "不错！继续努力！",
                    "fail": "需要更加努力！不要放弃！"
                },
                "ja": {
                    "excellent": "素晴らしい！とても良くできました！",
                    "good": "良くできました！上達しています！",
                    "pass": "悪くないです！頑張り続けてください！",
                    "fail": "もっと頑張りましょう！諾めないで！"
                }
            }
            
            # Chọn feedback dựa trên điểm
            if avg_score >= 90:
                feedback_key = "excellent"
            elif avg_score >= 75:
                feedback_key = "good"
            elif avg_score >= 60:
                feedback_key = "pass"
            else:
                feedback_key = "fail"
            
            feedback_text = feedback_messages.get(bot_lang, feedback_messages["vi"])[feedback_key]
            
            print(f"📊 Điểm trung bình: {avg_score:.1f}%")
            print(f"🎤 Feedback: {feedback_text}")
            
            # 🎊 Hiển thị popup feedback
            feedback_popup = tk.Toplevel(self.root)
            feedback_popup.title("Feedback")
            feedback_popup.geometry("400x150")
            feedback_popup.resizable(False, False)
            
            # Set icon
            try:
                if self.icon_path.exists():
                    feedback_popup.iconbitmap(str(self.icon_path))
            except:
                pass
            
            # Center popup
            feedback_popup.transient(self.root)
            feedback_popup.grab_set()
            
            # Frame chính
            popup_frame = ttk.Frame(feedback_popup, padding=30)
            popup_frame.pack(fill=tk.BOTH, expand=True)
            
            # Label với feedback text lớn và màu sắc
            feedback_label = ttk.Label(
                popup_frame, 
                text=feedback_text,
                font=("Arial", 16, "bold"),
                foreground="#2E7D32" if avg_score >= 75 else "#D84315",
                justify=tk.CENTER
            )
            feedback_label.pack(expand=True)
            
            # Phát TTS feedback trong thread riêng
            def play_and_close():
                try:
                    self.voice_manager.voice_manager.speak_google_tts(feedback_text, language=bot_lang)
                except Exception as e:
                    print(f"⚠️ Lỗi TTS feedback: {e}")
                finally:
                    # Đóng popup sau khi TTS xong
                    try:
                        feedback_popup.destroy()
                    except:
                        pass
            
            threading.Thread(target=play_and_close, daemon=True).start()
            
            self.root.wait_window(feedback_popup)
            
            # �🕐 Thêm timestamp
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
        
        # 📝 Xác định loại bài kiểm tra
        quiz_lang = self._get_quiz_language_code()
        if self.test_mode == 1:
            if self.quiz_type_str == "meaning":
                test_type = f"Kiểm tra từ vựng - dịch sang {quiz_lang}"
            else:
                test_type = f"Kiểm tra câu - dịch sang {quiz_lang}"
        else:  # mode 2
            if self.quiz_type_str == "meaning":
                test_type = "Kiểm tra từ vựng - dịch sang tiếng Việt"
            else:
                test_type = "Kiểm tra câu - dịch sang tiếng Việt"
        
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
📝 Loại bài: {test_type}

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
            
            # 💾 Save to leaderboard database
            try:
                total_points = sum(r.get("score", 0) for r in self.quiz_results)
                num_questions = len(self.quiz_results)
                avg_score = (total_points / (num_questions * 10)) * 100 if num_questions > 0 else 0
                
                quiz_lang = self._get_quiz_language_code()
                file_name_only = Path(self.selected_file).name if hasattr(self, 'selected_file') and self.selected_file else "Unknown"
                
                conn = sqlite3.connect('study_history.db')
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quiz_results (user_name, score, total_questions, language, file_name)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_name, avg_score, num_questions, quiz_lang, file_name_only))
                conn.commit()
                conn.close()
                
                # Refresh leaderboard
                self._load_leaderboard()
                print(f"✅ Đã lưu điểm {avg_score:.1f} vào leaderboard")
            except Exception as lb_err:
                print(f"⚠️ Lỗi lưu leaderboard: {lb_err}")
            
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
            
            # 📝 Xác định loại bài kiểm tra
            quiz_lang = self._get_quiz_language_code()
            if self.test_mode == 1:
                if self.quiz_type_str == "meaning":
                    test_type = f"Kiểm tra từ vựng - dịch sang {quiz_lang}"
                else:
                    test_type = f"Kiểm tra câu - dịch sang {quiz_lang}"
            else:  # mode 2
                if self.quiz_type_str == "meaning":
                    test_type = "Kiểm tra từ vựng - dịch sang tiếng Việt"
                else:
                    test_type = "Kiểm tra câu - dịch sang tiếng Việt"
            
            # Tạo nội dung message
            message_content = f"""
📊 **KẾT QUẢ KIỂM TRA**
═══════════════════════════════════════
👤 **Học sinh:** {user_name}
🕐 **Thời gian:** {timestamp}
📁 **File:** {file_name}
📝 **Phạm vi:** từ câu {start_q} đến câu {end_q}
✍️ **Loại bài:** {test_type}

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
    
    def _speak_current_question(self):
        """🔊 Phát âm từ trong câu hỏi hiện tại"""
        if not hasattr(self, 'current_voice_question') or not self.current_voice_question:
            return
        
        question = self.current_voice_question
        word_to_speak = question.get("word", "")
        
        if not word_to_speak:
            return
        
        # Xác định ngôn ngữ để chọn voice đúng
        language = question.get("language", "English")
        
        def speak_async():
            try:
                if language == "English":
                    # Use AWS Polly for English
                    voice = "Joanna" if self.en_voice_var.get() == "female" else "Matthew"
                    self._speak_with_polly(word_to_speak, voice, "en-US")
                elif language == "Japanese":
                    # Use AWS Polly for Japanese
                    voice = "Mizuki" if self.ja_voice_var.get() == "female" else "Takumi"
                    self._speak_with_polly(word_to_speak, voice, "ja-JP")
                else:
                    # Fallback to gTTS
                    from gtts import gTTS
                    import tempfile
                    import os
                    from pygame import mixer
                    
                    lang_code = "en" if language == "English" else "ja" if language == "Japanese" else "zh-cn"
                    tts = gTTS(text=word_to_speak, lang=lang_code, slow=False)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                        temp_path = f.name
                    
                    tts.save(temp_path)
                    
                    mixer.init()
                    mixer.music.load(temp_path)
                    mixer.music.play()
                    
                    while mixer.music.get_busy():
                        import time
                        time.sleep(0.1)
                    
                    mixer.quit()
                    os.unlink(temp_path)
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
        
        import threading
        threading.Thread(target=speak_async, daemon=True).start()
    
    def _speak_practice_question(self):
        """🔊 Phát âm câu hỏi Practice Quiz (dịch câu)"""
        if not hasattr(self, 'current_practice_question') or not self.current_practice_question:
            return
        
        question = self.current_practice_question
        # Lấy câu cần đọc (câu tiếng Anh hoặc tiếng Nhật)
        text_to_speak = question.get("question_sentence", "")
        
        if not text_to_speak:
            return
        
        # Xác định ngôn ngữ từ câu
        language = question.get("language", "English")
        
        def speak_async():
            try:
                if language == "English":
                    voice = "Joanna" if self.en_voice_var.get() == "female" else "Matthew"
                    self._speak_with_polly(text_to_speak, voice, "en-US")
                elif language == "Japanese":
                    voice = "Mizuki" if self.ja_voice_var.get() == "female" else "Takumi"
                    self._speak_with_polly(text_to_speak, voice, "ja-JP")
                else:
                    from gtts import gTTS
                    import tempfile
                    import os
                    from pygame import mixer
                    
                    lang_code = "en" if language == "English" else "ja" if language == "Japanese" else "zh-cn"
                    tts = gTTS(text=text_to_speak, lang=lang_code, slow=False)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                        temp_path = f.name
                    
                    tts.save(temp_path)
                    
                    mixer.init()
                    mixer.music.load(temp_path)
                    mixer.music.play()
                    
                    while mixer.music.get_busy():
                        import time
                        time.sleep(0.1)
                    
                    mixer.quit()
                    os.unlink(temp_path)
            except Exception as e:
                print(f"⚠️ Practice TTS error: {e}")
        
        import threading
        threading.Thread(target=speak_async, daemon=True).start()
    
    def _speak_with_polly(self, text, voice_id, language_code):
        """Speak text using AWS Polly with speed control"""
        try:
            import boto3
            from pygame import mixer
            import tempfile
            import os
            
            # Get voice speed
            speed = getattr(self, 'voice_speed_var', None)
            speed_rate = speed.get() if speed else 1.0
            
            # Use boto3 for AWS Polly
            polly = boto3.client(
                'polly',
                region_name='us-east-1',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # Determine engine based on voice - Mizuki and Takumi only support 'standard'
            # Neural voices: Matthew, Joanna, Amy, etc.
            # Standard only voices: Mizuki, Takumi
            standard_only_voices = ['Mizuki', 'Takumi', 'Zhiyu']
            engine = 'standard' if voice_id in standard_only_voices else 'neural'
            
            # Apply SSML for speed control
            ssml_text = f'<speak><prosody rate="{int(speed_rate * 100)}%">{text}</prosody></speak>'
            
            response = polly.synthesize_speech(
                Text=ssml_text,
                TextType='ssml',
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine
            )
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                f.write(response['AudioStream'].read())
                temp_path = f.name
            
            # Play with pygame - ensure mixer is initialized
            if not mixer.get_init():
                mixer.init()
            mixer.music.load(temp_path)
            mixer.music.play()
            
            while mixer.music.get_busy():
                import time
                time.sleep(0.1)
            
            # Don't quit mixer, just unload
            mixer.music.unload()
            os.unlink(temp_path)
        except Exception as e:
            print(f"⚠️ Polly error: {e}")
    
    def _update_speed_label(self, value):
        """Cập nhật label hiển thị tốc độ"""
        speed = float(value)
        self.voice_speed_label.config(text=f"{speed:.1f}x")
    
    def _set_voice_speed(self, speed):
        """Đặt tốc độ voice nhanh"""
        self.voice_speed_var.set(speed)
        self.voice_speed_label.config(text=f"{speed:.1f}x")
    
    def _play_sound(self, sound_type):
        """🔊 Phát âm thanh cho Practice Quiz
        sound_type: 'click', 'correct', 'wrong'
        """
        def play_async():
            try:
                import winsound
                import time
                if sound_type == 'click':
                    winsound.Beep(440, 50)
                elif sound_type == 'correct':
                    winsound.Beep(523, 100)  # C5
                    time.sleep(0.05)
                    winsound.Beep(659, 100)  # E5
                    time.sleep(0.05)
                    winsound.Beep(784, 150)  # G5
                elif sound_type == 'wrong':
                    winsound.Beep(400, 150)
                    time.sleep(0.05)
                    winsound.Beep(300, 250)
            except Exception as e:
                print(f"⚠️ Sound error: {e}")
        
        # Play in thread to not block UI
        import threading
        threading.Thread(target=play_async, daemon=True).start()
    
    def _practice_select_file(self):
        """Chọn file cho Practice Quiz"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Chọn File Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.practice_selected_file = file_path
            self.practice_file_label.config(
                text=file_path.split("/")[-1].split("\\")[-1],  # Get filename only
                foreground="green"
            )
            # 💾 Lưu vào settings
            self.user_settings["practice_file"] = file_path
            self._save_settings()
    
    def _start_practice_quiz(self):
        """Bắt đầu Practice Quiz với Multiple Choice"""
        if not hasattr(self, 'practice_selected_file'):
            messagebox.showerror("Lỗi", "❌ Vui lòng chọn file Excel!")
            return
        
        # Read data
        try:
            data = self._read_excel_data_practice(self.practice_selected_file)
            if not data:
                messagebox.showerror("Lỗi", "❌ Không đọc được dữ liệu từ file!")
                return
        except Exception as e:
            messagebox.showerror("Lỗi", f"❌ Lỗi đọc file:\n{str(e)}")
            return
        
        # Get range
        start_idx = self.practice_start_var.get() - 1
        end_idx = self.practice_end_var.get()
        
        if start_idx < 0:
            start_idx = 0
        if end_idx > len(data):
            end_idx = len(data)
        if start_idx >= end_idx:
            messagebox.showerror("Lỗi", f"❌ Khoảng không hợp lệ!\n\nTổng số câu: {len(data)}")
            return
        
        self.practice_questions = data[start_idx:end_idx]
        self.practice_current_idx = 0
        self.practice_results = []
        
        # Display first question
        self._display_practice_question()
    
    def _read_excel_data_practice(self, file_path):
        """Đọc dữ liệu Excel cho Practice Quiz (simplified)"""
        import openpyxl
        import os
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active  # Default to first sheet
        
        # Detect language from filename
        filename = os.path.basename(file_path).lower()
        if 'nhat' in filename or 'japanese' in filename or 'ja' in filename:
            detected_lang = "Japanese"
        elif 'trung' in filename or 'chinese' in filename or 'zh' in filename:
            detected_lang = "Chinese"
        else:
            detected_lang = "English"
        
        self.practice_detected_language = detected_lang
        print(f"📚 Practice Quiz - Detected language: {detected_lang}")
        
        data = []
        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:  # Skip empty rows
                continue
            data.append({
                "excel_row": idx - 1,
                "word": row[1] if len(row) > 1 else "",
                "meaning": row[2] if len(row) > 2 else "",
                "example_en": row[3] if len(row) > 3 else "",
                "example_vi": row[4] if len(row) > 4 else "",
                "language": detected_lang
            })
        return data
    
    def _display_practice_question(self):
        """Hiển thị câu hỏi Multiple Choice"""
        if self.practice_current_idx >= len(self.practice_questions):
            self._show_practice_results()
            return
        
        question = self.practice_questions[self.practice_current_idx]
        quiz_type = self.practice_quiz_type_var.get()
        
        # Get question text
        if quiz_type == "meaning":
            question_text = f"💬 Nghĩa của từ:\n\n{question['word']}"
            correct_answer = question['meaning']
            question_sentence = question['word']  # For TTS
        else:  # example
            question_text = f"📝 Dịch câu sau:\n\n{question['example_en']}"
            correct_answer = question['example_vi']
            question_sentence = question['example_en']  # For TTS
        
        # Store current question for TTS - use detected language
        detected_lang = getattr(self, 'practice_detected_language', question.get("language", "English"))
        self.current_practice_question = {
            "language": detected_lang,
            "question_sentence": question_sentence
        }
        
        # Enable speaker button
        self.practice_speak_btn.config(state=tk.NORMAL)
        
        # Generate distractors (3 wrong answers) - SMARTER
        import random
        all_answers = [q.get('meaning' if quiz_type == 'meaning' else 'example_vi', '') 
                      for q in self.practice_questions]
        all_answers = [a for a in all_answers if a and a != correct_answer]
        
        if len(all_answers) < 3:
            # Not enough distractors, add placeholders
            distractors = all_answers + ["...", "...", "..."][:3 - len(all_answers)]
        else:
            # 🧠 SMART DISTRACTOR: Prioritize answers with similar length
            correct_len = len(correct_answer)
            
            # Score each answer by length similarity
            scored_answers = []
            for ans in all_answers:
                length_diff = abs(len(ans) - correct_len)
                # Lower score = better (more similar length)
                scored_answers.append((ans, length_diff))
            
            # Sort by length similarity
            scored_answers.sort(key=lambda x: x[1])
            
            # Take top 10 candidates, then random sample 3 from them
            candidates = [ans for ans, score in scored_answers[:min(10, len(scored_answers))]]
            distractors = random.sample(candidates, min(3, len(candidates)))
            
            # If still not enough, add random ones
            if len(distractors) < 3:
                remaining = [a for a in all_answers if a not in distractors]
                distractors += random.sample(remaining, 3 - len(distractors))
        
        # Shuffle options
        options = [correct_answer] + distractors
        random.shuffle(options)
        
        # Store correct answer
        self.practice_correct_answer = correct_answer
        self.practice_options = {
            "A": options[0],
            "B": options[1],
            "C": options[2],
            "D": options[3]
        }
        
        # Update UI - Dùng Label
        self.practice_question_label.config(text=question_text)
        
        # Update buttons - FULL TEXT không cắt
        self.practice_btn_a.config(text=f"A. {options[0]}", state=tk.NORMAL, bg="#bbdefb", fg="#000000")
        self.practice_btn_b.config(text=f"B. {options[1]}", state=tk.NORMAL, bg="#c8e6c9", fg="#000000")
        self.practice_btn_c.config(text=f"C. {options[2]}", state=tk.NORMAL, bg="#ffe0b2", fg="#000000")
        self.practice_btn_d.config(text=f"D. {options[3]}", state=tk.NORMAL, bg="#f8bbd0", fg="#000000")
        
        # Update progress
        current = self.practice_current_idx + 1
        total = len(self.practice_questions)
        self.practice_progress_label.config(text=f"Câu {current}/{total}")
        self.practice_progress_bar['value'] = (current / total) * 100
        
        # Clear feedback
        self.practice_feedback_text.config(state=tk.NORMAL)
        self.practice_feedback_text.delete(1.0, tk.END)
        self.practice_feedback_text.config(state=tk.DISABLED)
        
        # ⏱️ Start timer countdown (30 seconds per question)
        self.practice_timer_seconds = 30
        self._update_practice_timer()
        
        # Enable pause button
        self.practice_pause_btn.config(state=tk.NORMAL)
        # 🔊 Auto TTS - Đọc câu hỏi khi hiển thị (tùy chọn)
        # Uncomment dòng dưới nếu muốn tự động đọc:
        # self._speak_practice_question()
    
    def _practice_submit_answer(self, choice):
        """Xử lý khi chọn đáp án A/B/C/D"""
        # 🔊 Click sound
        self._play_sound('click')
        
        # Stop timer
        self.practice_timer_seconds = -1
        
        user_answer = self.practice_options[choice]
        is_correct = (user_answer == self.practice_correct_answer)
        score = 10 if is_correct else 0
        
        # Highlight correct/wrong
        btn = getattr(self, f"practice_btn_{choice.lower()}")
        if is_correct:
            # 🔊 Correct sound
            self._play_sound('correct')
            btn.config(bg="#4caf50", fg="white")  # Green for correct
            feedback_msg = f"✅ CHÍNH XÁC! (+{score} điểm)\n\n💡 Đáp án đúng: {self.practice_correct_answer}"
        else:
            # 🔊 Wrong sound
            self._play_sound('wrong')
            btn.config(bg="#f44336", fg="white")  # Red for wrong
            # Find correct button and highlight
            for opt, ans in self.practice_options.items():
                if ans == self.practice_correct_answer:
                    correct_btn = getattr(self, f"practice_btn_{opt.lower()}")
                    correct_btn.config(bg="#4caf50", fg="white")
                    break
            feedback_msg = f"❌ SAI RỒI! (+{score} điểm)\n\n💡 Đáp án đúng: {self.practice_correct_answer}"
        
        # Show feedback
        self.practice_feedback_text.config(state=tk.NORMAL)
        self.practice_feedback_text.delete(1.0, tk.END)
        self.practice_feedback_text.insert(tk.END, feedback_msg)
        self.practice_feedback_text.config(state=tk.DISABLED)
        
        # Disable buttons
        self.practice_btn_a.config(state=tk.DISABLED)
        self.practice_btn_b.config(state=tk.DISABLED)
        self.practice_btn_c.config(state=tk.DISABLED)
        self.practice_btn_d.config(state=tk.DISABLED)
        
        # Save result
        question = self.practice_questions[self.practice_current_idx]
        self.practice_results.append({
            "question_num": question['excel_row'],
            "question": question['word'],
            "user_answer": user_answer,
            "correct_answer": self.practice_correct_answer,
            "score": score,
            "is_correct": is_correct
        })
        
        # Save to Smart Review DB
        if self.smart_review_db and hasattr(self, 'practice_selected_file'):
            try:
                self.smart_review_db.save_question_result(
                    file_path=str(self.practice_selected_file),
                    question_id=question['excel_row'],
                    question_text=question.get('word', ''),
                    correct_answer=self.practice_correct_answer,
                    user_name="Default",
                    quiz_type="practice_" + self.practice_quiz_type_var.get(),
                    test_mode=0,  # Practice mode
                    is_correct=is_correct,
                    user_answer=user_answer,
                    score=score
                )
            except Exception as e:
                print(f"⚠️ Smart Review save error: {e}")
        
        # Next question after 2 seconds
        self.root.after(2000, self._next_practice_question)
    
    def _next_practice_question(self):
        """Chuyển sang câu tiếp theo"""
        self.practice_current_idx += 1
        self._display_practice_question()
    
    def _update_practice_timer(self):
        """Cập nhật timer countdown mỗi giây"""
        # Check if paused
        if hasattr(self, 'practice_paused') and self.practice_paused:
            self.root.after(1000, self._update_practice_timer)
            return
        
        if self.practice_timer_seconds < 0:
            # Timer stopped
            self.practice_timer_label.config(text="")
            return
        
        if self.practice_timer_seconds == 0:
            # Time's up! Auto-submit random answer
            self.practice_timer_label.config(text="⏰ Hết giờ!", foreground="red")
            
            # Disable buttons
            self.practice_btn_a.config(state=tk.DISABLED)
            self.practice_btn_b.config(state=tk.DISABLED)
            self.practice_btn_c.config(state=tk.DISABLED)
            self.practice_btn_d.config(state=tk.DISABLED)
            
            # Show feedback
            self.practice_feedback_text.config(state=tk.NORMAL)
            self.practice_feedback_text.delete(1.0, tk.END)
            self.practice_feedback_text.insert(tk.END, f"⏰ HẾT GIỜ! (+0 điểm)\n\n💡 Đáp án đúng: {self.practice_correct_answer}")
            self.practice_feedback_text.config(state=tk.DISABLED)
            
            # Save result (timeout = wrong answer)
            question = self.practice_questions[self.practice_current_idx]
            self.practice_results.append({
                "question_num": question['excel_row'],
                "question": question['word'],
                "user_answer": "(Hết giờ)",
                "correct_answer": self.practice_correct_answer,
                "score": 0,
                "is_correct": False
            })
            
            # Save to Smart Review DB
            if self.smart_review_db and hasattr(self, 'practice_selected_file'):
                try:
                    self.smart_review_db.save_question_result(
                        file_path=str(self.practice_selected_file),
                        question_id=question['excel_row'],
                        question_text=question.get('word', ''),
                        correct_answer=self.practice_correct_answer,
                        user_name="Default",
                        quiz_type="practice_" + self.practice_quiz_type_var.get(),
                        test_mode=0,
                        is_correct=False,
                        user_answer="(Hết giờ)",
                        score=0
                    )
                except Exception as e:
                    print(f"⚠️ Smart Review save error: {e}")
            
            # Next question after 2 seconds
            self.root.after(2000, self._next_practice_question)
            return
        
        # Update timer display
        self.practice_timer_label.config(
            text=f"⏱️ {self.practice_timer_seconds}s",
            foreground="#ff5722" if self.practice_timer_seconds <= 10 else "#4caf50"
        )
        
        # Countdown
        self.practice_timer_seconds -= 1
        
        # Schedule next update in 1 second
        self.root.after(1000, self._update_practice_timer)
    
    def _show_practice_results(self):
        """Hiển thị kết quả Practice Quiz"""
        if not self.practice_results:
            return
        
        total_score = sum(r['score'] for r in self.practice_results)
        total_questions = len(self.practice_results)
        correct_count = sum(1 for r in self.practice_results if r['is_correct'])
        
        result_msg = f"""
🎉 HOÀN THÀNH PRACTICE QUIZ!

📊 Kết quả:
   • Tổng số câu: {total_questions}
   • Đúng: {correct_count}/{total_questions}
   • Điểm: {total_score}/{total_questions * 10}
   • Độ chính xác: {correct_count/total_questions*100:.1f}%
        """
        
        messagebox.showinfo("Kết quả", result_msg)
        
        # Reset UI - Use Label instead of ScrolledText
        self.practice_question_label.config(text="Đã hoàn thành! Nhấn 'Bắt Đầu Practice' để làm lại.")
    
    def export_smart_review_stats(self):
        """📊 Export Smart Review statistics to Excel"""
        if not self.smart_review_db:
            messagebox.showerror("Lỗi", "❌ Smart Review chưa khởi tạo!")
            return
        
        if not hasattr(self, 'selected_file') or not self.selected_file:
            messagebox.showwarning("Cảnh báo", "⚠️ Vui lòng chọn file Excel trước!")
            return
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from datetime import datetime
            from tkinter import filedialog
            
            user_name = "Default"  # Or get from settings
            
            # Get stats
            stats = self.smart_review_db.get_mastery_stats(str(self.selected_file), user_name)
            weak_questions = self.smart_review_db.get_weak_questions(
                str(self.selected_file), user_name, limit=100
            )
            
            # Create workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Smart Review Stats"
            
            # Header styling
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Title
            ws.merge_cells('A1:G1')
            ws['A1'] = f"📊 SMART REVIEW STATISTICS - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ws['A1'].font = Font(bold=True, size=14, color="366092")
            ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
            
            # Overall stats
            ws['A3'] = "📈 TỔNG QUAN"
            ws['A3'].font = Font(bold=True, size=12, color="366092")
            
            stats_data = [
                ["Tổng số câu", stats.get('total', 0)],
                ["Câu thành thạo (mastery = 5)", stats.get('mastered', 0)],
                ["Câu tốt (mastery >= 3)", stats.get('good', 0)],
                ["Câu yếu (mastery < 3)", stats.get('weak', 0)]
            ]
            
            for idx, (label, value) in enumerate(stats_data, start=4):
                ws[f'A{idx}'] = label
                ws[f'B{idx}'] = value
                ws[f'A{idx}'].font = Font(bold=True)
            
            # Weak questions table
            ws['A9'] = "🎯 CÂU HỎI YẾU (Cần ôn tập)"
            ws['A9'].font = Font(bold=True, size=12, color="366092")
            
            # Table headers
            headers = ["STT", "Question ID", "Câu hỏi", "Đáp án đúng", "Mastery", "Attempts", "Lần cuối"]
            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=10, column=col_idx)
                cell.value = header
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = border
            
            # Weak questions data
            for row_idx, q in enumerate(weak_questions, start=11):
                ws.cell(row=row_idx, column=1, value=row_idx - 10)
                ws.cell(row=row_idx, column=2, value=q['question_id'])
                ws.cell(row=row_idx, column=3, value=q.get('question_text', ''))
                ws.cell(row=row_idx, column=4, value=q.get('correct_answer', ''))
                ws.cell(row=row_idx, column=5, value=q['mastery_level'])
                ws.cell(row=row_idx, column=6, value=q['attempt_count'])
                ws.cell(row=row_idx, column=7, value=q.get('last_attempt_date', ''))
                
                # Color code mastery level
                mastery_cell = ws.cell(row=row_idx, column=5)
                if q['mastery_level'] == 0:
                    mastery_cell.fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    mastery_cell.font = Font(color="FFFFFF", bold=True)
                elif q['mastery_level'] <= 2:
                    mastery_cell.fill = PatternFill(start_color="FFA500", end_color="FFA500", fill_type="solid")
                    mastery_cell.font = Font(bold=True)
                
                # Apply borders
                for col in range(1, 8):
                    ws.cell(row=row_idx, column=col).border = border
            
            # Auto-adjust column widths
            ws.column_dimensions['A'].width = 6
            ws.column_dimensions['B'].width = 12
            ws.column_dimensions['C'].width = 30
            ws.column_dimensions['D'].width = 30
            ws.column_dimensions['E'].width = 10
            ws.column_dimensions['F'].width = 10
            ws.column_dimensions['G'].width = 20
            
            # Save file
            default_filename = f"smart_review_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if file_path:
                wb.save(file_path)
                messagebox.showinfo("Thành công", f"✅ Đã xuất stats:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"❌ Lỗi khi xuất stats:\n{str(e)}")
    
    def open_settings_dialog(self):
        """Mở dialog cài đặt API keys"""
        from pathlib import Path
        import os
        
        # Tạo dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("⚙️ Cài đặt API Keys")
        dialog.geometry("650x550")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Set icon if exists
        try:
            icon_path = Path(__file__).parent / "logo.ico"
            if icon_path.exists():
                dialog.iconbitmap(icon_path)
        except:
            pass
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (650 // 2)
        y = (dialog.winfo_screenheight() // 2) - (550 // 2)
        dialog.geometry(f"650x550+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with logo
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Try to load logo
        try:
            logo_path = Path(__file__).parent / "logo.bmp"
            if logo_path.exists():
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((48, 48), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = ttk.Label(header_frame, image=logo_photo)
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Không load được logo: {e}")
        
        # Title
        title_label = ttk.Label(header_frame, text="🔐 Cấu hình API Keys", 
                               font=("Segoe UI", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Load current values from .env
        env_path = Path(__file__).parent / ".env"
        current_values = {}
        
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        current_values[key.strip()] = value.strip()
        
        # AWS Section
        aws_frame = ttk.LabelFrame(main_frame, text="☁️ AWS Polly (Text-to-Speech)", padding=15)
        aws_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(aws_frame, text="AWS Access Key ID:", font=("Segoe UI", 9)).pack(anchor=tk.W)
        aws_key_entry = ttk.Entry(aws_frame, width=60, font=("Courier", 9))
        aws_key_entry.insert(0, current_values.get("AWS_ACCESS_KEY_ID", ""))
        aws_key_entry.pack(fill=tk.X, pady=(2, 10))
        
        ttk.Label(aws_frame, text="AWS Secret Access Key:", font=("Segoe UI", 9)).pack(anchor=tk.W)
        aws_secret_entry = ttk.Entry(aws_frame, width=60, font=("Courier", 9), show="*")
        aws_secret_entry.insert(0, current_values.get("AWS_SECRET_ACCESS_KEY", ""))
        aws_secret_entry.pack(fill=tk.X, pady=(2, 10))
        
        ttk.Label(aws_frame, text="AWS Region:", font=("Segoe UI", 9)).pack(anchor=tk.W)
        aws_region_entry = ttk.Entry(aws_frame, width=60)
        aws_region_entry.insert(0, current_values.get("AWS_REGION", "ap-southeast-2"))
        aws_region_entry.pack(fill=tk.X, pady=2)
        
        # Discord Section
        discord_frame = ttk.LabelFrame(main_frame, text="💬 Discord Webhook", padding=15)
        discord_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(discord_frame, text="Discord Webhook URL:", font=("Segoe UI", 9)).pack(anchor=tk.W)
        discord_entry = ttk.Entry(discord_frame, width=60, font=("Courier", 9))
        discord_entry.insert(0, current_values.get("DISCORD_WEBHOOK_URL", ""))
        discord_entry.pack(fill=tk.X, pady=2)
        
        # Info label
        info_label = ttk.Label(main_frame, 
                              text="💡 Các thay đổi sẽ được lưu vào file .env và áp dụng ngay lập tức",
                              font=("Segoe UI", 8),
                              foreground="gray")
        info_label.pack(pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        def save_settings():
            """Lưu settings vào .env file"""
            try:
                # Prepare new values
                new_values = {
                    "AWS_ACCESS_KEY_ID": aws_key_entry.get().strip(),
                    "AWS_SECRET_ACCESS_KEY": aws_secret_entry.get().strip(),
                    "AWS_REGION": aws_region_entry.get().strip(),
                    "DISCORD_WEBHOOK_URL": discord_entry.get().strip()
                }
                
                # Read existing .env or create new
                env_lines = []
                if env_path.exists():
                    with open(env_path, 'r', encoding='utf-8') as f:
                        env_lines = f.readlines()
                
                # Update or add keys
                updated_keys = set()
                new_env_lines = []
                
                for line in env_lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#') and '=' in stripped:
                        key = stripped.split('=', 1)[0].strip()
                        if key in new_values:
                            new_env_lines.append(f"{key}={new_values[key]}\n")
                            updated_keys.add(key)
                        else:
                            new_env_lines.append(line)
                    else:
                        new_env_lines.append(line)
                
                # Add new keys that weren't in file
                for key, value in new_values.items():
                    if key not in updated_keys:
                        new_env_lines.append(f"{key}={value}\n")
                
                # Write back to file
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_env_lines)
                
                # Reload environment variables
                from dotenv import load_dotenv
                load_dotenv(env_path, override=True)
                
                messagebox.showinfo("Thành công", 
                                  "✅ Đã lưu cấu hình API keys!\n\n"
                                  "Các thay đổi đã được áp dụng.",
                                  parent=dialog)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"❌ Không thể lưu cấu hình:\n{e}", parent=dialog)
        
        ttk.Button(button_frame, text="💾 Lưu", command=save_settings, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Hủy", command=dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
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


    def _toggle_practice_pause(self):
        """Tạm dừng/Tiếp tục Practice Quiz"""
        if not hasattr(self, 'practice_paused'):
            self.practice_paused = False
        
        self.practice_paused = not self.practice_paused
        
        if self.practice_paused:
            self.practice_pause_btn.config(text="▶️ Tiếp tục", bg="#4caf50")
            self.practice_timer_label.config(text=f"⏸️ Tạm dừng ({self.practice_timer_seconds}s)", foreground="#ff9800")
        else:
            self.practice_pause_btn.config(text="⏸️ Tạm dừng", bg="#ff9800")
            self.practice_timer_label.config(text=f"⏱️ {self.practice_timer_seconds}s", foreground="#ff5722")
    
    def _toggle_voice_pause(self):
        """Tạm dừng/Tiếp tục Voice Quiz (ở tab Chuẩn bị)"""
        if not hasattr(self, 'voice_paused'):
            self.voice_paused = False
        
        self.voice_paused = not self.voice_paused
        
        if self.voice_paused:
            self.voice_pause_btn.config(text="▶️ Tiếp tục", bg="#4caf50")
            messagebox.showinfo("Tạm dừng", "Voice Quiz đã tạm dừng.\n\nBấm 'Tiếp tục' để làm tiếp.")
        else:
            self.voice_pause_btn.config(text="⏸️ Tạm dừng", bg="#ff9800")
            messagebox.showinfo("Tiếp tục", "Voice Quiz đã tiếp tục!")
    
    def _toggle_voice_quiz_pause(self):
        """Tạm dừng/Tiếp tục Voice Quiz (ở tab Voice Quiz)"""
        if not hasattr(self, 'voice_quiz_paused'):
            self.voice_quiz_paused = False
        
        self.voice_quiz_paused = not self.voice_quiz_paused
        
        if self.voice_quiz_paused:
            self.voice_quiz_pause_btn.config(text="▶️ TIẾP TỤC")
            messagebox.showinfo("⏸️ Tạm dừng", "Voice Quiz đã tạm dừng.\n\n📌 Nhấn 'Tiếp tục' để làm tiếp.")
        else:
            self.voice_quiz_pause_btn.config(text="⏸️ TẠM DỪNG")
            messagebox.showinfo("▶️ Tiếp tục", "Voice Quiz đã tiếp tục!")
    
    def _load_leaderboard(self):
        """Load top scores to leaderboard"""
        try:
            # Query database for top scores from study_log table
            conn = sqlite3.connect('study_history.db')
            cursor = conn.cursor()
            
            # Check if we have any quiz results saved
            # Since we don't have a quiz_results table, we'll show a placeholder
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='table' AND name='quiz_results'
            """)
            
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                # Create the table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS quiz_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_name TEXT NOT NULL,
                        score REAL NOT NULL,
                        total_questions INTEGER,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        language TEXT,
                        file_name TEXT
                    )
                """)
                conn.commit()
            
            # Get top 15 unique users with highest average scores
            cursor.execute("""
                SELECT 
                    user_name,
                    ROUND(AVG(score), 1) as avg_score,
                    MAX(score) as best_score,
                    COUNT(*) as attempts,
                    MAX(date) as last_date
                FROM quiz_results
                WHERE score IS NOT NULL
                GROUP BY user_name
                ORDER BY avg_score DESC, best_score DESC
                LIMIT 15
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            # Clear listbox
            self.leaderboard_list.delete(0, tk.END)
            
            if not results:
                self.leaderboard_list.insert(tk.END, "  Chưa có dữ liệu điểm số")
                self.leaderboard_list.insert(tk.END, "")
                self.leaderboard_list.insert(tk.END, "  💡 Làm bài kiểm tra để ghi điểm!")
                return
            
            # Header
            self.leaderboard_list.insert(tk.END, "  RANK  TÊN           AVG   BEST  TESTS")
            self.leaderboard_list.insert(tk.END, "  " + "="*40)
            
            # Display rankings with colors
            for idx, (name, avg, best, attempts, last_date) in enumerate(results, 1):
                # Truncate long names
                display_name = name[:12].ljust(12)
                line = f"  #{idx:<3} {display_name} {avg:>5.1f}  {best:>4.0f}  {attempts:>4}"
                
                self.leaderboard_list.insert(tk.END, line)
                
                # Color top 3
                if idx == 1:
                    self.leaderboard_list.itemconfig(idx+1, bg="#ffd700", fg="#000")  # Gold
                elif idx == 2:
                    self.leaderboard_list.itemconfig(idx+1, bg="#c0c0c0", fg="#000")  # Silver
                elif idx == 3:
                    self.leaderboard_list.itemconfig(idx+1, bg="#cd7f32", fg="#fff")  # Bronze
                    
        except Exception as e:
            self.leaderboard_list.delete(0, tk.END)
            self.leaderboard_list.insert(tk.END, f"  ⚠️ Lỗi: {str(e)}")

def main():
    root = tk.Tk()
    app = LanguageQuizGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
