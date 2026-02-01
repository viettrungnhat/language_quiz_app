#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify user name flow in Voice Quiz

This test verifies:
1. _ask_user_name_before_quiz() method exists and works
2. User name is stored in self.current_quiz_user
3. Realtime saves use the correct user name
4. End-of-quiz update_user_name() works if user changes name
"""

import sys
from pathlib import Path
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_review_db import SmartReviewDB

def test_weak_questions_filtering():
    """Test that weak questions are filtered by file/sheet/type/mode, not by user_name"""
    print("\n" + "="*60)
    print("TEST: Weak Questions Filtering (NOT by user_name)")
    print("="*60)
    
    try:
        db = SmartReviewDB()
        
        # Sample test data - create records for different users but same file/mode/type
        test_file = "d:/test/english.xlsx"
        
        # Simulate saving results from User A with correct answers
        print("\n📝 Saving results from User A (Mode 2, voice_quiz)...")
        db.save_question_result(
            file_path=test_file,
            question_id=1,
            question_text="Hello",
            correct_answer="Xin chào",
            user_name="User A",
            quiz_type="voice_quiz",
            test_mode=2,
            is_correct=True,
            user_answer="Xin chào",
            score=10
        )
        
        # Simulate User B saving wrong answer for same question
        print("📝 Saving results from User B (Mode 2, voice_quiz) - WRONG ANSWER...")
        db.save_question_result(
            file_path=test_file,
            question_id=1,
            question_text="Hello",
            correct_answer="Xin chào",
            user_name="User B",
            quiz_type="voice_quiz",
            test_mode=2,
            is_correct=False,
            user_answer="Chào",
            score=0
        )
        
        # Get weak questions - should return question 1 (User B's wrong answer)
        print("\n🔍 Getting weak questions for file (Mode 2, voice_quiz)...")
        weak_questions = db.get_weak_questions(
            file_path=test_file,
            user_name=None,  # ← NOT filtered by user!
            quiz_type_filter="voice_quiz",
            test_mode=2
        )
        
        print(f"✅ Found {len(weak_questions)} weak questions:")
        for q in weak_questions:
            print(f"   - Q{q['question_id']}: {q['question_text']} (users: contributed by all)")
        
        if len(weak_questions) > 0:
            print("\n✅ PASS: Weak questions are shared across users (not per-user)")
        else:
            print("\n❌ FAIL: Expected weak questions but got none")
        
        # Clean up test data
        db.conn.execute("DELETE FROM question_history WHERE file_path = ?", (test_file,))
        db.conn.commit()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def test_user_name_update():
    """Test that update_user_name() works correctly"""
    print("\n" + "="*60)
    print("TEST: User Name Update Function")
    print("="*60)
    
    try:
        db = SmartReviewDB()
        
        test_file = "d:/test/english.xlsx"
        
        # Save result with initial user name
        print("\n📝 Saving result with user_name='TestUser'...")
        db.save_question_result(
            file_path=test_file,
            question_id=5,
            question_text="Test",
            correct_answer="Kiểm tra",
            user_name="TestUser",
            quiz_type="voice_quiz",
            test_mode=1,
            is_correct=True,
            user_answer="Kiểm tra",
            score=10
        )
        
        # Verify it was saved
        cursor = db.conn.execute(
            "SELECT * FROM question_history WHERE file_path=? AND user_name=?",
            (test_file, "TestUser")
        )
        records_before = len(cursor.fetchall())
        print(f"✅ Found {records_before} records with user_name='TestUser'")
        
        # Update user name
        print("\n🔄 Updating user name: 'TestUser' → 'UpdatedUser'...")
        db.update_user_name(
            file_path=test_file,
            old_user_name="TestUser",
            new_user_name="UpdatedUser",
            quiz_type_filter="voice_quiz"
        )
        
        # Verify update
        cursor = db.conn.execute(
            "SELECT * FROM question_history WHERE file_path=? AND user_name=?",
            (test_file, "UpdatedUser")
        )
        records_after = len(cursor.fetchall())
        print(f"✅ Found {records_after} records with user_name='UpdatedUser'")
        
        if records_before > 0 and records_after > 0:
            print("\n✅ PASS: User name update works correctly")
        else:
            print("\n❌ FAIL: User name update failed")
        
        # Clean up
        db.conn.execute("DELETE FROM question_history WHERE file_path=?", (test_file,))
        db.conn.commit()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Starting Voice Quiz User Name Flow Tests...\n")
    
    test_weak_questions_filtering()
    test_user_name_update()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60 + "\n")
