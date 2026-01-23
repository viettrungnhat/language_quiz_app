# 🎓 Language Quiz Chatbot v2.0 - Voice Edition

Ứng dụng kiểm tra ngôn ngữ tự động với **giao diện đồ họa** và **kiểm tra bằng giọng nói**!

## 🎯 Tính Năng Chính

### ✨ v2.0 - Kiểm Tra Bằng Giọng Nói (MỚI)

- 🎤 **Hỏi bằng giọng nói** - Máy phát câu hỏi bằng tiếng nói
- 🎙️ **Trả lời bằng giọng nói** - Bạn nói câu trả lời vào microphone
- 🤖 **Đánh giá tự động** - Máy nhận dạng và so sánh câu trả lời
- ✅ **Chấm điểm tức thì** - Hiển thị điểm (0-10) ngay

### 📋 v1.1 - Giao Diện Đồ Họa

- 🖥️ **GUI 4 Tab** - Chuẩn bị, Kiểm tra thường, Kiểm tra giọng nói, Kết quả
- 📂 **Xử lý Excel trực tiếp** - Không cần chuyển JSON
- 📊 **Thống kê chi tiết** - Điểm, xếp loại A-F, phân tích

### 📚 v1.0 - Terminal

- 💬 **Kiểm tra terminal** - Menu dòng lệnh
- 🎯 **3 loại câu hỏi** - Meaning, Example, Vietnamese
- 🏆 **Chấm điểm 0-100** - Xếp loại A-F

## 🚀 Cài Đặt Nhanh

### Bước 1: Cài Packages

```bash
pip install pyttsx3 SpeechRecognition pyaudio openpyxl
```

**LƯU Ý Windows**: Nếu `pyaudio` gặp lỗi, tải `.whl` file từ [đây](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### Bước 2: Chạy Chương Trình

**Windows (Đơn giản)**:
```bash
python run_gui_v2.bat
```

**Hoặc chạy trực tiếp**:
```bash
python gui_main_v2.py
```

### Bước 3: Kiểm Tra Hệ Thống

```bash
python test_voice_system.py
```

## 📖 Hướng Dẫn Sử Dụng

### Voice Quiz (Kiểm Tra Giọng Nói)

1. **Chuẩn Bị**:
   - Kết nối microphone
   - Chọn file Excel
   - Chọn loại kiểm tra (Meaning/Example/Vietnamese)
   - Chọn số câu

2. **Kiểm Tra**:
   - Nhấn "🎤 KIỂM TRA GIỌNG NÓI"
   - Máy hiển thị + phát câu hỏi
   - Bạn nói câu trả lời
   - Nhấn "🎤 NGHE GIỌNG NÓI"
   - Máy đánh giá và chuyển câu tiếp theo

3. **Kết Quả**:
   - Tự động hiển thị tổng điểm
   - Xếp loại A-F
   - Lưu JSON

### Quiz Thường (Text-based)

1. Chọn file Excel
2. Nhấn "▶️ KIỂM TRA THƯỜNG"
3. Nhập câu trả lời từ bàn phím
4. Xem kết quả

## 📁 Cấu Trúc Dự Án

```
language_quiz_app/
├── gui_main_v2.py              # GUI v2.0 với Voice Quiz ⭐
├── voice_quiz.py               # Module giọng nói (TTS + STT)
├── quiz_engine.py              # Logic kiểm tra
├── scorer.py                   # Chấm điểm
├── data_loader.py              # Đọc dữ liệu
├── main.py                     # Terminal v1.0
├── create_templates.py         # Tạo template Excel
├── check_excel_format.py       # Kiểm tra định dạng Excel
├── test_voice_system.py        # Test hệ thống giọng nói
├── run_gui_v2.bat              # Launcher Windows
├── requirements.txt            # Dependencies
├── VOICE_QUIZ_GUIDE.txt        # Hướng dẫn chi tiết giọng nói
├── VOICE_QUICK_START.txt       # Quick start (5 phút)
├── GUI_GUIDE.txt               # Hướng dẫn GUI
├── README.md                   # File này
└── data/                       # Thư mục dữ liệu
    ├── TEMPLATE_ENGLISH.xlsx
    ├── TEMPLATE_CHINESE.xlsx
    └── TEMPLATE_JAPANESE.xlsx
```

## 🔧 Thành Phần Kỹ Thuật

### Libraries

- **pyttsx3** - Text-to-Speech (offline)
- **SpeechRecognition** - Speech-to-Text (Google)
- **pyaudio** - Điều khiển microphone
- **openpyxl** - Xử lý Excel
- **tkinter** - GUI (built-in)

### Modules

**voice_quiz.py**:
- `VoiceManager` - Quản lý TTS & STT
- `VoiceQuizManager` - Logic kiểm tra giọng nói

**gui_main_v2.py**:
- `LanguageQuizGUI` - Giao diện 4 tab
- Tab 1: Chuẩn bị
- Tab 2: Kiểm tra thường
- Tab 3: Kiểm tra giọng nói ⭐
- Tab 4: Kết quả

## 📊 Công Thức Chấm Điểm

### Kiểm Tra Thường (Text)

```
Lần 1: Đúng = 10 điểm | Tương tự = 8 | Sai = 0
Lần 2: Đúng = 7 điểm  | Tương tự = 5 | Sai = 0
Lần 3: Đúng = 4 điểm  | Sai = 0

Điểm tổng = (tổng điểm / số câu / 10) × 100
```

### Kiểm Tra Giọng Nói (Voice)

```
Độ tương đồng = So sánh câu trả lời với đáp án

100% → 10 điểm ✅
80-99% → 8-10 điểm
70-79% → 5-7 điểm
<70% → 0-4 điểm ❌
```

## ❓ Câu Hỏi Thường Gặp

### TTS (Text-to-Speech)

**Q: Máy không phát âm**
- A: Kiểm tra loa bật chưa? Chỉnh âm lượng cao hơn

**Q: Nói quá nhanh/quá chậm**
- A: Chỉnh trong voice_quiz.py: `setProperty('rate', 150)`

### STT (Speech-to-Text)

**Q: Không nhận dạng được giọng nói**
- A: Nói rõ ràng hơn + kiểm tra internet (Google STT cần internet)

**Q: Lỗi microphone**
- A: Kiểm tra kết nối + Settings → Sound → có microphone không?

### Installation

**Q: ModuleNotFoundError: pyttsx3**
- A: `pip install pyttsx3`

**Q: pyaudio cài không được (Windows)**
- A: Tải .whl file → `pip install /path/to/file.whl`

## 🎓 Ví Dụ Sử Dụng

### Kiểm Tra Tiếng Anh - Meaning

```
Máy: "What does 'beautiful' mean?"
Bạn: "something that is aesthetically pleasing"
Máy: "✅ Tốt! Độ chính xác 85%"
     "Điểm: 8/10"
```

### Kiểm Tra Tiếng Trung - Example

```
Máy: "Translate this example: 我很喜欢这个电影"
Bạn: "I really like this movie"
Máy: "✅ Chính xác 100%"
     "Điểm: 10/10"
```

## 📞 Hỗ Trợ

- **Kiểm tra hệ thống**: `python test_voice_system.py`
- **Xem chi tiết**: `VOICE_QUIZ_GUIDE.txt`
- **Quick start**: `VOICE_QUICK_START.txt`

## 🔐 Bảo Mật & Quyền Riêng Tư

- Google Speech Recognition gửi audio lên Google để xử lý
- Để offline: Dùng Vosk hoặc Whisper model
- Dữ liệu lưu locally (JSON file)

## 🚀 Tương Lai

- [ ] Offline speech recognition (Vosk)
- [ ] Accent analysis
- [ ] Performance charts
- [ ] Mobile version
- [ ] Multi-language TTS

## 📝 License

MIT License - Miễn phí sử dụng

## 👨‍💻 Tác Giả

Phát triển cho học sinh ngôn ngữ 🎓

---

**Bắt đầu**: `python gui_main_v2.py`

**Hỗ trợ**: Xem file hướng dẫn trong thư mục
