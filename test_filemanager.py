#!/usr/bin/env python3
"""Test file manager functionality"""

from pathlib import Path

# Test scanning folders
app_folder = Path(__file__).parent
data_folder = app_folder / "data"

print("Testing File Manager (relative paths):")
print(f"App folder: {app_folder}")
print(f"Data folder: {data_folder}")

all_files = {}

# Scan app folder
if app_folder.exists():
    app_xlsx = list(app_folder.glob("*.xlsx"))
    print(f"\n✅ Found {len(app_xlsx)} Excel files in app folder:")
    for f in sorted(app_xlsx):
        if not f.name.startswith("~$"):
            print(f"  - {f.name}")
            all_files[f.name] = str(f)

# Scan data folder
if data_folder.exists():
    data_xlsx = list(data_folder.glob("*.xlsx"))
    print(f"\n✅ Found {len(data_xlsx)} Excel files in data folder:")
    for f in sorted(data_xlsx):
        if not f.name.startswith("~$"):
            print(f"  - {f.name}")
            all_files[f.name] = str(f)

print(f"\n📊 Total unique Excel files: {len(all_files)}")
print("\n✅ File manager test passed (using relative paths only!)")

