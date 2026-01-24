# 📖 Hướng Dẫn Cài Đặt - Language Quiz App

## 🎯 Mục Đích
Hướng dẫn chi tiết cho người mới clone dự án về máy trắng (chưa cài gì) để có thể sử dụng app ngay.

---

## ✅ Yêu Cầu Hệ Thống

### **Phần Cứng:**
- 💻 Windows 10/11 (hoặc macOS, Linux)
- 🎤 Microphone (cho tính năng Voice Quiz)
- 📷 Camera (tùy chọn - cho Discord photo submission)
- 🔊 Loa/Tai nghe (để nghe câu hỏi)

### **Phần Mềm:**
- 🐍 Python 3.10 trở lên ([Download tại đây](https://www.python.org/downloads/))
- 📦 pip (thường đi kèm với Python)
- 🌐 Kết nối Internet (cho Text-to-Speech và Speech Recognition)

---

## 🚀 Cài Đặt Nhanh (3 Phút)

### **Bước 1: Cài Python**

1. Tải Python từ: https://www.python.org/downloads/
2. **QUAN TRỌNG:** Khi cài đặt:
   - ✅ Tích chọn **"Add Python to PATH"**
   - ✅ Chọn **"Install Now"**

3. Kiểm tra cài đặt:
   ```cmd
   python --version
   ```
   Kết quả: `Python 3.10.x` hoặc cao hơn

### **Bước 2: Cài Thư Viện**

Mở Command Prompt/Terminal trong thư mục dự án và chạy:

```cmd
SETUP.bat
```

**Hoặc cài thủ công:**
```cmd
pip install -r requirements.txt
pip install requests opencv-python python-dotenv
```

### **Bước 3: Cấu Hình Discord (Tùy Chọn)**

Nếu muốn gửi kết quả lên Discord:

1. Đổi tên file `.env.example` → `.env`
2. Mở file `.env` và điền Discord Webhook URL:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_here
   ```
3. Xem chi tiết tại: [DISCORD_SETUP.md](DISCORD_SETUP.md)

### **Bước 4: Chạy Ứng Dụng**

```cmd
RUN_APP.bat
```

**Hoặc:**
```cmd
python gui_main_v2_new.py
```

---

## 🔧 Cài Đặt Thủ Công (Chi Tiết)

### **1. Kiểm tra Python và pip:**
```cmd
python --version
pip --version
```

### **2. Nâng cấp pip:**
```cmd
python -m pip install --upgrade pip
```

### **3. Cài từng thư viện:**
```cmd
pip install openpyxl>=3.0.0
pip install gtts>=2.2.4
pip install SpeechRecognition>=3.10.0
pip install pygame>=2.1.0
pip install requests
pip install opencv-python
pip install python-dotenv
```

### **4. Cài PyAudio (Cho Microphone):**

**Windows:**
- Tải wheel file phù hợp với Python version tại:
  https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Cài đặt:
  ```cmd
  pip install PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl
  ```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install python3-pyaudio
```

---

## 📁 Cấu Trúc Thư Mục Sau Khi Clone

```
language_quiz_app/
├── SETUP.bat                 # ← Chạy file này đầu tiên
├── RUN_APP.bat              # ← Chạy file này để khởi động app
├── gui_main_v2_new.py       # Main application
├── requirements.txt         # Danh sách thư viện
├── .env.example             # Template cho Discord config
├── DISCORD_SETUP.md         # Hướng dẫn Discord
├── README.md                # Tài liệu tổng quan
└── data/                    # Chứa file Excel mẫu
```

---

## 🎓 Sử Dụng Lần Đầu

### **1. Chuẩn Bị File Excel:**
- Sử dụng file mẫu trong thư mục `data/`
- Hoặc tạo file mới theo format:
  | Word | Meaning | Example EN | Example VI |
  |------|---------|------------|------------|
  | apple| táo     | I eat an apple | Tôi ăn táo |

### **2. Test Microphone:**
- Mở tab "Chuẩn bị"
- Chọn microphone từ danh sách
- Bấm "Test (5s)" để kiểm tra
- Nói thử vài câu để đảm bảo nhận dạng được

### **3. Chọn Camera (Tùy Chọn):**
- Chọn camera từ dropdown
- Ảnh sẽ tự động gửi kèm kết quả lên Discord

### **4. Bắt Đầu Quiz:**
- Chọn file Excel và sheet
- Chọn phạm vi câu hỏi (Từ... Đến...)
- Bấm "🎤 VOICE QUIZ" để bắt đầu

---

## ❓ Xử Lý Lỗi Thường Gặp

### **1. "Python không được nhận diện"**
```
'python' is not recognized as an internal or external command
```
**Giải pháp:**
- Cài lại Python và **tích chọn "Add Python to PATH"**
- Hoặc thêm Python vào PATH thủ công:
  - Mở System Properties → Environment Variables
  - Thêm đường dẫn Python vào PATH (VD: `C:\Python310\`)

### **2. "No module named 'openpyxl'"**
```
ModuleNotFoundError: No module named 'openpyxl'
```
**Giải pháp:**
```cmd
pip install openpyxl
```

### **3. "Could not find PyAudio"**
**Giải pháp:**
- Tải wheel file từ: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Cài đặt: `pip install PyAudio‑xxx.whl`

### **4. Microphone không hoạt động**
**Giải pháp:**
- Kiểm tra quyền truy cập microphone trong Windows Settings
- Chọn đúng microphone trong dropdown
- Thử test lại với nút "Test (5s)"

### **5. Camera không hiển thị**
**Giải pháp:**
- Cài OpenCV: `pip install opencv-python`
- Kiểm tra quyền truy cập camera
- Thử khởi động lại app

### **6. Discord webhook không gửi được**
**Giải pháp:**
- Kiểm tra file `.env` có đúng format
- Webhook URL phải bắt đầu bằng `https://discord.com/api/webhooks/`
- Xem chi tiết: [DISCORD_SETUP.md](DISCORD_SETUP.md)

---

## 🌟 Tính Năng Chính

✅ **Multi-Language Support:** English, Vietnamese, Chinese, Japanese  
✅ **Voice Quiz:** Nhận dạng giọng nói tức thì  
✅ **Semantic Scoring:** Chấm điểm thông minh với từ đồng nghĩa  
✅ **Discord Integration:** Tự động gửi kết quả + ảnh lên Discord  
✅ **Excel Import:** Hỗ trợ nhiều format Excel  
✅ **Practice Mode:** Ôn tập từ yếu  

---

## 📚 Tài Liệu Tham Khảo

- [README.md](README.md) - Tổng quan dự án
- [DISCORD_SETUP.md](DISCORD_SETUP.md) - Cấu hình Discord
- [FILE_CONVERTER_GUIDE.md](FILE_CONVERTER_GUIDE.md) - Hướng dẫn convert Excel
- [README_SEMANTIC_SCORING.md](README_SEMANTIC_SCORING.md) - Hệ thống chấm điểm

---

## 💬 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra file `FAQ.txt`
2. Xem các file `README_*.md`
3. Chạy lại `SETUP.bat`
4. Liên hệ developer

---

## 📝 Checklist Hoàn Tất

- [ ] Python 3.10+ đã cài đặt
- [ ] Tất cả thư viện đã cài (`pip list`)
- [ ] Microphone hoạt động (test thành công)
- [ ] Camera hoạt động (nếu cần)
- [ ] File `.env` đã cấu hình (nếu dùng Discord)
- [ ] Đã test chạy app thành công
- [ ] Đã thử 1 bài quiz mẫu

---

**🎉 Chúc bạn sử dụng app hiệu quả!**
