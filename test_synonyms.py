#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test semantic matching with synonym support (Cách 1+2)
"""

from scorer import Scorer

def test_synonym_matching():
    scorer = Scorer()
    
    print("=== TEST SYNONYM + NLP SEMANTIC MATCHING ===\n")
    
    test_cases = [
        # (user_answer, correct_answer, quiz_type, description)
        
        # === SYNONYM TESTS ===
        ("bright", "white", "meaning", "Synonym: bright=white"),
        ("huge", "big", "meaning", "Synonym: huge=big"),
        ("excellent", "good", "meaning", "Synonym: excellent=good"),
        
        # === WORD SIMILARITY TESTS ===
        ("happyy", "happy", "meaning", "Typo: 1 extra char"),
        ("wite", "white", "meaning", "Typo: missing char"),
        
        # === EXISTING TESTS (should still work) ===
        ("white", "white", "meaning", "Exact match"),
        ("it is white", "is it white", "meaning", "Word reorder"),
        ("black", "white", "meaning", "No match (different words)"),
        
        # === VIETNAMESE SYNONYMS ===
        ("sáng", "trắng", "meaning", "Vietnamese synonym: sáng≈trắng"),
        ("to", "lớn", "meaning", "Vietnamese synonym: to=lớn"),
    ]
    
    results = []
    
    for user, correct, quiz_type, desc in test_cases:
        score, feedback, is_semantic = scorer.calculate_score(user, correct, 1, quiz_type)
        is_correct = score >= 5
        
        results.append({
            "user": user,
            "correct": correct,
            "score": score,
            "is_semantic": is_semantic,
            "is_correct": is_correct,
            "desc": desc,
        })
    
    # Display results
    passed = 0
    failed = 0
    
    for r in results:
        status = "PASS" if r["is_correct"] else "FAIL"
        semantic_note = " [SEMANTIC]" if r["is_semantic"] else ""
        
        print(f"{status}: {r['desc']}")
        print(f"  '{r['user']}' vs '{r['correct']}'")
        print(f"  Score: {r['score']}/10{semantic_note}\n")
        
        if r["is_correct"]:
            passed += 1
        else:
            failed += 1
    
    print(f"=== RESULTS: {passed} passed, {failed} failed ===")
    return failed == 0

if __name__ == "__main__":
    success = test_synonym_matching()
    exit(0 if success else 1)
