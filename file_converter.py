#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-detect và convert file Excel không chuẩn về format TEMPLATE
Tự động nhận dạng ngôn ngữ và cấu trúc
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from pathlib import Path
import re


def detect_language_from_sheet(sheet_name):
    """Nhận dạng ngôn ngữ từ tên sheet"""
    sheet_lower = sheet_name.lower()
    
    if "english" in sheet_lower or "anh" in sheet_lower or "eng" in sheet_lower:
        return "English"
    elif "chinese" in sheet_lower or "trung" in sheet_lower or "中文" in sheet_lower:
        return "Chinese"
    elif "japanese" in sheet_lower or "nhật" in sheet_lower or "日本" in sheet_lower:
        return "Japanese"
    elif "vietnam" in sheet_lower or "việt" in sheet_lower:
        return "Vietnamese"
    
    return None


def detect_file_structure(ws):
    """
    Detect cấu trúc file (kiểm tra các patterns)
    Return: ('structure_type', 'language', confidence)
    """
    
    # Check pattern: B1(meaning), B2(word), B3(meaning), B4(word)...
    # Và: D1(example_vi), D2(example), D3(example_vi), D4(example)...
    
    b1 = ws['B1'].value
    b2 = ws['B2'].value
    b3 = ws['B3'].value
    d1 = ws['D1'].value
    d2 = ws['D2'].value
    
    # Kiểm tra nếu B column là alternating pairs (meaning, word, meaning, word...)
    has_b_pattern = (b1 and b2 and b3 and 
                     len(str(b1)) < 50 and len(str(b2)) < 50 and len(str(b3)) < 50)
    
    # Kiểm tra nếu D column có cặp examples
    has_d_pattern = (d1 and d2 and len(str(d1)) > 10)
    
    if has_b_pattern and has_d_pattern:
        # Detect language
        jp_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
        
        # Kiểm tra từ B2 (word) có phải Nhật, Trung hay không
        if re.search(jp_pattern, str(b2)):
            if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', str(b2)):  # Hiragana/Katakana
                return "alternating_pairs", "Japanese", 0.95
            elif re.search(r'[\u4E00-\u9FFF]', str(b2)):  # Kanji
                return "alternating_pairs", "Chinese", 0.95
        
        return "alternating_pairs", "English", 0.85
    
    # Default TEMPLATE format
    return "template", None, 0.0


def is_template_format(ws):
    """Kiểm tra xem file đã là format TEMPLATE chưa"""
    try:
        # Check for 5-column format with No.
        headers_5col = [
            ws['A1'].value,
            ws['B1'].value,
            ws['C1'].value,
            ws['D1'].value,
            ws['E1'].value
        ]
        
        expected_5col = ["No.", "Word", "Meaning", "Example EN", "Example VI"]
        if all(h and str(h).strip() == e for h, e in zip(headers_5col, expected_5col)):
            return True
        
        # Check for 5-column Chinese format
        expected_5col_zh = ["No.", "Word", "Meaning", "Example ZH", "Example VI"]
        if all(h and str(h).strip() == e for h, e in zip(headers_5col, expected_5col_zh)):
            return True
        
        # Check for 5-column Japanese format
        expected_5col_ja = ["No.", "Word", "Meaning", "Example JA", "Example VI"]
        if all(h and str(h).strip() == e for h, e in zip(headers_5col, expected_5col_ja)):
            return True
        
        # Check for 4-column format (old format without No.)
        headers_4col = [
            ws['A1'].value,
            ws['B1'].value,
            ws['C1'].value,
            ws['D1'].value
        ]
        
        expected_4col = ["Word", "Meaning", "Example EN", "Example VI"]
        if all(h and str(h).strip() == e for h, e in zip(headers_4col, expected_4col)):
            return True
        
        # Check alternative headers (lowercase)
        expected_lower = ["word", "meaning", "example_en", "example_vi"]
        if all(h and str(h).strip().lower() == e for h, e in zip(headers_4col, expected_lower)):
            return True
        
        return False
    except:
        return False


def convert_alternating_pairs(input_ws, language="Japanese"):
    """Convert alternating pairs format to TEMPLATE"""
    
    rows_output = []
    row_idx = 1
    
    while True:
        # Get values from columns B and D (pairs)
        meaning = input_ws[f'B{row_idx}'].value
        word = input_ws[f'B{row_idx + 1}'].value
        example_vi = input_ws[f'D{row_idx}'].value
        example_lang = input_ws[f'D{row_idx + 1}'].value
        
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
        example_lang = str(example_lang).strip() if example_lang else ""
        
        # Append row
        rows_output.append([
            word,           # Column A: Word
            meaning,        # Column B: Meaning
            example_lang,   # Column C: Example EN/ZH/JA
            example_vi,     # Column D: Example VI
        ])
        
        row_idx += 2
    
    return rows_output


def convert_file_auto(input_path, output_path=None):
    """
    Convert file Excel tự động
    
    Return: (success, message, output_file_path)
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        return False, f"❌ File không tồn tại: {input_path}", None
    
    try:
        # Load file input
        wb_input = openpyxl.load_workbook(input_path)
        ws_input = wb_input.active
        
        # Check if already TEMPLATE format
        if is_template_format(ws_input):
            return True, "✅ File đã là format TEMPLATE, không cần convert", str(input_path)
        
        # Detect structure
        structure, detected_lang, confidence = detect_file_structure(ws_input)
        
        if structure == "alternating_pairs":
            # Detect language từ sheet name nếu không detect được
            if not detected_lang:
                detected_lang = detect_language_from_sheet(ws_input.title)
            
            detected_lang = detected_lang or "Japanese"
            
            # Convert
            rows_output = convert_alternating_pairs(ws_input, detected_lang)
            
            if not rows_output:
                return False, "❌ Không thể extract dữ liệu từ file", None
            
            # Create output file
            wb_output = openpyxl.Workbook()
            ws_output = wb_output.active
            
            # Set sheet name theo language
            sheet_names = {
                "Japanese": "Japanese",
                "Chinese": "Chinese",
                "English": "English",
                "Vietnamese": "Vietnamese"
            }
            ws_output.title = sheet_names.get(detected_lang, "Sheet1")
            
            # Add headers với cột số thứ tự
            headers = ["No.", "Word", "Meaning", "Example EN", "Example VI"]
            ws_output.append(headers)
            
            # Format header
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            for cell in ws_output[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            
            # Add data rows với số thứ tự
            for idx, row_data in enumerate(rows_output, start=1):
                ws_output.append([idx] + row_data)  # Thêm số thứ tự vào đầu
            
            # Auto-width columns
            ws_output.column_dimensions["A"].width = 8   # Số thứ tự (cột mới)
            for col in ["B", "C", "D", "E"]:  # Word, Meaning, Example EN, Example VI
                ws_output.column_dimensions[col].width = 25
            
            # Save output
            if output_path is None:
                output_name = f"{input_path.stem}_converted.xlsx"
                output_path = input_path.parent / output_name
            else:
                output_path = Path(output_path)
            
            wb_output.save(output_path)
            
            message = f"✅ Convert thành công!\n📝 Detected: {detected_lang}\n📊 Rows: {len(rows_output)}\n💾 Output: {output_path.name}"
            return True, message, str(output_path)
        
        else:
            return False, "❌ Không thể detect cấu trúc file", None
    
    except Exception as e:
        return False, f"❌ Lỗi: {str(e)}", None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_converter.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success, message, output_path = convert_file_auto(input_file, output_file)
    print(message)
    if success and output_path:
        print(f"📁 File output: {output_path}")
