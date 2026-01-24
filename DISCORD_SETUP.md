# 📤 Discord Integration Setup Guide

## 🔒 Bảo Mật Discord Webhook

App sử dụng Discord webhook để tự động gửi kết quả quiz và ảnh học viên lên Discord channel.

### ⚠️ QUAN TRỌNG - BẢO MẬT

**KHÔNG BAO GIỜ** commit file `.env` lên GitHub! File này chứa:
- AWS credentials
- Discord webhook URL (có thể bị lạm dụng nếu lộ)

✅ File `.env` đã được thêm vào `.gitignore` để bảo vệ thông tin nhạy cảm.

---

## 🚀 Cách Setup Discord Webhook

### Bước 1: Tạo Discord Webhook

1. Mở Discord Server của bạn
2. Vào **Server Settings** (icon bánh răng)
3. Chọn **Integrations** > **Webhooks**
4. Click **"New Webhook"** hoặc chọn webhook có sẵn
5. Đặt tên cho webhook (ví dụ: "Quiz Bot")
6. Chọn channel mà webhook sẽ gửi tin (ví dụ: #quiz-results)
7. Click **"Copy Webhook URL"**

### Bước 2: Cấu Hình File .env

1. Copy file `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```

2. Mở file `.env` và điền thông tin:
   ```env
   # AWS Polly Configuration
   AWS_ACCESS_KEY_ID=your_aws_access_key_here
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
   AWS_REGION=ap-southeast-2

   # Discord Webhook
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
   ```

3. Paste Discord Webhook URL vào dòng `DISCORD_WEBHOOK_URL`

4. Lưu file

### Bước 3: Cài Đặt Dependencies

Nếu chưa cài, chạy:
```bash
pip install python-dotenv requests opencv-python
```

---

## 📋 Tính Năng Discord Integration

Khi hoàn thành quiz, app sẽ tự động gửi lên Discord:

### 📊 Nội dung gửi:
- 👤 Tên học viên
- 🕐 Thời gian làm bài
- 📈 Điểm trung bình & xếp loại
- 📋 Chi tiết 5 câu đầu tiên (hoặc tất cả nếu ≤5 câu)
- 📷 Ảnh chụp từ camera (nếu có)

### 🎯 Xử lý linh hoạt:
- ✅ Có camera → Gửi kết quả + ảnh
- ⚠️ Không có camera → Chỉ gửi kết quả text
- ❌ Lỗi chụp ảnh → Vẫn gửi kết quả text

---

## 🔧 Troubleshooting

### Lỗi: "DISCORD_WEBHOOK_URL không tìm thấy"
- Kiểm tra file `.env` có tồn tại không
- Kiểm tra đã điền `DISCORD_WEBHOOK_URL` chưa
- Restart app sau khi sửa `.env`

### Lỗi: "Discord webhook failed: 404"
- Webhook URL không đúng
- Webhook đã bị xóa trên Discord
- Tạo webhook mới và update `.env`

### Lỗi: "Discord webhook failed: 401"
- Token trong URL không hợp lệ
- Copy lại Webhook URL từ Discord

### Không chụp được ảnh
- Kiểm tra camera có hoạt động không
- Chọn đúng camera trong Settings > Camera
- App vẫn gửi kết quả text nếu không có ảnh

---

## 📚 Tham Khảo

- [Discord Webhooks Documentation](https://discord.com/developers/docs/resources/webhook)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)

---

## ✅ Checklist Setup

- [ ] Tạo Discord Webhook
- [ ] Copy file `.env.example` thành `.env`
- [ ] Điền AWS credentials vào `.env`
- [ ] Điền Discord Webhook URL vào `.env`
- [ ] Cài `python-dotenv`, `requests`, `opencv-python`
- [ ] Test gửi kết quả (làm quiz và kiểm tra Discord channel)
- [ ] Kiểm tra `.env` **KHÔNG** được commit lên GitHub

---

**🔐 Lưu ý cuối cùng:** 
Nếu vô tình commit `.env` lên GitHub:
1. Xóa file khỏi Git history
2. Tạo webhook mới trên Discord
3. Update `.env` với webhook URL mới
4. Thêm `.env` vào `.gitignore` (đã có sẵn)
