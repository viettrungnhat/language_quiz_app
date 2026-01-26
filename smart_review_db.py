"""
Enhanced Database Manager for Smart Review System
Mở rộng db_manager.py với tính năng Smart Review, Flashcard, Dashboard
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json

class SmartReviewDB:
    """Enhanced database manager với Smart Review features"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent / "smart_review.db"
        
        self.db_path = Path(db_path)
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database với các bảng mới"""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # 📚 Table 1: Question History - Lưu lịch sử từng câu hỏi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                user_name TEXT NOT NULL,
                quiz_type TEXT NOT NULL,  -- meaning/example/vietnamese
                test_mode INTEGER NOT NULL,  -- 1 or 2
                is_correct BOOLEAN NOT NULL,
                user_answer TEXT,
                score INTEGER,  -- 0-10
                attempt_count INTEGER DEFAULT 1,
                mastery_level INTEGER DEFAULT 0,  -- 0-5 (0=new, 5=mastered)
                last_attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_path, question_id, user_name, quiz_type)
            )
        """)
        
        # Index cho performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_question_mastery 
            ON question_history(file_path, mastery_level, attempt_count)
        """)
        
        # 🔄 Table 2: Flashcard Status - Đánh dấu câu đã thuộc/chưa thuộc
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcard_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                user_name TEXT NOT NULL,
                status TEXT DEFAULT 'not_learned',  -- not_learned/learning/mastered
                marked_as_known BOOLEAN DEFAULT 0,
                review_count INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_path, question_id, user_name)
            )
        """)
        
        # 📊 Table 3: Study Sessions - Thống kê phiên học
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                session_date DATE NOT NULL,
                quiz_type TEXT NOT NULL,
                test_mode INTEGER NOT NULL,
                duration_seconds INTEGER,
                total_questions INTEGER NOT NULL,
                correct_count INTEGER NOT NULL,
                wrong_count INTEGER NOT NULL,
                average_score REAL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Index cho dashboard queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_date 
            ON study_sessions(user_name, session_date)
        """)
        
        self.conn.commit()
        print("✅ Smart Review Database initialized!")
    
    # ===== SMART REVIEW METHODS =====
    
    def save_question_result(self, file_path: str, question_id: int, 
                            question_text: str, correct_answer: str,
                            user_name: str, quiz_type: str, test_mode: int,
                            is_correct: bool, user_answer: str, score: int):
        """Lưu kết quả 1 câu hỏi và cập nhật mastery level"""
        cursor = self.conn.cursor()
        
        # Check if exists
        cursor.execute("""
            SELECT attempt_count, mastery_level FROM question_history
            WHERE file_path=? AND question_id=? AND user_name=? AND quiz_type=?
        """, (file_path, question_id, user_name, quiz_type))
        
        existing = cursor.fetchone()
        
        if existing:
            attempt_count = existing['attempt_count'] + 1
            mastery_level = existing['mastery_level']
            
            # Update mastery level based on result
            if is_correct:
                mastery_level = min(5, mastery_level + 1)  # Cap at 5
            else:
                mastery_level = max(0, mastery_level - 1)  # Floor at 0
            
            cursor.execute("""
                UPDATE question_history
                SET is_correct=?, user_answer=?, score=?,
                    attempt_count=?, mastery_level=?,
                    last_attempt_date=CURRENT_TIMESTAMP
                WHERE file_path=? AND question_id=? AND user_name=? AND quiz_type=?
            """, (is_correct, user_answer, score, attempt_count, mastery_level,
                  file_path, question_id, user_name, quiz_type))
        else:
            # First attempt
            mastery_level = 1 if is_correct else 0
            cursor.execute("""
                INSERT INTO question_history 
                (file_path, question_id, question_text, correct_answer,
                 user_name, quiz_type, test_mode, is_correct, user_answer,
                 score, attempt_count, mastery_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (file_path, question_id, question_text, correct_answer,
                  user_name, quiz_type, test_mode, is_correct, user_answer,
                  score, mastery_level))
        
        self.conn.commit()
    
    def get_weak_questions(self, file_path: str, user_name: str, 
                          limit: int = 20) -> List[Dict]:
        """Lấy các câu hỏi yếu nhất để ôn tập"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT question_id, question_text, correct_answer, quiz_type,
                   mastery_level, attempt_count, last_attempt_date
            FROM question_history
            WHERE file_path=? AND user_name=?
            AND mastery_level < 3
            ORDER BY mastery_level ASC, attempt_count DESC, last_attempt_date ASC
            LIMIT ?
        """, (file_path, user_name, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'question_id': row['question_id'],
                'question_text': row['question_text'],
                'correct_answer': row['correct_answer'],
                'quiz_type': row['quiz_type'],
                'mastery_level': row['mastery_level'],
                'attempt_count': row['attempt_count'],
                'last_attempt_date': row['last_attempt_date']
            })
        
        return results
    
    def get_mastery_stats(self, file_path: str, user_name: str) -> Dict:
        """Thống kê mastery level"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN mastery_level = 5 THEN 1 ELSE 0 END) as mastered,
                SUM(CASE WHEN mastery_level >= 3 THEN 1 ELSE 0 END) as good,
                SUM(CASE WHEN mastery_level < 3 THEN 1 ELSE 0 END) as weak
            FROM question_history
            WHERE file_path=? AND user_name=?
        """, (file_path, user_name))
        
        row = cursor.fetchone()
        return {
            'total': row['total'] or 0,
            'mastered': row['mastered'] or 0,
            'good': row['good'] or 0,
            'weak': row['weak'] or 0
        }
    
    # ===== FLASHCARD METHODS =====
    
    def mark_flashcard(self, file_path: str, question_id: int,
                      question_text: str, user_name: str, is_known: bool):
        """Đánh dấu flashcard là đã thuộc/chưa thuộc"""
        cursor = self.conn.cursor()
        
        status = 'mastered' if is_known else 'learning'
        
        cursor.execute("""
            INSERT OR REPLACE INTO flashcard_status
            (file_path, question_id, question_text, user_name, 
             status, marked_as_known, review_count, last_reviewed)
            VALUES (?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT review_count FROM flashcard_status 
                              WHERE file_path=? AND question_id=? AND user_name=?), 0) + 1,
                    CURRENT_TIMESTAMP)
        """, (file_path, question_id, question_text, user_name, status, is_known,
              file_path, question_id, user_name))
        
        self.conn.commit()
    
    def get_flashcard_status(self, file_path: str, user_name: str) -> Dict[int, str]:
        """Lấy status của tất cả flashcards"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT question_id, status, marked_as_known
            FROM flashcard_status
            WHERE file_path=? AND user_name=?
        """, (file_path, user_name))
        
        return {row['question_id']: row['status'] for row in cursor.fetchall()}
    
    def get_known_questions(self, file_path: str, user_name: str) -> List[int]:
        """Lấy danh sách ID các câu đã đánh dấu thuộc"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT question_id FROM flashcard_status
            WHERE file_path=? AND user_name=? AND marked_as_known=1
        """, (file_path, user_name))
        
        return [row['question_id'] for row in cursor.fetchall()]
    
    # ===== DASHBOARD METHODS =====
    
    def save_session(self, user_name: str, file_path: str, quiz_type: str,
                    test_mode: int, total: int, correct: int, wrong: int,
                    avg_score: float, duration: int):
        """Lưu thông tin phiên học"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO study_sessions
            (user_name, file_path, session_date, quiz_type, test_mode,
             duration_seconds, total_questions, correct_count, wrong_count,
             average_score, end_time)
            VALUES (?, ?, DATE('now'), ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_name, file_path, quiz_type, test_mode, duration,
              total, correct, wrong, avg_score))
        
        self.conn.commit()
    
    def get_progress_by_period(self, user_name: str, 
                               period: str = 'day', limit: int = 30) -> List[Dict]:
        """Lấy tiến độ theo ngày/tuần/tháng"""
        cursor = self.conn.cursor()
        
        if period == 'day':
            group_by = "DATE(session_date)"
            date_format = "session_date"
        elif period == 'week':
            group_by = "strftime('%Y-W%W', session_date)"
            date_format = "strftime('%Y-W%W', session_date)"
        else:  # month
            group_by = "strftime('%Y-%m', session_date)"
            date_format = "strftime('%Y-%m', session_date)"
        
        cursor.execute(f"""
            SELECT 
                {date_format} as period,
                SUM(total_questions) as total_questions,
                SUM(correct_count) as correct_count,
                AVG(average_score) as avg_score,
                COUNT(*) as session_count
            FROM study_sessions
            WHERE user_name=?
            GROUP BY {group_by}
            ORDER BY period DESC
            LIMIT ?
        """, (user_name, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'period': row['period'],
                'total_questions': row['total_questions'],
                'correct_count': row['correct_count'],
                'accuracy': (row['correct_count'] / row['total_questions'] * 100) if row['total_questions'] > 0 else 0,
                'avg_score': row['avg_score'],
                'session_count': row['session_count']
            })
        
        return results
    
    def get_cumulative_study_time(self, user_name: str) -> int:
        """Tổng thời gian học (giây)"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT SUM(duration_seconds) as total_seconds
            FROM study_sessions
            WHERE user_name=?
        """, (user_name,))
        
        row = cursor.fetchone()
        return row['total_seconds'] or 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# ===== TESTING =====
if __name__ == "__main__":
    print("🧪 Testing Smart Review Database...\n")
    
    db = SmartReviewDB()
    
    # Test save question result
    db.save_question_result(
        file_path="test.xlsx",
        question_id=1,
        question_text="Hello",
        correct_answer="Xin chào",
        user_name="TestUser",
        quiz_type="meaning",
        test_mode=1,
        is_correct=False,
        user_answer="chào mừng",
        score=3
    )
    
    # Test get weak questions
    weak = db.get_weak_questions("test.xlsx", "TestUser")
    print(f"📚 Weak questions: {len(weak)}")
    
    # Test mastery stats
    stats = db.get_mastery_stats("test.xlsx", "TestUser")
    print(f"📊 Mastery stats: {stats}")
    
    db.close()
    print("\n✅ Test completed!")
