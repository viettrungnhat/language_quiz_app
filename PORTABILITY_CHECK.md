# ✅ KIỂM TRA PORTABILITY - Dự Án Có Thể Chạy Trên Máy Khác

## 📋 Tóm Tắt Kiểm Tra
Dự án **CÓ THỂ chạy bình thường** trên máy khác (copy hoặc clone từ GitHub)

---

## ✅ Điểm Tốt

### 1. **Relative Paths** (Tất cả đường dẫn tương đối)
- ✅ `Path(__file__).parent` dùng để get app folder
- ✅ Không có hardcoded paths như `d:\Da Ngon Ngu\...` ở code Python
- ✅ Có thể copy folder sang bất kỳ đâu vẫn chạy được

### 2. **Dependencies Có Trong requirements.txt**
```
✅ openpyxl>=3.0.0         # Excel support
✅ python-dotenv            # Environment variables
✅ gtts>=2.2.4             # Google TTS
✅ SpeechRecognition>=3.10.0 # Google STT
✅ pygame>=2.1.0           # Audio playback
✅ boto3                    # AWS Polly (optional)
```

### 3. **Environment Variables**
- ✅ `.env.example` có sẵn (template)
- ✅ `.env` được thêm vào `.gitignore` (secure)
- ✅ AWS credentials không hardcoded
- ✅ Dùng `load_dotenv()` để load từ `.env`

### 4. **Data Files**
- ✅ Template Excel files có sẵn: `data/TEMPLATE_*.xlsx`
- ✅ Sample JSON files có sẵn: `data/sample_*.json`
- ✅ Database `study_history.db` tạo tự động (SQLite)
- ✅ `results/` folder tạo tự động khi chạy

### 5. **Configuration Files**
- ✅ `user_settings.json` tạo tự động
- ✅ `logo.ico` có sẵn
- ✅ `.gitignore` chính xác

### 6. **Python Version Compatibility**
- ✅ Dùng Python 3.8+ (compatible)
- ✅ Không dùng features Python mới

---

## ⚠️ Cần Lưu Ý

### 1. **AWS Credentials (Optional)**
Nếu sử dụng Voice Quiz (AWS Polly):
- ⚠️ Phải tạo file `.env` từ `.env.example`
- ⚠️ Phải có AWS credentials (IAM user + access key)
- ✅ Nếu không có → App vẫn chạy (fallback to gTTS)

### 2. **Microphone Support**
- ⚠️ Máy phải có microphone để dùng Voice Quiz
- ✅ Nếu không có → Chỉ dùng Text Quiz được

### 3. **Internet Connection**
- ⚠️ Cần internet cho:
  - Google STT (Speech Recognition)
  - gTTS (Text-to-Speech)
  - AWS Polly (nếu dùng)

---

## 🚀 Hướng Dẫn Chạy Trên Máy Mới

### Bước 1: Clone hoặc Copy Project
```bash
# Clone từ GitHub
git clone <repo_url> language_quiz_app
cd language_quiz_app

# Hoặc copy folder sang máy khác
```

### Bước 2: Cài Đặt Dependencies
```bash
pip install -r requirements.txt

# Nếu có issue với PyAudio:
# pip install --only-binary :all: pyaudio
```

### Bước 3: Tạo .env File (Optional - Chỉ Cho Voice Quiz)
```bash
# Copy template
cp .env.example .env

# Sửa .env thêm AWS credentials (nếu có):
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_REGION=ap-southeast-2
```

### Bước 4: Chạy App
```bash
# Chạy GUI
python gui_main_v2_new.py

# Hoặc chạy script batch (Windows)
run_gui.bat
```

---

## 📁 File Structure (Tự Tạo)

Những file/folder này sẽ **tự động tạo** khi chạy:
```
language_quiz_app/
├── results/                    # 📁 Tạo tự động - lưu kết quả quiz
├── study_history.db            # 📄 Tạo tự động - SQLite database
├── user_settings.json          # 📄 Tạo tự động - cài đặt người dùng
├── __pycache__/                # 📁 Tạo tự động - bytecode cache
└── .env                        # 📄 Tạo thủ công - AWS credentials
```

---

## ✅ Danh Sách Kiểm Tra Cho GitHub

Khi push lên GitHub, đảm bảo:

```
✅ .gitignore có chứa:
   - .env (AWS credentials)
   - __pycache__/
   - *.db (Database)
   - results/ (User results)
   - user_settings.json

✅ .env.example có (template)
✅ requirements.txt có (dependencies)
✅ README.md có hướng dẫn cài đặt
✅ data/ folder có (templates)
✅ .git/ folder có (version control)
```

---

## 🎯 Tóm Tắt: Có Thể Copy Sang Máy Khác!

| Yếu Tố | Trạng Thái | Ghi Chú |
|--------|-----------|---------|
| Relative Paths | ✅ OK | Dùng `Path(__file__).parent` |
| Dependencies | ✅ OK | Trong `requirements.txt` |
| Data Files | ✅ OK | Templates có sẵn |
| Config | ✅ OK | Tạo tự động |
| Secrets (.env) | ✅ OK | `.env` trong `.gitignore` |
| Database | ✅ OK | SQLite tạo tự động |
| Results | ✅ OK | Folder tạo tự động |

**Kết Luận**: Dự án **100% portable** - Có thể copy sang máy khác và chạy ngay! 🚀

