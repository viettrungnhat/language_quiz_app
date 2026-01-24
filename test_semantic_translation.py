#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test semantic matching with real translation examples
"""

from scorer import Scorer

def test_semantic_translation():
    """Test semantic matching for translation scenarios"""
    scorer = Scorer()
    
    print("🧪 Semantic Translation Matching Tests...\n")
    
    test_cases = [
        # Vietnamese sentence translations (quiz_type="example")
        {
            "user": "nó có phải màu trắng không",
            "correct": "nó màu trắng phải không",
            "type": "example",
            "description": "Vietnamese paraphrase: same meaning, different word order",
        },
        {
            "user": "cái này trắng bạn nhé",
            "correct": "nó màu trắng",
            "type": "example",
            "description": "Vietnamese paraphrase: similar but with extra words",
        },
        {
            "user": "nó trắng à",
            "correct": "nó trắng phải không",
            "type": "example",
            "description": "Vietnamese: simplified version, same meaning",
        },
        # English-Vietnamese translations (quiz_type="example")
        {
            "user": "nó trắng phải không",
            "correct": "is it white",
            "type": "example",
            "description": "VN→EN: user answers in VN when expected EN (wrong language)",
        },
        {
            "user": "its white",  # Slightly wrong grammar but semantic match
            "correct": "it is white",
            "type": "example",
            "description": "EN: common grammar mistake but semantically correct",
        },
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        user = test["user"]
        correct = test["correct"]
        quiz_type = test["type"]
        
        score, feedback, is_semantic = scorer.calculate_score(
            user, correct, attempt=1, quiz_type=quiz_type
        )
        is_correct = score >= 5
        
        result = {
            "num": i,
            "user": user,
            "correct": correct,
            "score": score,
            "feedback": feedback,
            "is_semantic": is_semantic,
            "is_correct": is_correct,
            "description": test["description"],
        }
        results.append(result)
    
    # Display results
    for r in results:
        print(f"Test {r['num']}: {r['description']}")
        print(f"  User answer: '{r['user']}'")
        print(f"  Correct:     '{r['correct']}'")
        print(f"  Result:      {'✅ CORRECT' if r['is_correct'] else '❌ WRONG'}")
        print(f"  Score:       {r['score']}/10")
        print(f"  Semantic:    {'Yes (✓ Đúng về mặt ý nghĩa)' if r['is_semantic'] else 'No (regular match)'}")
        print(f"  Feedback:    {r['feedback']}")
        print()
    
    # Summary
    correct_count = sum(1 for r in results if r['is_correct'])
    semantic_count = sum(1 for r in results if r['is_semantic'] and r['is_correct'])
    
    print(f"📊 Summary:")
    print(f"   Total tests: {len(results)}")
    print(f"   Correct: {correct_count}/{len(results)}")
    print(f"   Semantic matches: {semantic_count}/{correct_count if correct_count > 0 else 0}")

if __name__ == "__main__":
    test_semantic_translation()
