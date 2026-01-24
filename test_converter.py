#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file_converter với file thực
"""

from file_converter import convert_file_auto, is_template_format, detect_file_structure
from pathlib import Path
import openpyxl

# List some Excel files in workspace
workspace_path = Path("d:\\Da Ngon Ngu")
excel_files = list(workspace_path.glob("*.xlsx"))[:5]

print("🔍 Scanning Excel files...\n")

for excel_file in excel_files:
    print(f"📄 File: {excel_file.name}")
    
    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb.active
        
        # Check format
        is_template = is_template_format(ws)
        structure, language, confidence = detect_file_structure(ws)
        
        print(f"   Is Template: {is_template}")
        print(f"   Structure: {structure}")
        print(f"   Language: {language}")
        print(f"   Confidence: {confidence*100:.1f}%")
        
        if not is_template and structure == "alternating_pairs":
            print(f"   ✅ Can convert!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
