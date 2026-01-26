# 🚀 Quick Start - Tab Luyện Phát Âm

## ✅ Hoàn Thành 100%

Tab "🎤 Luyện phát âm" đã sẵn sàng sử dụng!

---

## 📥 Cách Chạy App

```powershell
cd "d:\Da Ngon Ngu\language_quiz_app"
$env:PYTHONIOENCODING="utf-8"
python gui_main_v2_new.py
```

**Hoặc** chạy trực tiếp (app đã fix encoding UTF-8)

---

## 📖 Hướng Dẫn Chi Tiết

### Step 1: Chọn File
1. Ấn nút **"📂 Chọn File Excel"**
2. Chọn file Excel (.xlsx) chứa từ vựng
3. File name sẽ hiển thị xanh ✅

### Step 2: Chọn Sheet
1. Dropdown **"Sheet:"** sẽ hiển thị tất cả sheets trong file
2. Chọn sheet cần học
3. Số câu sẽ **tự động cập nhật** ở "Đến:"

### Step 3: Cài Đặt Giọng (tuỳ chọn - có mặc định)
- **🎀 Nữ (Joanna)** - Mặc định ✅
- **🎩 Nam (Matthew)**

### Step 4: Cài Đặt Tốc Độ (tuỳ chọn - có mặc định)
- **0.5x** - Chậm hơn
- **1.0x** - Bình thường (Mặc định ✅)
- **1.5x** - Nhanh hơn

### Step 5: Chọn Loại Quiz
- **💬 Từ vựng** - Luyện phát âm từ đơn
- **📝 Câu ví dụ** - Luyện phát âm câu hoàn chỉnh

### Step 6: Chọn Chế Độ Test
- **VN → English/中文/日本語** - Mặc định ✅
- **English/中文/日本語 → VN**

### Step 7: Chọn Phạm Vi
- **Từ:** 1 (câu đầu tiên)
- **Đến:** 50 (hoặc tổng số câu trong file)

### Step 8: Ấn "▶️ BẮT ĐẦU LUYỆN PHÁT ÂM"
1. Nhập tên học sinh (nếu lần đầu)
2. Cửa sổ luyện tập sẽ mở ra 🎉

---

## 🎙️ Trong Cửa Sổ Luyện Tập

### Màn Hình Hiển Thị

```
👤 Anh | 📁 English.xlsx | 🌐 English
Tiến độ: 1/10  [=========>          ] 45%

┌─────────────────────────────────┐
│  1. hello                       │  ← Câu với thứ tự
└─────────────────────────────────┘

📚 Nghĩa: lời chào
📝 Ví dụ: Hello, how are you?
```

### Các Nút Điều Khiển

| Nút | Chức Năng | Khi Nào Dùng |
|-----|----------|------------|
| 🔊 Nghe lại | Phát lại từ/câu từ Polly | Khi muốn nghe lại |
| 🎙️ Luyện phát âm | Ghi âm phát âm bạn, so sánh, hiển thị kết quả | Chính yếu |
| ✅ Tiếp theo | Sang câu tiếp theo | Sau khi xem kết quả |
| ❌ Dừng | Kết thúc luyện tập | Khi muốn dừng |

### Khi Ấn "🎙️ Luyện phát âm"

1. **Ghi âm:** App ghi phát âm bạn (5 giây)
2. **So sánh:** So sánh với âm thanh Polly
3. **Kết quả:**
   ```
   ✅ ĐÚNG!
   
   📊 Điểm tương đồng: 92.5%
   ⭐ Mức độ: ⭐⭐⭐ Xuất sắc!
   
   🎉 Hoàn hảo! Tiếp tục nhé!
   ```
   
   **Hoặc** (nếu sai):
   ```
   ❌ SAI!
   
   📊 Điểm tương đồng: 45.2%
   ⭐ Mức độ: ❌ Tiếp tục luyện
   
   💡 Gợi ý: Bạn phát âm "hello" cần như âm thanh đã phát
   ```

### Mức Đánh Giá

| Điểm | Mức Độ | Ký Hiệu |
|-----|--------|--------|
| ≥ 90% | Xuất sắc | ⭐⭐⭐ |
| 75-90% | Tốt | ⭐⭐ |
| 60-75% | Có cải thiện | ⭐ |
| < 60% | Tiếp tục luyện | ❌ |

---

## 📊 Kết Quả Cuối Cùng

Sau khi luyện hết tất cả câu, app sẽ hiển thị:

```
🎉 KẾT QUẢ LUYỆN PHÁT ÂM

👤 Học sinh: Anh
📊 Tổng câu: 10
✅ Đúng: 8
❌ Sai: 2
📈 Độ chính xác: 80.0%

🔗 Kết quả đã được lưu vào Leaderboard
```

---

## 💾 Cài Đặt được Lưu Tự Động

App sẽ **nhớ** những thứ này cho lần sau:

✅ File đã chọn  
✅ Sheet đã chọn  
✅ Giọng (Nữ/Nam)  
✅ Tốc độ (0.5x/1.0x/1.5x)  
✅ Loại Quiz (Từ/Câu)  
✅ Chế độ Test (VN↔EN)  
✅ Phạm vi (Từ-Đến)  

**Lần sau:** Chỉ cần mở app, mọi cài đặt đã có sẵn!

---

## ⚙️ Nếu Có Lỗi

### Lỗi: "Unicode encoding error"
**Giải pháp:**
```powershell
$env:PYTHONIOENCODING="utf-8"
python gui_main_v2_new.py
```

### Lỗi: "File not found"
**Giải pháp:**
1. File Excel phải là format `.xlsx` (không .xls)
2. File phải có data từ row 2 trở đi
3. Kiểm tra path không có dấu cách lạ

### Lỗi: "Không thể ghi âm"
**Giải pháp:**
1. Kiểm tra mic được kết nối
2. Kiểm tra Windows cho phép app dùng mic
3. Ấn nút "🎙️ Luyện phát âm" chậm hơn sau khi ấn "🔊 Nghe lại"

---

## 💡 Mẹo & Thủ Thuật

### Phát Âm Đúng
✓ **Phát âm rõ ràng** - Không lúc lóc, lúc mềm  
✓ **Vận tốc tự nhiên** - Không quá chậm hay quá nhanh  
✓ **Xả hơi đủ** - Âm thanh phải đủ lớn để ghi  
✓ **Nghe kỹ Polly** - Polly đọc chuẩn, bạn bắt chước  

### Sử Dụng Hiệu Quả
✓ **Chọn phạm vi nhỏ** - 10-20 từ mỗi lần  
✓ **Luyện thường xuyên** - 15 phút mỗi ngày  
✓ **Lặp lại câu sai** - Ấn "🎙️ Luyện phát âm" nhiều lần  
✓ **Kiểm tra progess** - Xem Dashboard để theo dõi  

### File Excel Format

Cấu trúc file cần có:
```
Row 1: Header (Từ | Meaning | Ví dụ EN | Ví dụ VN)
Row 2: Data    (hello | lời chào | Hello, how are you? | Xin chào)
Row 3: Data    (world | thế giới | ...)
...
```

---

## 🎯 Tính Năng Sắp Ra Mắt

- [ ] Discord webhook cho kết quả  
- [ ] Export kết quả to CSV  
- [ ] Audio playback  
- [ ] Pitch detection cho tone languages  

---

## 📞 Hỗ Trợ

Nếu có vấn đề, hãy:
1. Kiểm tra lại các bước trên
2. Xem logs trong console
3. Thử restart app
4. Xóa cache: `Remove-Item __pycache__ -Recurse -Force`

---

**Happy learning! 🎉 Chúc bạn học tốt! 🌟**

Phiên bản: v2.2 | Ngày: 26/01/2026
