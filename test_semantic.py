#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test semantic matching functionality
"""

from scorer import Scorer

def test_semantic_matching():
    scorer = Scorer()
    
    test_cases = [
        # (user_answer, correct_answer, quiz_type, expected_score_>=_5, expected_semantic)
        # Exact matches (semantic = False)
        ("white", "white", "meaning", True, False),
        ("nó màu trắng", "nó màu trắng", "meaning", True, False),
        
        # Word-based high match (now marks as semantic due to synonym/similarity check)
        ("nó màu trắng phải không", "nó màu trắng không", "example", True, True),  # Semantic match now
        ("is it white", "it is white", "meaning", True, True),  # Semantic match now
        
        # Fuzzy char match (semantic = False)
        ("nó trắng hả", "nó trắng phải không", "example", True, False),  # 69% char similarity
        
        # NEW: Synonym/semantic matches
        ("sáng", "trắng", "meaning", True, True),  # Vietnamese synonyms - NOW WORKS!
        
        # Wrong answers (should always fail)
        ("black", "white", "meaning", False, False),
        ("đen", "trắng", "meaning", False, False),
    ]
    
    print("🧪 Testing Semantic Matching...\n")
    passed = 0
    failed = 0
    
    for user, correct, quiz_type, expected_correct, expected_semantic in test_cases:
        score, feedback, is_semantic = scorer.calculate_score(user, correct, attempt=1, quiz_type=quiz_type)
        is_correct = score >= 5
        
        # Check if result matches expectation
        match_correct = is_correct == expected_correct
        match_semantic = is_semantic == expected_semantic if is_correct else True
        
        status = "✅" if (match_correct and match_semantic) else "❌"
        passed += 1 if (match_correct and match_semantic) else 0
        failed += 0 if (match_correct and match_semantic) else 1
        
        print(f"{status} '{user}' vs '{correct}'")
        print(f"   Quiz Type: {quiz_type}")
        print(f"   Score: {score}/10, Feedback: {feedback}")
        print(f"   Is Correct: {is_correct} (expected {expected_correct})")
        print(f"   Is Semantic: {is_semantic} (expected {expected_semantic})")
        print()
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = test_semantic_matching()
    exit(0 if success else 1)
