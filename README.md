# 📚 HƯỚNG DẪN SỬ DỤNG CHATBOT KIỂM TRA NGÔN NGỮ

## 🚀 Cài đặt

### 1. Cài đặt Python (nếu chưa có)
```bash
# Tải từ https://www.python.org/downloads/
# Lựa chọn Python 3.8+
```

### 2. Cài đặt thư viện cần thiết
```bash
pip install openpyxl  # Để chuyển đổi Excel sang JSON
pip install python-dotenv  # Để quản lý AWS credentials
```

### 2.1 Cấu hình AWS Polly (cho tính năng Voice Quiz)

#### Bước 1: Tạo file `.env`
Copy file `.env.example` thành `.env` và điền AWS credentials:

```bash
cp .env.example .env
```

#### Bước 2: Điền thông tin AWS
Mở file `.env` và thêm:
```
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=ap-southeast-2
```

**Lưu ý**: 
- ⚠️ File `.env` chứa thông tin nhạy cảm - **KHÔNG** commit lên GitHub
- File `.env` đã được thêm vào `.gitignore`
- Chỉ cần cấu hình nếu sử dụng Voice Quiz (`voice_quiz_v3.py`)

### 3. Cấu trúc thư mục
```
language_quiz_app/
├── main.py              # Chương trình chính
├── quiz_engine.py       # Xử lý kiểm tra
├── scorer.py            # Chấm điểm
├── data_loader.py       # Load dữ liệu
├── excel_to_json.py     # Chuyển đổi Excel
└── data/
    ├── sample_english.json
    ├── sample_chinese.json
    ├── sample_japanese.json
    └── (các file JSON khác)
```

---

## 📖 Hướng dẫn sử dụng

### Chạy ứng dụng
```bash
python main.py
```

### Quy trình kiểm tra
1. **Chọn ngôn ngữ**: Anh / Trung / Nhật
2. **Chọn loại kiểm tra**:
   - Meaning: Hỏi ý nghĩa tiếng Việt
   - Example: Hỏi dịch ví dụ
   - Vietnamese: Dịch từ tiếng Việt sang
3. **Chọn số câu**: 5, 10, 15, 20 hoặc tất cả
4. **Trả lời câu hỏi**:
   - Nhập câu trả lời bình thường
   - Gõ `h` để nhận gợi ý
   - Gõ `c` để xem đáp án
5. **Xem kết quả**: Điểm, xếp loại và chi tiết từng câu

---

## 🔧 Cách thêm dữ liệu từ file Excel

### Bước 1: Chuẩn bị file Excel
Tạo file Excel với cột:

| A (word) | B (meaning) | C (example_en) | D (example_vi) |
|----------|------------|-----------------|-----------------|
| aunt | cô, dì | Is she your aunt? | Cô ấy là cô của bạn? |
| love | yêu, thích | Do you love it? | Bạn có yêu nó không? |

### Bước 2: Chuyển đổi thành JSON
```bash
python excel_to_json.py
```

Sau đó nhập tên file Excel và tên file JSON output.

### Bước 3: Chạy lại main.py
```bash
python main.py
```

Dữ liệu mới sẽ tự động xuất hiện trong danh sách chọn.

---

## 📊 Hệ thống chấm điểm

### Điểm từng câu (0-10):
- **10 điểm**: Lần 1 trả lời đúng chính xác
- **8 điểm**: Lần 1 trả lời gần đúng
- **7 điểm**: Lần 2 trả lời đúng
- **5-6 điểm**: Lần 2 gần đúng
- **4 điểm**: Lần 3 trả lời đúng
- **0 điểm**: Sai hoặc không trả lời

### Xếp loại cuối cùng (0-100):
- **A (90-100)**: Xuất sắc
- **B (80-89)**: Tốt
- **C (70-79)**: Khá
- **D (60-69)**: Đạt
- **F (<60)**: Chưa đạt

---

## ✨ Tính năng chính

✅ **3 ngôn ngữ**: Tiếng Anh, Trung, Nhật  
✅ **3 loại kiểm tra**: Ý nghĩa, Ví dụ, Dịch  
✅ **Linh hoạt số câu**: 5, 10, 15, 20 hoặc tất cả  
✅ **Cho phép sửa**: Tối đa 3 lần mỗi câu  
✅ **Gợi ý thông minh**: Gợi ý từ hoặc xem đáp án  
✅ **Chấm điểm chi tiết**: Từ 0-100  
✅ **Lưu kết quả**: Thống kê chi tiết mỗi câu  

---

## 💡 Ý tưởng mở rộng (tính năng nâng cao)

### Hiện tại đã có:
1. ✅ Kiểm tra 3 ngôn ngữ
2. ✅ 3 loại câu hỏi
3. ✅ Cho phép sửa lại
4. ✅ Chấm điểm 0-100
5. ✅ Gợi ý thông minh

### Có thể thêm sau:
1. **Lưu tiến độ học** → Biết từ nào yếu nhất
2. **Ôn tập từ yếu** → Mode chuyên biệt cho từ khó
3. **Giọng nói** → Text-to-speech (pip install pyttsx3)
4. **Phát âm** → So sánh phát âm học viên
5. **Thống kê chi tiết** → Biểu đồ tiến độ
6. **Chế độ thi** → Theo thời gian thực
7. **Hệ thống đánh giá** → Theo từng chủ đề
8. **Bài tập bổ trợ** → Các bài tập cụ thể cho từ yếu
9. **So sánh lịch sử** → Xem tiến độ qua ngày/tuần
10. **Export kết quả** → Xuất PDF, Excel

---

## 🐛 Khắc phục sự cố

**Lỗi: Không tìm thấy file dữ liệu**
- Kiểm tra thư mục `data/` có file JSON không
- Chạy lại để tạo file mẫu

**Lỗi: openpyxl not found**
```bash
pip install openpyxl
```

**Lỗi: Encoding (ký tự lạ)**
- Đảm bảo file Excel lưu dưới dạng UTF-8
- Hoặc dùng Python 3.8+

---

## 📞 Hỗ trợ
0986183806
Nếu có vấn đề, kiểm tra:
1. Python version >= 3.8
2. Thư mục `data/` có file JSON
3. Tên file Excel đúng (lưu ý chính tả)

Chúc học tập vui vẻ! 🎓
