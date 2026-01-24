#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📖 FILE CONVERTER - AUTO-DETECT & AUTO-CONVERT

Tính năng Auto-Detect và Convert file Excel không chuẩn về format TEMPLATE

========================================================================
🎯 TỬA NĂNG CỦA FILE_CONVERTER
========================================================================

1. AUTO-DETECT FILE FORMAT
   - Kiểm tra tự động cấu trúc file
   - Detect language (Japanese, Chinese, English, Vietnamese)
   - Tính confidence level

2. AUTO-CONVERT
   - Convert alternating_pairs format → TEMPLATE format
   - Tự động nhận dạng và convert
   - Lưu file output mới (.._converted.xlsx)

3. INTEGRATION VỚI GUI
   - Khi import file, tự động check format
   - Nếu không chuẩn, hỏi user có convert không
   - Auto-convert nếu user đồng ý

========================================================================
📝 FILE FORMATS DETECTED
========================================================================

FORMAT 1: TEMPLATE (Chuẩn)
┌────┬──────────┬──────────┬──────────────┬──────────────┐
│    │ A: Word  │ B: Mean  │ C: Example EN│ D: Example VI│
├────┼──────────┼──────────┼──────────────┼──────────────┤
│ 1  │ Headers  │ Headers  │ Headers      │ Headers      │
│ 2  │ 日本語1  │ Meaning1 │ Example EN 1 │ Example VI 1 │
│ 3  │ 日本語2  │ Meaning2 │ Example EN 2 │ Example VI 2 │
└────┴──────────┴──────────┴──────────────┴──────────────┘

FORMAT 2: ALTERNATING PAIRS (Cần Convert)
┌────┬────┬──────────────┬────┬──────────────────┐
│    │ A  │ B            │ C  │ D                │
├────┼────┼──────────────┼────┼──────────────────┤
│ 1  │    │ Meaning 1    │    │ Example VI 1     │
│ 2  │    │ 日本語1      │    │ Example EN/ZH/JA │
│ 3  │    │ Meaning 2    │    │ Example VI 2     │
│ 4  │    │ 日本語2      │    │ Example EN/ZH/JA │
└────┴────┴──────────────┴────┴──────────────────┘

Convert thành:
┌────┬──────────┬──────────┬──────────────┬──────────────┐
│    │ A: Word  │ B: Mean  │ C: Example   │ D: Example VI│
├────┼──────────┼──────────┼──────────────┼──────────────┤
│ 1  │ Headers  │ Headers  │ Headers      │ Headers      │
│ 2  │ 日本語1  │ Meaning1 │ Example EN 1 │ Example VI 1 │
│ 3  │ 日本語2  │ Meaning2 │ Example EN 2 │ Example VI 2 │
└────┴──────────┴──────────┴──────────────┴──────────────┘

========================================================================
🚀 CÁCH SỬ DỤNG
========================================================================

1. PROGRAMMATIC USAGE
   ────────────────────────────────────────────────────

   from file_converter import convert_file_auto
   
   success, message, output_path = convert_file_auto(
       input_path="path/to/file.xlsx",
       output_path="path/to/output.xlsx"  # Optional
   )
   
   if success:
       print(f"✅ Converted: {output_path}")
   else:
       print(f"❌ Error: {message}")

2. COMMAND LINE USAGE
   ────────────────────────────────────────────────────

   python file_converter.py path/to/file.xlsx [output_file.xlsx]

3. GUI INTEGRATION (AUTO)
   ────────────────────────────────────────────────────

   Khi chọn file trong GUI:
   - Auto-detect format
   - Nếu không chuẩn → Dialog hỏi convert
   - User chọn Yes/No
   - Auto-convert nếu Yes

========================================================================
🔍 DETECTION ALGORITHM
========================================================================

Kiểm tra 3 điều kiện:

1. Column B Pattern (Alternating Meaning-Word)
   ✓ B1 có text (meaning)
   ✓ B2 có text (word - ngôn ngữ)
   ✓ B3 có text (meaning)
   ✓ Tất cả < 50 ký tự

2. Column D Pattern (Examples)
   ✓ D1 có text (example VI)
   ✓ D2 có text (example in language)
   ✓ D1 có > 10 ký tự

3. Language Detection (từ Column B)
   ✓ Japanese: Contains Hiragana/Katakana (ひらがな/カタカナ) or Kanji
   ✓ Chinese: Contains Hanzi (汉字/漢字)
   ✓ English: ASCII alphabets

CONFIDENCE SCORE:
   - Alternating pairs + language detected = 95%
   - Alternating pairs + no language = 85%

========================================================================
📊 HÌNH VỊ DETECTION
========================================================================

Ví dụ 1: Japanese Alternating Pairs
────────────────────────────────────

File gốc:
   B1: "ひらがなの意味" (meaning)
   B2: "ひらがな" (japanese word with hiragana)
   D1: "これはひらがなの例です" (example VI)
   D2: "これはひらがなの例です" (example EN)

Detection: 
   - B có alternating pattern ✓
   - B2 có Hiragana → Language = Japanese ✓
   - Confidence: 95%

Result: Auto-convert thành TEMPLATE

========================================================================
⚙️ ADVANCED OPTIONS
========================================================================

1. CHECK FORMAT ONLY (không convert)
   ────────────────────────────────

   from file_converter import detect_file_structure, is_template_format
   
   structure, language, confidence = detect_file_structure(ws)
   is_template = is_template_format(ws)

2. DETECT LANGUAGE ONLY
   ────────────────────────────────

   from file_converter import detect_language_from_sheet
   
   lang = detect_language_from_sheet("Sheet Name")

========================================================================
🛠️ TROUBLESHOOTING
========================================================================

Problem: File detected as wrong language
Fix:
   - Check Column B format (should be alternating)
   - Ensure row 1 is data (not headers)
   - Check language characters in Column B Row 2

Problem: File not detected as convertible
Fix:
   - Verify format is alternating_pairs
   - Check if it already is TEMPLATE
   - Ensure min 2 rows of data

Problem: Convert output has empty rows
Fix:
   - Check source file for empty cells
   - Verify Column D has examples

========================================================================
📝 EXAMPLE FILES
========================================================================

✅ Auto-detectable:
   - "200 câu đố nhật việt 25072025.xlsx"
     → Structure: alternating_pairs
     → Language: Japanese
     → Confidence: 95%
     → Result: 141 rows extracted ✅

========================================================================
🔄 WORKFLOW
========================================================================

User opens GUI
   ↓
User clicks "Chọn File Excel"
   ↓
System detects file format
   ├─ Is TEMPLATE? → Load directly
   └─ Not TEMPLATE? → Show dialog
       ↓
    Dialog: "Convert này?"
       ├─ YES → Auto-convert
       │   ↓
       │   Create output file (_converted.xlsx)
       │   Show result
       │   Load converted file
       └─ NO → Use original
           (May cause errors if format wrong)

========================================================================
📞 SUPPORT
========================================================================

For issues with file conversion:
1. Check file structure (B and D columns)
2. Ensure data starts from row 1 (no headers)
3. Check language characters in row 2
4. Use test_converter.py to scan your files

"""

if __name__ == "__main__":
    print(__doc__)
