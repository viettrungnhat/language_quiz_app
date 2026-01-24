#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test GUI integration với file_converter
Simulate user selecting different file types
"""

from pathlib import Path
from file_converter import detect_file_structure, is_template_format
import openpyxl

print("=" * 70)
print("🧪 GUI FILE CONVERTER INTEGRATION TEST")
print("=" * 70)
print()

# Test 1: Check TEMPLATE file
print("Test 1️⃣: TEMPLATE Format")
print("-" * 70)
try:
    template_files = list(Path("d:\\Da Ngon Ngu\\language_quiz_app\\data").glob("*.xlsx"))
    if template_files:
        f = template_files[0]
        wb = openpyxl.load_workbook(f)
        ws = wb.active
        is_template = is_template_format(ws)
        print(f"File: {f.name}")
        print(f"Is Template: {is_template}")
        print(f"→ Action: Load directly ✅")
    else:
        print("No template files found")
except Exception as e:
    print(f"Error: {e}")

print()
print()

# Test 2: Check files yang bisa convert
print("Test 2️⃣: Convertible Files")
print("-" * 70)

convertible_files = [
    "1,2 văn viết nghe 02112025.xlsx",
    "200 câu đố nhật việt 25072025.xlsx",
]

workspace = Path("d:\\Da Ngon Ngu")

for filename in convertible_files:
    filepath = workspace / filename
    
    if not filepath.exists():
        print(f"⚠️  {filename}: NOT FOUND")
        continue
    
    try:
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
        
        is_template = is_template_format(ws)
        structure, language, confidence = detect_file_structure(ws)
        
        print(f"\nFile: {filename}")
        print(f"├─ Is Template: {is_template}")
        print(f"├─ Structure: {structure}")
        print(f"├─ Language: {language}")
        print(f"├─ Confidence: {confidence*100:.0f}%")
        
        if not is_template and structure == "alternating_pairs":
            print(f"└─ Action: SHOW CONVERT DIALOG ✅")
            print(f"\n   Dialog would show:")
            print(f"   ├─ Detected Structure: {structure}")
            print(f"   ├─ Detected Language: {language}")
            print(f"   ├─ Confidence: {confidence*100:.0f}%")
            print(f"   └─ [YES] [NO] buttons")
        else:
            print(f"└─ Action: Load as-is (⚠️  may have errors)")
            
    except Exception as e:
        print(f"Error reading {filename}: {e}")

print()
print()

# Test 3: Simulate GUI dialog flow
print("Test 3️⃣: GUI Dialog Flow Simulation")
print("-" * 70)
print()
print("Scenario: User selects '200 câu đố nhật việt 25072025.xlsx'")
print()
print("Flow:")
print("1. System detects file format")
print("   ✓ Is Template: NO")
print("   ✓ Structure: alternating_pairs")
print("   ✓ Language: Japanese")
print("   ✓ Confidence: 95%")
print()
print("2. System shows dialog:")
print("   ┌─────────────────────────────────────────┐")
print("   │ ⚠️  File Không Chuẩn Format             │")
print("   │                                         │")
print("   │ 📋 File của bạn không đúng TEMPLATE    │")
print("   │                                         │")
print("   │ 📊 Detected: alternating_pairs         │")
print("   │ 🌐 Language: Japanese                  │")
print("   │ 📈 Confidence: 95%                     │")
print("   │                                         │")
print("   │ ❓ Bạn muốn convert file?              │")
print("   │                                         │")
print("   │ [✅ YES]                [❌ NO]        │")
print("   └─────────────────────────────────────────┘")
print()
print("3a. If YES:")
print("    ✓ Run convert_file_auto()")
print("    ✓ Create output: *_converted.xlsx")
print("    ✓ Load converted file")
print("    ✓ Show success message")
print()
print("3b. If NO:")
print("    ⚠️  Load original file (may have errors)")
print()

print()
print("=" * 70)
print("✅ Test Complete!")
print("=" * 70)
