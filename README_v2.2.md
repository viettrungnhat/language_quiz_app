# 🎓 Language Quiz v2.2 - Voice Enhanced

Ứng dụng kiểm tra ngôn ngữ tiếng Anh với **Voice Quiz cải tiến**.

## 🎯 Tính Năng Mới (v2.2)

### ✨ Cải Tiến Giọng Nói
- **gTTS (Google Text-to-Speech)**: Phát âm chuẩn, tự nhiên
- **Google Speech Recognition**: Nhận dạng giọng nói chính xác
- **Đếm ngược 3 giây**: Chuẩn bị trước khi nói
- **Tự động flow**: Phát 2 lần → Đếm ngược → Lắng nghe → Đánh giá → Feedback

### 🎤 Voice Quiz Tự Động

```
📢 Câu hỏi (lần 1)
   ↓
📢 Câu hỏi (lần 2)
   ↓
⏳ Đếm ngược 3s: 3... 2... 1...
   ↓
🎤 Tự động lắng nghe
   ↓
✅/❌ Đánh giá tự động
   ↓
💬 Phát feedback (Đúng/Sai/Gần đúng)
   ↓
⏭️ Câu tiếp theo
```

### 📝 Feedback Bằng Giọng Nói

- **✅ Đúng**: "Đúng rồi! Hoàn hảo!"
- **⚠️ Gần đúng**: "Gần đúng rồi! Bạn phải nói là: [đáp án]"
- **❌ Sai**: "Sai rồi! Câu trả lời đúng là: [đáp án]"

## 📋 Cấu Hình

### Python Requirements
```bash
pip install -r requirements_v2.2.txt
```

**Gói chính:**
- `gtts>=2.3.0` - Google Text-to-Speech (thay pyttsx3)
- `SpeechRecognition>=3.10.0` - STT
- `pyaudio>=0.2.11` - Microphone
- `pygame>=2.0.0` - Audio playback
- `openpyxl>=3.0.0` - Excel file

### Microphone Setup (Windows)

1. **Kiểm tra microphone:**
   ```bash
   python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_indexes())"
   ```

2. **Chọn microphone mặc định:**
   - Settings → Sound → Input devices → Select microphone

## 🚀 Chạy Chương Trình

### Cách 1: Chạy file .bat (Windows)
```bash
run_v2_2.bat
```

### Cách 2: Chạy trực tiếp Python
```bash
python gui_main_v2_new.py
```

### Cách 3: Chạy từ Terminal
```bash
cd d:\Da Ngon Ngu\language_quiz_app
pip install -r requirements_v2.2.txt
python gui_main_v2_new.py
```

## 📊 Các Tab Chính

### 📋 Tab "Chuẩn Bị"
1. Chọn file Excel (khảo sát từ vựng)
2. Chọn sheet, loại kiểm tra, số câu
3. Nhấn **▶️ KIỂM TRA THƯỜNG** hoặc **🎤 VOICE QUIZ**

### 🎯 Tab "Kiểm Tra"
- Kiểm tra thường (gõ trả lời)
- Gợi ý nếu cần

### 🎤 Tab "Voice Quiz"
- **Tự động phát:** Máy hỏi 2 lần
- **Tự động lắng nghe:** Sau đếm ngược 3s
- **Tự động feedback:** Phát giọng nói (Đúng/Sai)
- **Tự động tiếp:** Câu hỏi tiếp theo

### 📊 Tab "Kết Quả"
- Xem điểm trung bình, xếp loại
- Chi tiết từng câu
- Lưu kết quả (JSON)

## 📁 File Excel Mẫu

**Cột:**
| A (Word) | B (Meaning) | C (Example EN) | D (Example VN) |
|----------|-----------|---|---|
| apple | a fruit | An apple a day keeps the doctor away | Một quả táo mỗi ngày tránh được bác sĩ |
| beautiful | attractive | This painting is beautiful | Bức tranh này rất đẹp |

## 🎨 Ngôn Ngữ Hỗ Trợ

### TTS (Phát âm)
- `en` - English (English)
- `vi` - Tiếng Việt
- `zh-cn` - 中文 (Chinese Simplified)
- `ja` - 日本語 (Japanese)

### STT (Nhận dạng)
- `en-US` - English (USA)
- `vi-VN` - Tiếng Việt
- `zh-CN` - Chinese Simplified
- `ja-JP` - Japanese

## ⚙️ Cấu Hình Nâng Cao

### Điều chỉnh nhạy cảm microphone

Mở `voice_quiz_v3.py`, sửa dòng:
```python
self.recognizer.energy_threshold = 4000  # Tăng = ít nhạy, Giảm = nhạy hơn
```

### Thay đổi ngôn ngữ feedback

Trong `gui_main_v2_new.py`, sửa:
```python
self.voice_manager.voice_manager.speak(feedback_text, language="vi")  # vi = Tiếng Việt
```

### Tăng thời gian lắng nghe

Mở `gui_main_v2_new.py`, tìm:
```python
user_answer = self.voice_manager.voice_manager.listen_to_microphone(timeout=15)
# Thay 15 thành số giây muốn
```

## 🐛 Xử Lý Sự Cố

### ❌ "Không nhận dạng được"
1. Kiểm tra kết nối internet (cần cho gTTS và STT)
2. Kiểm tra microphone: Settings → Sound → Input
3. Tăng `energy_threshold` trong voice_quiz_v3.py
4. Nói rõ ràng, to tiếng

### ❌ "gTTS không khả dụng"
```bash
pip install --upgrade gtts
```

### ❌ "pyaudio không cài được"
**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### ❌ Không nghe thấy tiếng phát
- Kiểm tra volume hệ thống
- Kiểm tra loa: Settings → Sound → Output
- Thử pygame với fallback: `pygame.mixer`

### ❌ File Excel không tải
- Đảm bảo file không open ở Excel
- Kiểm tra cột A, B, C, D có dữ liệu
- Lưu file dưới định dạng `.xlsx` (không `.xls`)

## 📈 Công Thức Tính Điểm

### Kiểm Tra Thường
```
Lần 1 đúng: 10 điểm
Lần 2 đúng: 7 điểm  
Lần 3 đúng: 4 điểm
Sai cả 3 lần: 0 điểm
```

### Voice Quiz
```
Điểm = Độ giống nhân 10 (0-10 điểm)
Ví dụ: Độ giống 85% = 8.5 điểm
```

### Xếp Loại
```
A: 90-100  (Xuất sắc)
B: 80-89   (Tốt)
C: 70-79   (Khá)
D: 60-69   (Đạt)
F: < 60    (Chưa đạt)
```

## 🔄 So Sánh: v2.0 vs v2.2

| Tính năng | v2.0 | v2.2 |
|---------|------|------|
| TTS | pyttsx3 (offline) | gTTS (online) ✨ |
| STT | Speech Recognition | Speech Recognition |
| Phát âm | Kém tự nhiên | Chuẩn ngôn ngữ ✨ |
| Nhận dạng | Bình thường | Cải tiến ✨ |
| Phát 2 lần | Không | Có ✨ |
| Đếm ngược | Không | 3 giây ✨ |
| Tự động lắng nghe | Không | Có ✨ |
| Feedback voice | Không | Phát bằng giọng ✨ |
| Auto-flow | Không | Hoàn toàn tự động ✨ |

## 📞 Liên Hệ & Báo Cáo Lỗi

Nếu gặp sự cố, kiểm tra:
1. Python 3.8+ cài đặt?
2. Tất cả dependencies trong `requirements_v2.2.txt` cài đặt?
3. Microphone kết nối và được chọn làm mặc định?
4. Internet kết nối (để gTTS hoạt động)?

---

**Version:** 2.2  
**Last Updated:** 2024  
**Language:** Python 3.8+  
**Author:** AI Assistant  
**License:** Free for educational use
