#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converter: Chuyển file Excel custom sang format TEMPLATE
Cấu trúc input:
  B1: Meaning (Việt), B2: Word (Nhật)
  B3: Meaning (Việt), B4: Word (Nhật)
  ...
  
  D1: Example VI (Việt), D2: Example (Nhật)
  D3: Example VI (Việt), D4: Example (Nhật)
  ...
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from pathlib import Path
import sys


def convert_file(input_path, output_name=None):
    """
    Convert custom Excel file to TEMPLATE format
    
    Args:
        input_path: Đường dẫn file Excel input
        output_name: Tên file output (nếu None sẽ là TEMPLATE_JAPANESE_converted.xlsx)
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"❌ File không tồn tại: {input_path}")
        return False
    
    try:
        # Load file input
        print(f"📖 Đang load file: {input_path.name}")
        wb_input = openpyxl.load_workbook(input_path)
        ws_input = wb_input.active
        
        # Tạo workbook output
        wb_output = openpyxl.Workbook()
        ws_output = wb_output.active
        ws_output.title = "Japanese"  # ✅ Set sheet name để detect đúng language
        
        # Header - Match TEMPLATE format Y HỆT
        headers = ["Word", "Meaning", "Example EN", "Example VI"]
        ws_output.append(headers)
        
        # Format header
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in ws_output[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Parse input data
        # Column B: B1(Meaning), B2(Word), B3(Meaning), B4(Word), ...
        # Column D: D1(Example VI), D2(Example JA), D3(Example VI), D4(Example JA), ...
        
        row_count = 0
        row_idx = 1  # 1-indexed
        
        while True:
            # Get values from columns B and D (pairs)
            meaning = ws_input[f'B{row_idx}'].value
            word = ws_input[f'B{row_idx + 1}'].value
            example_vi = ws_input[f'D{row_idx}'].value
            example_ja = ws_input[f'D{row_idx + 1}'].value
            
            # Stop if no more data
            if not word and not meaning:
                break
            
            # Skip empty rows
            if not word:
                row_idx += 2
                continue
            
            # Convert to string and strip
            word = str(word).strip() if word else ""
            meaning = str(meaning).strip() if meaning else ""
            example_vi = str(example_vi).strip() if example_vi else ""
            example_ja = str(example_ja).strip() if example_ja else ""
            
            # Append row to output
            # ✅ Match TEMPLATE format: word | meaning | example_en (Nhật) | example_vi
            ws_output.append([
                word,           # Column A: word (Nhật)
                meaning,        # Column B: meaning (Việt)
                example_ja,     # Column C: example_en → Nhật
                example_vi,     # Column D: example_vi (Việt)
            ])
            
            row_count += 1
            row_idx += 2  # Move to next pair
            
            # Progress
            if row_count % 10 == 0:
                print(f"  ✓ Đã xử lý {row_count} từ vựng...")
        
        # Auto-width columns
        for col in ["A", "B", "C", "D"]:
            ws_output.column_dimensions[col].width = 25
        
        # Save output
        if output_name is None:
            output_name = f"TEMPLATE_JAPANESE_converted.xlsx"
        
        output_path = input_path.parent / output_name
        wb_output.save(output_path)
        
        print(f"\n✅ Chuyển đổi thành công!")
        print(f"📝 File output: {output_path}")
        print(f"📊 Tổng từ vựng: {row_count}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("📋 Cách dùng:")
        print("  python convert_custom_excel.py <input_file> [output_name]")
        print("\n📝 Ví dụ:")
        print("  python convert_custom_excel.py 'file nghe viet nhat.xlsx'")
        print("  python convert_custom_excel.py 'file nghe viet nhat.xlsx' 'TEMPLATE_JAPANESE.xlsx'")
        return
    
    input_file = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_file(input_file, output_name)


if __name__ == "__main__":
    main()

