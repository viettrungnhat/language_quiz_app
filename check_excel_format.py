#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra format file Excel
Đảm bảo file đúng format: Word | Meaning | Example EN | Example VI
"""

import openpyxl
import sys
from pathlib import Path

def check_excel_format(file_path):
    """Kiểm tra format file Excel"""
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File không tồn tại: {file_path}")
        return False
    
    if not file_path.suffix.lower() == '.xlsx':
        print(f"❌ File không phải .xlsx: {file_path.suffix}")
        return False
    
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
    except Exception as e:
        print(f"❌ Lỗi mở file: {e}")
        return False
    
    print(f"📄 Kiểm tra: {file_path.name}")
    print(f"📊 Sheet có trong file: {wb.sheetnames}\n")
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        print(f"{'='*60}")
        print(f"📋 Sheet: {sheet_name}")
        print(f"{'='*60}")
        
        # Kiểm tra header
        header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]
        print(f"\n📌 Cột trong header: {len(header_row)}")
        print(f"   Header: {header_row[:4]}")
        
        if len(header_row) < 4:
            print(f"❌ LỖI: Phải có 4 cột, hiện tại chỉ có {len(header_row)}")
            print(f"   Format chuẩn: [Word] [Meaning] [Example EN] [Example VI]")
            continue
        
        # Kiểm tra dữ liệu
        valid_rows = 0
        error_rows = []
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row[0]:  # Dòng trống
                continue
            
            # Kiểm tra có đủ 4 cột không
            if len(row) < 4:
                error_rows.append((row_idx, f"Chỉ có {len(row)} cột"))
                continue
            
            # Kiểm tra cột Word & Meaning
            if row[0] and row[1]:
                valid_rows += 1
            else:
                error_rows.append((row_idx, f"Word hoặc Meaning trống"))
        
        print(f"\n✅ Dữ liệu hợp lệ: {valid_rows} câu hỏi")
        
        if error_rows:
            print(f"⚠️  Dòng lỗi: {len(error_rows)}")
            for row_idx, error in error_rows[:5]:
                print(f"   - Dòng {row_idx}: {error}")
            if len(error_rows) > 5:
                print(f"   ... và {len(error_rows) - 5} dòng nữa")
        
        # Hiển thị mẫu dữ liệu
        print(f"\n📝 Mẫu dữ liệu (5 dòng đầu):")
        print(f"{'─'*60}")
        
        sample_count = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            if sample_count >= 5:
                break
            if row[0]:
                word = str(row[0])[:20]
                meaning = str(row[1])[:20] if row[1] else "[trống]"
                print(f"  • {word:20} → {meaning}")
                sample_count += 1
        
        print()
    
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Tìm Excel file gần đây
        excel_files = list(Path(".").glob("*.xlsx"))
        if not excel_files:
            print("❌ Không tìm thấy file .xlsx nào")
            print("Cách dùng: python check_excel_format.py <file_path>")
            sys.exit(1)
        
        file_path = excel_files[0]
        print(f"📌 Không có file chỉ định, kiểm tra: {file_path}")
    
    check_excel_format(file_path)
