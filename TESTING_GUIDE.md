# 🧪 Testing Guide - Voice Quiz Bug Fixes

## Overview

Three critical issues were identified and fixed:
1. **KeyError 'user_answer'** - Results display crashing
2. **AttributeError 'sqlite3.Row'** - Weak questions failing to load
3. **User Name Dialog** - May not be displaying properly (debugging in progress)

---

## Test Plan

### Test 1: Voice Quiz with Weak Questions (Most Important)

**Objective**: Verify all three fixes work together

**Steps**:
1. **Start Application**
   ```
   cd d:\Da Ngon Ngu\language_quiz_app
   python gui_main_v2_new.py
   ```

2. **Wait for App to Load**
   - Should see: `✅ Smart Review Database initialized!`
   - Should see: `✅ Đã load session trước...`

3. **Select File & Sheet**
   - File: H3EngP1_converted.xlsx (or your test file)
   - Sheet: English (or your test sheet)

4. **Start Voice Quiz**
   - Click "VOICE QUIZ" button
   - **EXPECTED**: Dialog appears asking "👤 Tên của bạn:"
   - **CHECK**: Look at console for `🔵 DEBUG: _ask_user_name_before_quiz() called`

5. **If Dialog Doesn't Appear**
   - Check console output:
     - Should see: `🔵 DEBUG: _ask_user_name_before_quiz() called`
     - Should see: `🔵 DEBUG: Dialog created at (X, Y), waiting for input...`
     - Dialog window should be centered on screen

6. **Enter Name**
   - Type your name: "TestUser" (or press Enter to use "Default")
   - Click "Bắt Đầu" button
   - **EXPECTED**: Console shows `👤 Bắt đầu Voice Quiz với tên: TestUser`

7. **Complete Quiz**
   - Answer 3-5 questions
   - Record your answers (you'll need them later)

8. **View Results**
   - After quiz completes, results dialog appears
   - **EXPECTED**: Should NOT crash with KeyError
   - **EXPECTED**: Shows all your answers with user name
   - Should show lines like:
     ```
     1. (Lần 1)
        ❓ Câu hỏi: ...
        🎤 Bạn trả lời: ...
        ✨ Đáp án đúng: ...
        📊 Điểm: X/10
     ```

### Test 2: "Ôn từ Yếu" (Review Weak) - Practice Mode

**Objective**: Verify weak questions load without AttributeError

**Prerequisites**: Complete at least one Voice Quiz first

**Steps**:
1. **Go to Practice Tab**
   - Click "Practice (ABC)" tab

2. **Select Same File & Sheet**
   - File: H3EngP1_converted.xlsx
   - Sheet: English

3. **Click Mode 2 (if used in Voice Quiz)**
   - Select "Mode 2: Bot EN/CJK → User nói VN"

4. **Check "Ôn từ yếu" (Practice Weak)**
   - Click "Ôn từ yếu" checkbox
   - **EXPECTED**: Should load without error
   - **EXPECTED**: Dialog shows weak questions count
   - **ERROR CHECK**: If error appears, check console for details

5. **If Error Appears**
   - Console should show: `❌ Lỗi khi tải từ yếu: ...`
   - Our fix should have prevented this
   - If still getting error, it's a different issue

---

## Console Output to Monitor

### Successful Flow ✅

```
🔵 DEBUG: _ask_user_name_before_quiz() called
🔵 DEBUG: Dialog created at (X, Y), waiting for input...
🔵 DEBUG: Dialog closed, result[0] = TestUser
👤 Bắt đầu Voice Quiz với tên: TestUser

[Quiz proceeds normally...]

✅ Kết thúc quiz!
🔍 DEBUG Voice Quiz: user_name = TestUser
📊 Điểm trung bình: 75.0%

[Results display without crashing]
```

### Issues to Catch ❌

**Dialog Not Showing**:
```
🔵 DEBUG: _ask_user_name_before_quiz() called
🔵 DEBUG: Dialog created at (X, Y), waiting for input...
[Long pause - dialog not responding]
👤 Bắt đầu Voice Quiz với tên: Default  ← Used default instead
```

**Weak Questions Error**:
```
❌ Lỗi khi tải từ yếu:
'sqlite3.Row' object has no attribute 'get'
```
→ Our fix should prevent this

**Results Display Error**:
```
Exception in Tkinter callback
KeyError: 'user_answer'
```
→ Our fix should prevent this

---

## Quick Verification Checklist

Run this quick test to verify all fixes:

```python
# Test in Python console (or create test_fixes.py)
from smart_review_db import SmartReviewDB
import sqlite3

db = SmartReviewDB()

# Test 1: Get weak questions (should not error with .get())
try:
    weak = db.get_weak_questions(
        file_path="d:/test/test.xlsx",
        quiz_type_filter="voice_quiz",
        test_mode=2
    )
    print("✅ get_weak_questions() works")
except Exception as e:
    print(f"❌ get_weak_questions() failed: {e}")

# Test 2: Verify Row objects work
try:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INT, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'test')")
    row = cursor.fetchone()
    
    # This should work (dict-like access)
    val = row['name']
    print(f"✅ row['name'] works: {val}")
    
    # This should NOT work (no .get() method)
    try:
        val = row.get('name', 'default')
        print(f"❌ row.get() unexpectedly worked: {val}")
    except AttributeError:
        print(f"✅ row.get() correctly not supported (using bracket access instead)")
    
except Exception as e:
    print(f"❌ Row test failed: {e}")
```

---

## Expected Results After Fixes

| Test | Before Fix ❌ | After Fix ✅ |
|------|---------------|------------|
| Display results with missing field | KeyError crash | Shows default value |
| Load weak questions from DB | AttributeError crash | Loads successfully |
| User name dialog | Unknown behavior | Dialog shows, can debug with prints |

---

## Troubleshooting

### Problem: Dialog never appears

**Diagnosis**:
1. Check console for `🔵 DEBUG: _ask_user_name_before_quiz() called`
   - If NOT shown: Method not being called (check start_voice_quiz code)
   - If shown: Dialog is created but maybe not visible

2. Try moving/resizing main window
   - Dialog might be off-screen or behind main window
   - Our fix added better positioning

3. Check for exceptions in console
   - May have unhandled exception preventing dialog

**Solution**:
- Run with console visible to see debug messages
- Check if tkinter is working properly
- Try running test first (Test 1) before moving to Practice mode

### Problem: Results still show "KeyError"

**Diagnosis**:
1. Check that our fix was applied
2. Look for line 4733 in gui_main_v2_new.py:
   ```python
   report += f"   🎤 Bạn trả lời: {result.get('user_answer', '(Không có câu trả lời)')}\n"
   ```

**Solution**:
- Restart app (make sure changes are loaded)
- Clear any .pyc cache files

### Problem: Weak questions still error

**Diagnosis**:
1. Check smart_review_db.py line 198
   - Should be: `'test_mode': row['test_mode'],`
   - NOT: `'test_mode': row.get('test_mode'),`

2. May be hitting a different error

**Solution**:
- Verify the exact error message
- Check if it's the same Row.get() error or different

---

## Success Criteria

✅ **All tests pass when**:
1. Dialog appears asking for user name
2. Voice Quiz completes without crashes
3. Results display without KeyError
4. "Ôn từ yếu" loads without AttributeError
5. Console shows proper debug messages

---

## Next Steps If Issues Persist

If you encounter issues:

1. **Collect Console Output**: Copy entire console output when error occurs
2. **Note Exact Error**: Include full error message and line number
3. **Describe Steps**: What exactly were you doing when error occurred
4. **Screenshot**: If dialog doesn't appear, screenshot the app window

With this info, we can debug further.

---

## Status

✅ **Fixes Applied**: All code changes implemented
⏳ **Testing**: Ready for user testing
🔍 **Debugging**: Debug statements added for diagnosis
