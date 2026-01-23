"""
Script chuyển đổi dữ liệu từ file Excel sang JSON
Hướng dẫn: 
1. Chuẩn bị file Excel với cột: word, meaning, example_en, example_vi
2. Chạy script này để chuyển đổi
"""

import openpyxl
import json
import os
from pathlib import Path

def convert_excel_to_json(excel_file, json_file, sheet_name=0):
    """
    Chuyển đổi file Excel sang JSON
    
    Yêu cầu cột trong Excel:
    - Column A: word (từ vựng)
    - Column B: meaning (ý nghĩa tiếng Việt)
    - Column C: example_en (ví dụ tiếng Anh)
    - Column D: example_vi (ví dụ tiếng Việt)
    """
    try:
        # Đọc file Excel
        workbook = openpyxl.load_workbook(excel_file)
        worksheet = workbook.active
        
        data = []
        question_id = 1
        
        # Bỏ qua dòng tiêu đề (dòng 1)
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            # Kiểm tra dòng trống
            if not row[0]:  # Nếu cột đầu tiên trống, bỏ qua
                continue
            
            item = {
                "id": question_id,
                "word": str(row[0]).strip() if row[0] else "",
                "meaning": str(row[1]).strip() if row[1] else "",
                "example_en": str(row[2]).strip() if row[2] else "",
                "example_vi": str(row[3]).strip() if row[3] else ""
            }
            
            # Kiểm tra dữ liệu hợp lệ
            if item["word"] and item["meaning"]:
                data.append(item)
                question_id += 1
        
        # Lưu vào file JSON
        output_path = os.path.join("data", json_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Chuyển đổi thành công!")
        print(f"  - File Excel: {excel_file}")
        print(f"  - File JSON: {output_path}")
        print(f"  - Số câu: {len(data)}")
        
        return True
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("Hãy kiểm tra:")
        print("  1. File Excel tồn tại không?")
        print("  2. Đã cài openpyxl chưa? (pip install openpyxl)")
        print("  3. Cột dữ liệu đúng không?")
        return False

def list_excel_files():
    """Liệt kê file Excel trong thư mục"""
    print("\n📂 Các file Excel có sẵn:")
    for file in os.listdir(".."):
        if file.endswith(".xlsx") or file.endswith(".xls"):
            print(f"  - {file}")

if __name__ == "__main__":
    print("="*60)
    print("  CHUYỂN ĐỔI EXCEL SANG JSON")
    print("="*60)
    
    list_excel_files()
    
    # Ví dụ chuyển đổi
    excel_file = input("\nNhập tên file Excel (vd: 'file sach h2 anh.xlsx'): ").strip()
    
    if not os.path.exists(f"../{excel_file}"):
        print(f"❌ Không tìm thấy file {excel_file}")
    else:
        json_file = input("Nhập tên file JSON output (vd: 'english_h2.json'): ").strip()
        if not json_file.endswith(".json"):
            json_file += ".json"
        
        convert_excel_to_json(f"../{excel_file}", json_file)
