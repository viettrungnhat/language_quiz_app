# ✅ Voice Quiz User Name Implementation - COMPLETE

## Summary of Changes

This implementation ensures that **user names are captured BEFORE Voice Quiz starts**, eliminating issues with default names being used for realtime saves.

---

## Implementation Details

### 1. New Method: `_ask_user_name_before_quiz()`

**Location**: [gui_main_v2_new.py](gui_main_v2_new.py#L2833) (lines 2833-2901)

**Purpose**: Display a dialog asking user for their name BEFORE quiz starts

**Key Features**:
- ✅ Shows custom dialog with user name input field
- ✅ Pre-fills with default name from `user_name_entry` if available
- ✅ Sets `self.current_quiz_user` instance variable
- ✅ Returns user name if OK clicked, None if Cancel clicked
- ✅ Prints debug info for verification

**Code Flow**:
```python
def _ask_user_name_before_quiz(self):
    # Dialog asks: "👤 Tên của bạn:"
    # User enters name or accepts default
    # On OK: Sets self.current_quiz_user = user_name
    # Returns: user_name (str) or None
```

### 2. Updated: `start_voice_quiz()` Method

**Location**: [gui_main_v2_new.py](gui_main_v2_new.py#L2903) (lines 2903-2938)

**Changes**:
- ✅ Calls `_ask_user_name_before_quiz()` immediately after validation
- ✅ Returns early if user clicks "Hủy" (Cancel)
- ✅ Stores user name in `self.current_quiz_user`

**Code Flow**:
```python
def start_voice_quiz(self):
    # Check if quiz already running
    # Check if file selected
    
    # NEW: Ask for user name BEFORE quiz starts
    user_name = self._ask_user_name_before_quiz()
    if not user_name:
        return  # User cancelled
    
    # Continue with normal quiz initialization
    self.voice_quiz_running = True
    # ...
```

### 3. Realtime Save Points (Unchanged, now work correctly)

**Location 1**: [gui_main_v2_new.py](gui_main_v2_new.py#L3588) (lines 3588-3616)
- When user doesn't answer in time

**Location 2**: [gui_main_v2_new.py](gui_main_v2_new.py#L3660) (lines 3660-3688)
- When user answers correctly or incorrectly

**How it Works**:
```python
# Gets user name from instance variable
user_name = getattr(self, 'current_quiz_user', 'Unknown')

# Saves with correct user name
self.smart_review_db.save_question_result(
    file_path=normalized_file_path,
    question_id=question_num,
    question_text=question_text,
    correct_answer=correct_answer,
    user_name=user_name,  # ← Now has correct name from dialog!
    quiz_type=self.quiz_type_str,
    test_mode=self.test_mode,
    is_correct=is_correct,
    user_answer=user_answer,
    score=score
)
```

### 4. End-of-Quiz Name Change (Optional Update)

**Location**: [gui_main_v2_new.py](gui_main_v2_new.py#L4566) (lines 4550-4580)

**Purpose**: If user changes name at end of quiz, update all previous realtime saves

**Code Flow**:
```python
# Gets name from final dialog
new_user_name = user_name[0]

# Gets name that was used during quiz
old_user_name = getattr(self, 'current_quiz_user', 'Unknown')

# If different, update database
if old_user_name != new_user_name and self.smart_review_db:
    self.smart_review_db.update_user_name(
        file_path=normalized_file_path,
        old_user_name=old_user_name,
        new_user_name=new_user_name,
        quiz_type_filter='voice_quiz'
    )
```

---

## Database Functions (Already Implemented)

### 1. `get_weak_questions()`
- **Location**: [smart_review_db.py](smart_review_db.py#L154)
- **Filter**: By file_path + quiz_type + test_mode (NOT by user_name)
- **Result**: Weak questions shared across all users

### 2. `get_completed_question_ids()`
- **Location**: [smart_review_db.py](smart_review_db.py#L200)
- **Filter**: By file_path + quiz_type + test_mode (NOT by user_name)
- **Result**: Question IDs already attempted by any user

### 3. `update_user_name()`
- **Location**: [smart_review_db.py](smart_review_db.py#L211)
- **Purpose**: Update all records from old_user_name to new_user_name
- **Filter**: By file_path + quiz_type
- **When Used**: If user changes name at end of quiz

---

## Complete User Flow (CORRECTED)

### Before Starting Quiz:
1. User clicks "Voice Quiz" button
2. System checks file is selected ✅
3. **NEW**: System shows dialog "👤 Tên của bạn:" ← THIS IS NEW
4. User enters name (e.g., "BỐ test") or accepts default
5. User clicks "Bắt Đầu" button
6. System stores name in `self.current_quiz_user` ✅

### During Quiz:
7. Quiz loads questions
8. User answers each question
9. **Realtime save** uses `self.current_quiz_user` for user_name ✅ (WAS BROKEN, NOW FIXED)
10. Results display after each answer
11. Quiz continues to next question

### After Quiz:
12. System shows results summary
13. **Optional**: Shows dialog "👤 Nhập tên của bạn:" (can change name)
14. If name changed: `update_user_name()` updates database ✅
15. Results saved to JSON and Discord
16. Smart Review DB updated with final name ✅

---

## Issues Fixed

### ❌ OLD PROBLEM
- Realtime saves used "Default" or "Unknown" because `user_name_entry` didn't exist
- End-of-quiz update would find 0 records because saved name didn't match

### ✅ NEW SOLUTION
- Dialog appears BEFORE quiz starts
- User name captured directly and stored in `self.current_quiz_user`
- Realtime saves use correct user name
- End-of-quiz update only needed if user intentionally changes name

---

## Testing Notes

To verify this works:

1. **Start Voice Quiz**
   - Dialog should appear asking for name
   - Pre-filled with name from settings if available

2. **Enter a name** (e.g., "Test123")
   - Click "Bắt Đầu"
   - Quiz should start normally

3. **Complete a few questions**
   - Console should show: "👤 Bắt đầu Voice Quiz với tên: Test123"
   - Realtime saves should use "Test123"

4. **View results**
   - All saved questions should have user_name="Test123"

5. **Check database** (optional)
   - Query: `SELECT user_name, COUNT(*) FROM question_history WHERE user_name='Test123' GROUP BY user_name`
   - Should show all quiz results saved with correct name

---

## Code Quality Checks

✅ No syntax errors in gui_main_v2_new.py
✅ No syntax errors in smart_review_db.py
✅ All methods follow existing code patterns
✅ Error handling with try/except blocks
✅ Debug print statements for troubleshooting
✅ Comments in Vietnamese for consistency

---

## Files Modified

1. **gui_main_v2_new.py**
   - Added `_ask_user_name_before_quiz()` method (new)
   - Updated `start_voice_quiz()` method (modified)
   - No changes needed to realtime saves (already use `getattr(self, 'current_quiz_user', 'Unknown')`)

2. **smart_review_db.py**
   - No changes needed
   - Database functions already support this flow

---

## Implementation Status

✅ **COMPLETE** - All changes implemented and syntax verified

Next steps:
1. Test with actual Voice Quiz
2. Verify user names are saved correctly
3. Test name change at end of quiz
4. Test "Ôn từ yếu" with proper user name tracking
