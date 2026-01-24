"""
Hệ thống chấm điểm và đánh giá
"""

class Scorer:
    # Synonym dictionary for common words across languages
    SYNONYMS = {
        # English synonyms
        "en": {
            "white": ["bright", "pale", "light", "clear"],
            "black": ["dark", "dim"],
            "big": ["large", "great", "huge", "immense"],
            "small": ["tiny", "little", "minor"],
            "good": ["great", "excellent", "fine", "nice", "wonderful"],
            "bad": ["poor", "terrible", "awful", "horrible"],
            "happy": ["joyful", "cheerful", "glad", "delighted"],
            "sad": ["unhappy", "sorrowful", "gloomy"],
            "hot": ["warm", "burning", "scorching"],
            "cold": ["cool", "chilly", "frigid"],
            "fast": ["quick", "rapid", "swift"],
            "slow": ["sluggish", "leisurely"],
            "beautiful": ["pretty", "lovely", "attractive", "gorgeous"],
            "ugly": ["unattractive", "hideous"],
            "smart": ["intelligent", "clever", "bright"],
            "stupid": ["dumb", "foolish", "silly"],
        },
        # Vietnamese synonyms (normalized - without tone marks)
        "vi": {
            "trang": ["sang", "nhat", "su", "trang muot"],  # "trắng" normalized
            "đen": ["toi", "mu", "toi den"],  # "đen" normalized
            "lon": ["to", "khong long"],  # "lớn" normalized
            "nho": ["be", "ti", "ti tien"],  # "nhỏ" normalized
            "tot": ["hay", "xuat sac", "lanh", "tuyet voi"],  # "tốt" normalized
            "xau": ["te", "kinh khung"],  # "xấu" normalized
            "vui": ["hanh phuc", "vui tuoi", "phan khich"],  # "vui" normalized
            "buon": ["chan", "u sau", "the luong"],  # "buồn" normalized
            "nong": ["am", "soi", "ruc"],  # "nóng" normalized
            "lanh": ["mat", "gia ret", "mat tanh"],  # "lạnh" normalized
            "nhanh": ["toc do", "sieu nhanh"],  # "nhanh" normalized
            "cham": ["tu ton", "lau"],  # "chậm" normalized
            "dep": ["xinh", "duyen", "hap dan"],  # "đẹp" normalized
            "thong minh": ["sang suot", "thong tuyet"],  # "thông minh" normalized
            "ngu": ["ngoc", "dot", "ngu si"],  # "ngu" normalized
        },
        # Chinese synonyms (简体中文)
        "zh": {
            "白": ["亮", "淡", "清"],
            "黑": ["暗", "深"],
            "大": ["巨大", "宽大"],
            "小": ["迷你", "微小"],
            "好": ["极好", "优秀", "美好"],
            "坏": ["糟糕", "恐怖"],
            "快乐": ["开心", "高兴", "欢乐"],
            "悲伤": ["难过", "伤心"],
        },
        # Japanese synonyms
        "ja": {
            "白": ["明るい", "淡い", "クリア"],
            "黒": ["暗い", "深い"],
            "大きい": ["巨大な", "大きな"],
            "小さい": ["小さな", "ちっぽけな"],
            "良い": ["素晴らしい", "優秀な"],
            "悪い": ["ひどい", "悪劣な"],
        }
    }
    
    def __init__(self):
        self.total_points = 0
        self.questions_answered = 0
        self.results = []
    
    def calculate_score(self, user_answer, correct_answer, attempt=1, quiz_type="meaning"):
        """
        Tính điểm dựa trên câu trả lời
        attempt: lần thứ mấy trả lời (1-3)
        quiz_type: loại quiz ("meaning", "example", "vietnamese")
        
        Quy tắc:
        - Lần 1, chính xác: 10 điểm
        - Lần 1, gần đúng/ý nghĩa: 7-9 điểm
        - Lần 2, chính xác: 7 điểm
        - Lần 2, gần đúng/ý nghĩa: 5-6 điểm
        - Lần 3, bất kỳ: 3-4 điểm
        - Sai hoàn toàn: 0 điểm
        
        Note: Câu dài (example, vietnamese) được flexible hơn
        """
        import re
        import unicodedata
        
        # Normalize: loại bỏ dấu thanh tiếng Việt + dấu câu
        def normalize_text(text):
            # Loại bỏ dấu thanh Unicode
            nfd_text = unicodedata.normalize('NFD', text)
            text_clean = ''.join(c for c in nfd_text if unicodedata.category(c) != 'Mn')
            # Loại bỏ dấu câu - dùng regex explicit thay vì [^\w\s]
            text_clean = re.sub(r'[^\wàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]', '', text_clean)
            # Loại bỏ khoảng trắng dư thừa
            return re.sub(r'\s+', ' ', text_clean.strip().lower())
        
        user_normalized = normalize_text(user_answer)
        correct_normalized = normalize_text(correct_answer)
        
        # Debug output
        # print(f"User input: '{user_answer}' → '{user_normalized}'")
        # print(f"Correct: '{correct_answer}' → '{correct_normalized}'")
        # print(f"Match: {user_normalized == correct_normalized}")
        
        is_semantic = False  # Track if this is semantic match
        
        # Kiểm tra chính xác
        if user_normalized == correct_normalized:
            if attempt == 1:
                score = 10
                feedback = "✅ Hoàn hảo!"
            elif attempt == 2:
                score = 7
                feedback = "✅ Đúng!"
            else:
                score = 4
                feedback = "✅ Đúng (lần thứ 3)"
        # Kiểm tra gần đúng (chứa từ khóa chính hoặc ý nghĩa tương tự)
        else:
            similar_result = self._is_similar(user_normalized, correct_normalized, quiz_type, 
                                            original_user=user_answer, original_correct=correct_answer)
            if similar_result["match"]:
                is_semantic = similar_result.get("semantic", False)
                semantic_note = " (✓ Đúng về mặt ý nghĩa)" if is_semantic else ""
                
                if attempt == 1:
                    score = 8
                    feedback = f"✔️ Gần đúng{semantic_note}"
                elif attempt == 2:
                    score = 5
                    feedback = f"✔️ Gần đúng{semantic_note}"
                else:
                    score = 2
                    feedback = f"✔️ Gần đúng{semantic_note}"
            else:
                score = 0
                feedback = "❌ Sai rồi"
        
        return score, feedback, is_semantic
    
    def _check_synonym_match(self, word1, word2, language="en"):
        """
        Kiểm tra hai từ có phải synonym không
        Returns True nếu word1 là synonym của word2
        """
        lang_synonyms = self.SYNONYMS.get(language, {})
        
        # Normalize words for comparison
        w1 = word1.lower().strip()
        w2 = word2.lower().strip()
        
        # Exact match
        if w1 == w2:
            return True
        
        # Check if w1 is in w2's synonym list
        if w2 in lang_synonyms:
            if w1 in lang_synonyms[w2]:
                return True
        
        # Check if w2 is in w1's synonym list
        if w1 in lang_synonyms:
            if w2 in lang_synonyms[w1]:
                return True
        
        return False
    
    def _word_similarity(self, word1, word2):
        """
        Tính similarity giữa 2 từ (0.0 - 1.0)
        Dùng character-based similarity từ difflib
        """
        from difflib import SequenceMatcher
        
        if not word1 or not word2:
            return 0.0
        
        return SequenceMatcher(None, word1, word2).ratio()
    
    def _check_semantic_word_match(self, word1, word2, language="en", threshold=0.75):
        """
        Kiểm tra 2 từ có phải semantic match không
        Logic:
        1. Check exact synonym
        2. Check word similarity (>75%)
        3. Return True nếu một trong 2 match
        """
        # Check synonym first (fast path)
        if self._check_synonym_match(word1, word2, language):
            return True
        
        # Check word similarity (char-based)
        similarity = self._word_similarity(word1, word2)
        if similarity >= threshold:
            return True
        
        return False
    
    def _is_similar(self, answer1, answer2, quiz_type="meaning", original_user="", original_correct=""):
        """
        Kiểm tra hai câu trả lời có gần giống nhau không + semantic matching
        Input đã được normalize từ calculate_score(), không cần normalize lại
        Trả về dict: {"match": bool, "semantic": bool}
        
        Logic:
        1. Exact match: semantic=False
        2. Synonym match (NEW): semantic=True
        3. Word-based fuzzy: semantic=False
        4. Char-based fuzzy: semantic=False
        5. Char+keyword semantic: semantic=True
        """
        from difflib import SequenceMatcher
        
        # Phương pháp 1: Word-based (tốt cho tiếng Việt)
        words1 = set(answer1.split())
        words2 = set(answer2.split())
        
        if len(words2) > 0:
            common_words = len(words1 & words2)
            word_similarity = common_words / len(words2)  # % từ đúng có trong câu
        else:
            word_similarity = 0
        
        # Phương pháp 2: Character-based (Fuzzy matching - tốt cho CJK)
        char_similarity = SequenceMatcher(None, answer1, answer2).ratio()
        
        # Threshold điều chỉnh theo quiz type
        if quiz_type == "meaning":
            exact_fuzzy_threshold = 0.85
            word_exact_threshold = 0.95
            semantic_threshold = 0.65
        else:  # example, vietnamese
            exact_fuzzy_threshold = 0.70
            word_exact_threshold = 0.80
            semantic_threshold = 0.60
        
        keyword_threshold = 0.50
        
        # Extract keywords for all phases
        # Note: For vocabulary (meaning type), even short words can be keywords
        # For sentences, use 3+ char filter to avoid matching common words like "the", "a"
        if quiz_type == "meaning":
            correct_keywords = [w for w in words2 if len(w) >= 2]  # 2+ for vocab
            user_keywords = [w for w in words1 if len(w) >= 2]
        else:
            correct_keywords = [w for w in words2 if len(w) >= 3]  # 3+ for sentences
            user_keywords = [w for w in words1 if len(w) >= 3]
        
        # ========= PHASE 0: SYNONYM CHECK (NEW!) ==========
        # Check synonyms FIRST before fuzzy matching
        # This allows "bright" vs "white" to match even with 0% char similarity
        # Use original text for language detection (before normalization removed tone marks)
        lang = self._detect_language(original_correct if original_correct else answer2)
        
        # Special case: single word to single word
        if len(correct_keywords) <= 1 and len(user_keywords) <= 1:
            if correct_keywords and user_keywords:
                if self._check_semantic_word_match(user_keywords[0], correct_keywords[0], lang, threshold=0.75):
                    return {"match": True, "semantic": True}
        else:
            # Multi-word: check if any keywords are synonyms
            if correct_keywords and user_keywords:
                synonym_match_count = 0
                for correct_word in correct_keywords:
                    for user_word in user_keywords:
                        if self._check_synonym_match(user_word, correct_word, lang):
                            synonym_match_count += 1
                            break
                
                synonym_ratio = synonym_match_count / len(correct_keywords)
                if synonym_ratio >= keyword_threshold:
                    return {"match": True, "semantic": True}
        
        # ========= Phương pháp 1: Exact word-based match ==========
        if word_similarity >= word_exact_threshold:
            return {"match": True, "semantic": False}
        
        # ========= Phương pháp 2: Fuzzy match ==========
        if char_similarity >= exact_fuzzy_threshold:
            return {"match": True, "semantic": False}
        
        # ========= Phương pháp 3: Semantic matching (char + keyword similarity) ==========
        if char_similarity >= semantic_threshold:
            if correct_keywords and user_keywords:
                # Check exact keyword match
                exact_keyword_match = sum(1 for w in correct_keywords if w in user_keywords)
                exact_keyword_ratio = exact_keyword_match / len(correct_keywords)
                
                # Check semantic word match (similarity-based)
                semantic_keyword_match = 0
                for correct_word in correct_keywords:
                    for user_word in user_keywords:
                        if self._check_semantic_word_match(user_word, correct_word, lang, threshold=0.75):
                            semantic_keyword_match += 1
                            break
                
                semantic_keyword_ratio = semantic_keyword_match / len(correct_keywords)
                
                # Accept if either exact OR semantic keywords match
                if exact_keyword_ratio >= keyword_threshold or semantic_keyword_ratio >= keyword_threshold:
                    return {"match": True, "semantic": True}
        
        return {"match": False, "semantic": False}
    
    def _detect_language(self, text):
        """
        Đoán ngôn ngữ từ text
        Returns: "en", "vi", "zh", "ja"
        """
        # Simple heuristic: check for common patterns
        text_lower = text.lower()
        
        # Vietnamese: có các ký tự như à, á, ả, etc.
        if any(c in text for c in 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'):
            return "vi"
        
        # Chinese: CJK characters (thường từ 4E00-9FFF)
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            return "zh"
        
        # Japanese: Hiragana hoặc Katakana
        if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
            return "ja"
        
        # Default English
        return "en"
    
    def add_result(self, question_num, question_text, user_answer, correct_answer, score):
        """Thêm kết quả một câu"""
        self.results.append({
            'question': question_num,
            'text': question_text,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'score': score
        })
        self.total_points += score
        self.questions_answered += 1
    
    def get_average_score(self):
        """Tính điểm trung bình"""
        if self.questions_answered == 0:
            return 0
        return (self.total_points / (self.questions_answered * 10)) * 100
    
    def get_grade(self, percentage):
        """Xác định xếp loại"""
        if percentage >= 90:
            return "A - Xuất sắc"
        elif percentage >= 80:
            return "B - Tốt"
        elif percentage >= 70:
            return "C - Khá"
        elif percentage >= 60:
            return "D - Đạt"
        else:
            return "F - Chưa đạt"
    
    def print_summary(self):
        """In tóm tắt kết quả"""
        print("\n" + "="*60)
        print("📊 KẾT QUẢ KIỂM TRA")
        print("="*60)
        
        average = self.get_average_score()
        grade = self.get_grade(average)
        
        print(f"Tổng điểm: {self.total_points}/{self.questions_answered * 10}")
        print(f"Điểm trung bình: {average:.1f}/100")
        print(f"Xếp loại: {grade}")
        print("="*60)
        
        return average, grade
    
    def print_detailed_results(self):
        """In chi tiết kết quả từng câu"""
        print("\n📋 CHI TIẾT KẾT QUẢ:")
        print("-"*60)
        for result in self.results:
            print(f"\nCâu {result['question']}: {result['text'][:50]}...")
            print(f"  Your answer: {result['user_answer']}")
            print(f"  Correct: {result['correct_answer']}")
            print(f"  Score: {result['score']}/10")
        print("-"*60)
