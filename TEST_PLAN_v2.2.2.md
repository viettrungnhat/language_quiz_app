# 🧪 Language Quiz v2.2.2 - Test Plan

**Document Version**: 1.0  
**Test Date Range**: [Your Test Date]  
**Tester Name**: [Your Name]  
**Application Version**: v2.2.2

---

## 📋 Test Scope

### **Critical Bug Fixes to Verify**
1. ✅ WinError 32 (File Lock) - Should NOT occur
2. ✅ Errno 13 (Permission Denied) - Should NOT occur  
3. ✅ RuntimeError (Threading) - Should NOT occur

### **New Features to Verify**
4. ✅ Test Mode Selection UI - Should display and be functional
5. ✅ Mode 1 Voice Flow - Should read VN + EN
6. ✅ Mode 2 Voice Flow - Should read EN only
7. ✅ STT Language Switching - Should adapt by mode

---

## 🎯 Test Cases

### **TEST 1: Verify File Lock Fix (WinError 32)**

**Objective**: Ensure TTS files don't conflict across multiple questions

**Steps**:
```
1. Launch application
2. Select English Excel file
3. Select "🎤 VOICE QUIZ"
4. Mode 1 (default)
5. Select 5 questions
6. Complete all 5 questions successfully
   - Listen to each question (should play without error)
   - Speak clear answers
7. Check console for WinError 32
```

**Expected Result**:
- ✅ All 5 questions play without file lock errors
- ✅ Console shows NO "WinError 32"
- ✅ Console shows NO "The process cannot access the file"
- ✅ Audio plays smoothly for each question

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 2: Verify Permission Denied Fix (Errno 13)**

**Objective**: Ensure temp files are deleted correctly

**Steps**:
```
1. Launch application
2. Select Chinese Excel file
3. Select "🎤 VOICE QUIZ"
4. Mode 1 (default)
5. Select 10 questions
6. Complete all 10 questions
   - Let each question play completely
   - Pause 1-2 seconds between answers
7. Check console for Errno 13
```

**Expected Result**:
- ✅ All 10 questions complete without permission errors
- ✅ Console shows NO "Errno 13"
- ✅ Console shows NO "Permission denied"
- ✅ No temp files remain in system temp folder

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 3: Verify Threading Fix (RuntimeError)**

**Objective**: Ensure voice quiz doesn't crash due to threading issues

**Steps**:
```
1. Launch application
2. Select any Excel file
3. Select "🎤 VOICE QUIZ"
4. Rapidly click "VOICE QUIZ" button multiple times
5. Allow 3 complete questions to run
   - Each question: read + listen + feedback
6. Check console for RuntimeError
```

**Expected Result**:
- ✅ Application never crashes
- ✅ Console shows NO "RuntimeError: main thread is not in main loop"
- ✅ All voice interactions complete smoothly
- ✅ Feedback displays correctly

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 4: Verify Mode Selection UI**

**Objective**: Ensure Mode 1/Mode 2 radio buttons are visible and functional

**Steps**:
```
1. Launch application
2. Go to Setup Tab
3. Scroll down in Setup Tab
4. Look for "Chế độ Voice Quiz:" label
5. Verify 2 radio button options:
   ├─ Mode 1️⃣: Chatbot đọc Tiếng Việt...
   └─ Mode 2️⃣: Chatbot đọc Anh/Trung/Nhật...
6. Click Mode 1 (default should be selected)
7. Check console output
8. Click Mode 2
9. Check console output again
```

**Expected Result**:
- ✅ "Chế độ Voice Quiz:" label visible
- ✅ 2 radio buttons clearly visible
- ✅ Mode 1 selected by default
- ✅ Console shows "✨ Chế độ Voice Quiz: Mode 1: VN→Anh/Trung/Nhật"
- ✅ Can click Mode 2
- ✅ Console shows "✨ Chế độ Voice Quiz: Mode 2: Anh/Trung/Nhật→VN"

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 5: Mode 1 Voice Flow - Read Vietnamese → Answer Foreign**

**Objective**: Verify Mode 1 question reading pattern

**Steps**:
```
1. Launch application
2. Select English Excel file
3. Go to Setup Tab
4. Select Mode 1 (default)
5. Select "🎤 VOICE QUIZ"
6. Listen carefully to audio output (expected order):
   - Tiếng Việt (lần 1) - Vietnamese first reading
   - English (lần 2) - English second reading  
   - Tiếng Việt (lần 3) - Vietnamese third reading
7. Wait for "3..." countdown
8. Speak answer in English
9. Check console for reading pattern
```

**Expected Result**:
- ✅ Console shows "[Mode 1] Đọc câu hỏi (Tiếng Việt - lần 1)..."
- ✅ Console shows "[Mode 1] Đọc câu hỏi (English - AWS Polly - lần 2)..."
- ✅ Console shows "[Mode 1] Đọc câu hỏi (Tiếng Việt - lần 3)..."
- ✅ STT Language: en-US (from console)
- ✅ Audio plays in correct order
- ✅ User can speak answer when countdown reaches "1..."

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 6: Mode 2 Voice Flow - Read Foreign → Answer Vietnamese**

**Objective**: Verify Mode 2 question reading pattern

**Steps**:
```
1. Launch application
2. Select English Excel file
3. Go to Setup Tab
4. Select Mode 2
5. Select "🎤 VOICE QUIZ"
6. Listen carefully to audio output (expected order):
   - English (lần 1) - English first reading
   - English (lần 2) - English second reading
   - NO Vietnamese reading
7. Wait for "3..." countdown
8. Speak answer in Vietnamese
9. Check console for reading pattern
```

**Expected Result**:
- ✅ Console shows "[Mode 2] Đọc câu hỏi (English - AWS Polly - lần 1)..."
- ✅ Console shows "[Mode 2] Đọc câu hỏi (English - AWS Polly - lần 2)..."
- ✅ NO console output for Vietnamese reading
- ✅ STT Language: vi-VN (from console)
- ✅ Audio plays only in English (2 times)
- ✅ User can speak answer in Vietnamese when countdown reaches "1..."

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 7: STT Language Switching - Mode 1**

**Objective**: Verify STT listens in correct language for Mode 1

**Steps**:
```
1. Launch application
2. Select English Excel file (Quiz Language = English)
3. Go to Setup Tab → Select Mode 1
4. Start Voice Quiz
5. Speak ENGLISH answer (e.g., "beautiful")
6. Check if recognized ✓
7. Repeat with Chinese file (Quiz Language = Chinese)
8. Speak CHINESE answer (e.g., "美丽")
9. Check if recognized ✓
```

**Expected Result**:
- ✅ English file + Mode 1: STT uses en-US (recognized English answers)
- ✅ Console shows "🎤 STT Language: en-US"
- ✅ Chinese file + Mode 1: STT uses zh-CN (recognized Chinese answers)
- ✅ Console shows "🎤 STT Language: zh-CN"
- ✅ Answers correctly identified in respective languages

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 8: STT Language Switching - Mode 2**

**Objective**: Verify STT always uses Vietnamese for Mode 2

**Steps**:
```
1. Launch application
2. Select English Excel file (Quiz Language = English)
3. Go to Setup Tab → Select Mode 2
4. Start Voice Quiz
5. Speak VIETNAMESE answer (e.g., "đẹp")
6. Check if recognized ✓
7. Repeat with Chinese file (Quiz Language = Chinese)
8. Go to Setup Tab → Select Mode 2 (confirm selection)
9. Start Voice Quiz
10. Speak VIETNAMESE answer
11. Check if recognized ✓
```

**Expected Result**:
- ✅ English file + Mode 2: STT uses vi-VN (recognized Vietnamese answers)
- ✅ Console shows "🎤 STT Language: vi-VN"
- ✅ Chinese file + Mode 2: STT uses vi-VN (NOT zh-CN!)
- ✅ Console shows "🎤 STT Language: vi-VN"
- ✅ Answers correctly identified as Vietnamese regardless of quiz language

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 9: Long Session Stability (10+ questions)**

**Objective**: Verify application stays stable over extended use

**Steps**:
```
1. Launch application
2. Select any Excel file
3. Mode 1
4. Select 15 questions
5. Complete all 15 questions without stopping
   - Listen to each question
   - Provide clear answer
   - Read feedback
6. Check console for any errors
7. Check for memory leaks (task manager)
```

**Expected Result**:
- ✅ All 15 questions complete without crashes
- ✅ No error messages in console
- ✅ No file lock or permission errors
- ✅ No RuntimeError messages
- ✅ Memory usage stable (no continuous increase)
- ✅ Feedback displays correctly for all questions

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

### **TEST 10: Mode Switching Mid-Session**

**Objective**: Verify mode can be changed between quizzes

**Steps**:
```
1. Launch application
2. Select English file
3. Mode 1 → Run 3 questions
4. Return to Setup Tab
5. Switch to Mode 2
6. Same English file → Run 3 questions with Mode 2
7. Compare console outputs
```

**Expected Result**:
- ✅ First session shows Mode 1 reading pattern
- ✅ Second session shows Mode 2 reading pattern
- ✅ Console shows correct mode for each session
- ✅ STT language changes appropriately
- ✅ No conflicts or errors when switching modes

**Pass Criteria**: ✅ All conditions met

**Actual Result**: [Tester fills in]

---

## 📊 Test Summary

### **Critical Bugs**

| Bug | Test ID | Status | Notes |
|-----|---------|--------|-------|
| WinError 32 | TEST 1 | [ ] Pass / [ ] Fail | [Tester fills] |
| Errno 13 | TEST 2 | [ ] Pass / [ ] Fail | [Tester fills] |
| RuntimeError | TEST 3 | [ ] Pass / [ ] Fail | [Tester fills] |

### **New Features**

| Feature | Test ID | Status | Notes |
|---------|---------|--------|-------|
| Mode UI | TEST 4 | [ ] Pass / [ ] Fail | [Tester fills] |
| Mode 1 Flow | TEST 5 | [ ] Pass / [ ] Fail | [Tester fills] |
| Mode 2 Flow | TEST 6 | [ ] Pass / [ ] Fail | [Tester fills] |
| STT Mode 1 | TEST 7 | [ ] Pass / [ ] Fail | [Tester fills] |
| STT Mode 2 | TEST 8 | [ ] Pass / [ ] Fail | [Tester fills] |

### **Stability**

| Test | Test ID | Status | Notes |
|------|---------|--------|-------|
| Long Session | TEST 9 | [ ] Pass / [ ] Fail | [Tester fills] |
| Mode Switching | TEST 10 | [ ] Pass / [ ] Fail | [Tester fills] |

---

## ✅ Overall Result

**Total Tests**: 10  
**Passed**: ____ / 10  
**Failed**: ____ / 10  
**Skipped**: ____ / 10  

**Overall Status**:
- [ ] ✅ PASS - Ready for production
- [ ] ⚠️ CONDITIONAL - Minor issues, can proceed
- [ ] ❌ FAIL - Critical issues, do not release

---

## 🔍 Issues Found During Testing

### **Issue #1**
**Title**: [Description]  
**Severity**: [ ] Critical / [ ] High / [ ] Medium / [ ] Low  
**Steps to Reproduce**: [Your steps]  
**Expected**: [What should happen]  
**Actual**: [What actually happened]  
**Console Output**: [Relevant console messages]

### **Issue #2**
[Repeat as needed]

---

## 📝 Tester Notes

[Any additional observations or comments about the release]

---

## 🎯 Sign-Off

**Tester Name**: ______________________  
**Date**: ______________________  
**Signature**: ______________________  

**Reviewer Name**: ______________________  
**Date**: ______________________  
**Signature**: ______________________

---

**For questions about this test plan, contact the Language Quiz development team.**
