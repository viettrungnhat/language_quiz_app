"""
Tạo file Excel template mẫu chuẩn
Chạy script này để tạo file template.xlsx
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os


def create_excel_template(filename="TEMPLATE_ENGLISH.xlsx"):
    """
    Tạo file Excel template với format chuẩn
    
    Format:
    ┌─────────┬──────────┬────────────┬────────────┐
    │ Word    │ Meaning  │ Example EN │ Example VI │
    ├─────────┼──────────┼────────────┼────────────┤
    │ (từ)    │ (ý nghĩa)│ (ví dụ)    │ (dịch)     │
    └─────────┴──────────┴────────────┴────────────┘
    """
    
    # Tạo workbook mới
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "English H2"
    
    # Tên cột
    columns = ["Word", "Meaning", "Example EN", "Example VI"]
    
    # Style cho header
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True, size=12)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    # Viền
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Thêm header (Hàng 1)
    for col_idx, column_name in enumerate(columns, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.value = column_name
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Dữ liệu mẫu
    sample_data = [
        ["aunt", "cô, dì, bác gái", "Is she your aunt?", "Cô ấy là cô của bạn phải không?"],
        ["love", "yêu, thích", "Do you love this song?", "Bạn có yêu thích bài hát này không?"],
        ["white", "màu trắng", "Is your shirt white?", "Áo của bạn màu trắng phải không?"],
        ["help", "giúp đỡ", "Can you help me?", "Bạn có thể giúp tôi không?"],
        ["hundred", "một trăm", "Do you have a hundred dollars?", "Bạn có 100 đô không?"],
        ["newspaper", "báo", "Do you read the newspaper?", "Bạn có đọc báo không?"],
        ["friend", "bạn", "Is he your friend?", "Anh ấy là bạn của bạn phải không?"],
        ["home", "nhà", "When do you go home?", "Bạn khi nào về nhà?"],
        ["school", "trường học", "What school do you attend?", "Bạn đi học ở trường nào?"],
        ["work", "làm việc", "Where do you work?", "Bạn làm việc ở đâu?"],
    ]
    
    # Thêm dữ liệu mẫu
    for row_idx, row_data in enumerate(sample_data, 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.value = value
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            cell.border = thin_border
    
    # Thêm dòng trống để người dùng nhập
    for row_idx in range(len(sample_data) + 2, len(sample_data) + 12):
        for col_idx in range(1, 5):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    
    # Điều chỉnh chiều rộng cột
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 35
    
    # Chiều cao hàng
    ws.row_dimensions[1].height = 25
    for row in range(2, len(sample_data) + 12):
        ws.row_dimensions[row].height = 40
    
    # Lưu file
    filepath = os.path.join("data", filename)
    wb.save(filepath)
    print(f"✓ Tạo template thành công: {filepath}")
    return filepath


def create_all_templates():
    """Tạo tất cả template cho 3 ngôn ngữ"""
    
    templates = {
        "TEMPLATE_ENGLISH.xlsx": {
            "sheet": "English H2",
            "data": [
                ["aunt", "cô, dì", "Is she your aunt?", "Cô ấy là cô của bạn không?"],
                ["love", "yêu, thích", "Do you love this?", "Bạn có yêu thích cái này không?"],
                ["white", "màu trắng", "Is it white?", "Nó có màu trắng không?"],
                ["help", "giúp", "Can you help?", "Bạn có thể giúp được không?"],
            ]
        },
        "TEMPLATE_CHINESE.xlsx": {
            "sheet": "Chinese H3",
            "data": [
                ["你好", "xin chào", "你好，我是李明。", "Xin chào, tôi là Lý Minh."],
                ["谢谢", "cảm ơn", "谢谢你的帮助。", "Cảm ơn bạn đã giúp tôi."],
                ["再见", "tạm biệt", "再见，明天见。", "Tạm biệt, ngày mai gặp lại."],
                ["对不起", "xin lỗi", "对不起，我迟到了。", "Xin lỗi, tôi đến muộn."],
            ]
        },
        "TEMPLATE_JAPANESE.xlsx": {
            "sheet": "Japanese H2",
            "data": [
                ["こんにちは", "xin chào", "こんにちは、お元気ですか?", "Xin chào, bạn khỏe không?"],
                ["ありがとう", "cảm ơn", "ありがとうございます。", "Cảm ơn bạn rất nhiều."],
                ["さようなら", "tạm biệt", "さようなら、また明日。", "Tạm biệt, ngày mai gặp lại."],
                ["すみません", "xin lỗi", "すみません、間違えました。", "Xin lỗi, tôi sai rồi."],
            ]
        }
    }
    
    for filename, config in templates.items():
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = config["sheet"]
        
        # Header
        columns = ["Word", "Meaning", "Example EN", "Example VI"]
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=12)
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        
        for col_idx, col_name in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = col_name
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = thin_border
        
        # Dữ liệu
        for row_idx, row_data in enumerate(config["data"], 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.value = value
                cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                cell.border = thin_border
        
        # Thêm hàng trống
        for row_idx in range(len(config["data"]) + 2, len(config["data"]) + 12):
            for col_idx in range(1, 5):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = thin_border
        
        # Điều chỉnh cột
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 30
        ws.column_dimensions['D'].width = 35
        
        filepath = os.path.join("data", filename)
        wb.save(filepath)
        print(f"✓ Tạo: {filename}")


if __name__ == "__main__":
    print("Tạo file template Excel...")
    print("="*50)
    
    # Kiểm tra thư mục data
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Tạo tất cả template
    create_all_templates()
    
    print("="*50)
    print("✓ Tất cả template đã tạo xong!")
    print("\nHướng dẫn sử dụng:")
    print("1. Mở file template từ thư mục data/")
    print("2. Sửa dữ liệu mẫu hoặc thêm dữ liệu mới")
    print("3. Chạy GUI: python gui_main.py")
    print("4. Chọn file Excel trong GUI")
