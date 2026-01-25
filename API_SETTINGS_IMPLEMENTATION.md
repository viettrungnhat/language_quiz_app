# ⚙️ In-App API Settings Implementation

## 📋 Tổng quan

Thay vì sử dụng GitHub Gist (phức tạp), đã implement Settings Dialog **trực tiếp trong app** để người dùng có thể xem và chỉnh sửa API keys dễ dàng.

---

## ✨ Tính năng mới

### 1. **Nút "⚙️ Cài đặt API"**
- Vị trí: Tab "📋 Chuẩn bị" > Frame "📁 File & Sheet"
- Nằm cạnh nút "Chọn File Excel"
- Click để mở Settings Dialog

### 2. **Settings Dialog**
Dialog 600x400px với các trường:

#### ☁️ AWS Polly Section:
- **AWS Access Key ID**: Entry field (plain text)
- **AWS Secret Access Key**: Entry field (password masked với `show="*"`)
- **AWS Region**: Entry field (default: ap-southeast-2)

#### 💬 Discord Section:
- **Discord Webhook URL**: Entry field (plain text)

#### 💾 Buttons:
- **Lưu**: Lưu vào file `.env` và reload environment variables
- **Hủy**: Đóng dialog không lưu

---

## 🔧 Implementation Details

### File Changes:

#### 1. **gui_main_v2_new.py**

**Dòng 237-252**: Thêm nút Settings vào file frame
```python
# Row 0: File button và Settings button
file_row = ttk.Frame(file_frame)
file_row.grid(row=0, column=0, columnspan=2, sticky=tk.EW, pady=3)

ttk.Button(file_row, text="Chọn File Excel", 
          command=self.select_excel_file, width=20).pack(side=tk.LEFT, padx=(0, 5))

ttk.Button(file_row, text="⚙️ Cài đặt API", 
          command=self.open_settings_dialog, width=15).pack(side=tk.LEFT)
```

**Dòng 3115-3255**: Method `open_settings_dialog()`
- Load giá trị hiện tại từ `.env`
- Tạo dialog với các entry fields
- Save settings callback:
  - Parse các giá trị mới
  - Cập nhật file `.env` (preserve comments)
  - Reload environment variables với `load_dotenv(override=True)`
  - Hiển thị thông báo thành công

#### 2. **aws_config.py**
Revert về code đơn giản:
```python
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-2")
```

#### 3. **gui_main_v2_new.py - Discord webhook**
Revert về load từ `.env`:
```python
from dotenv import load_dotenv
load_dotenv()
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
```

#### 4. **.env.example**
Đơn giản hóa, xóa phần GitHub Gist:
```env
# AWS Polly Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=ap-southeast-2

# Discord Webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

#### 5. Files Deleted:
- ❌ `gist_config.py`
- ❌ `GIST_SETUP_GUIDE.md`
- ❌ `GIST_CONFIG_IMPLEMENTATION.md`

---

## 🎯 User Experience

### Before (Gist approach):
1. Tạo GitHub account
2. Tạo Gist trên GitHub
3. Copy Gist ID
4. Edit `.env` file
5. Thêm `GITHUB_GIST_ID`
6. Restart app

❌ **Phức tạp**, yêu cầu GitHub account

### After (In-app Settings):
1. Click "⚙️ Cài đặt API"
2. Điền/chỉnh sửa keys
3. Click "Lưu"

✅ **Đơn giản**, tất cả trong app

---

## 📸 UI Layout

```
┌─────────────────────────────────────────┐
│  ⚙️ Cài đặt API Keys                    │
├─────────────────────────────────────────┤
│  🔐 Cấu hình API Keys                   │
│                                         │
│  ☁️ AWS Polly (Text-to-Speech)         │
│  ┌─────────────────────────────────┐   │
│  │ AWS Access Key ID:              │   │
│  │ [AKIAIOSFODNN7EXAMPLE______]    │   │
│  │                                 │   │
│  │ AWS Secret Access Key:          │   │
│  │ [************************]       │   │
│  │                                 │   │
│  │ AWS Region:                     │   │
│  │ [ap-southeast-2___________]     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  💬 Discord Webhook                     │
│  ┌─────────────────────────────────┐   │
│  │ Discord Webhook URL:            │   │
│  │ [https://discord.com/api/___]   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  💡 Thay đổi sẽ lưu vào .env           │
│                                         │
│     [💾 Lưu]    [❌ Hủy]              │
└─────────────────────────────────────────┘
```

---

## 🔐 Security

### ✅ Maintained:
- File `.env` vẫn trong `.gitignore`
- AWS Secret Key được mask (`show="*"`)
- Không commit sensitive data lên Git

### ⚠️ Note:
- Keys lưu dạng plaintext trong `.env` (tương tự cách cũ)
- User có trách nhiệm bảo vệ file `.env`

---

## 💡 Benefits

### For Users:
✅ Không cần GitHub account  
✅ Cài đặt nhanh trong vài click  
✅ Xem được keys hiện tại  
✅ Thay đổi áp dụng ngay lập tức  
✅ UI thân thiện, không cần edit file thủ công

### For Developers:
✅ Code đơn giản hơn (không cần Gist API)  
✅ Ít dependencies (không cần `requests` cho Gist)  
✅ Dễ debug (chỉ cần check `.env`)  
✅ Standard approach (dotenv pattern)

---

## 🧪 Testing

### Test Case 1: Fresh Install
1. App khởi động, chưa có `.env`
2. Click "⚙️ Cài đặt API"
3. Điền keys → Click "Lưu"
4. ✅ File `.env` được tạo với keys mới

### Test Case 2: Update Existing
1. Đã có `.env` với keys cũ
2. Click "⚙️ Cài đặt API"
3. ✅ Entry fields hiển thị keys hiện tại
4. Sửa AWS Region → Click "Lưu"
5. ✅ File `.env` được cập nhật, giữ nguyên comments

### Test Case 3: Cancel
1. Click "⚙️ Cài đặt API"
2. Sửa keys → Click "Hủy"
3. ✅ Không thay đổi gì

---

## 📝 .env File Format

File `.env` sau khi save:
```env
# Comments được giữ nguyên
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCY
AWS_REGION=ap-southeast-2
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/abc

# Các dòng khác không bị ảnh hưởng
```

---

## 🚀 Future Enhancements

Có thể thêm:
1. **Validate keys**: Check AWS keys có hoạt động không
2. **Test buttons**: Test AWS Polly, test Discord webhook
3. **Import/Export**: Export config sang file, import từ file
4. **Multiple profiles**: Dev/Staging/Prod profiles
5. **Show/Hide password**: Toggle visibility cho secret key

---

## 📞 Support

- Implementation Date: January 25, 2026
- Status: ✅ Complete & Tested
- Approach: In-app settings dialog (Simple & User-friendly)
