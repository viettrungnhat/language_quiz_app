"""
Database Manager for Spaced Repetition
Manages SQLite database for tracking word study history, wrong answers, and review schedules
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class StudyHistoryDB:
    """Manage study history database for spaced repetition"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent / "study_history.db"
        
        self.db_path = Path(db_path)
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Create words table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS words (
                word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                language TEXT NOT NULL,
                level TEXT DEFAULT 'A1',
                wrong_count INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                next_review_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(word, language)
            )
        """)
        
        # Create study log table for detailed tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_name TEXT,
                sheet_name TEXT,
                FOREIGN KEY (word_id) REFERENCES words(word_id)
            )
        """)
        
        # Create review schedule table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_schedule (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                due_date TIMESTAMP NOT NULL,
                interval_days INTEGER DEFAULT 1,
                repetition_count INTEGER DEFAULT 0,
                easiness_factor REAL DEFAULT 2.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (word_id) REFERENCES words(word_id)
            )
        """)
        
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def add_or_update_word(self, word: str, language: str, level: str = "A1") -> int:
        """Add or get word ID"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT word_id FROM words WHERE word = ? AND language = ?",
            (word.strip(), language)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        cursor.execute(
            "INSERT INTO words (word, language, level) VALUES (?, ?, ?)",
            (word.strip(), language, level)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def log_answer(self, word_id: int, is_correct: bool, file_name: str = "", sheet_name: str = ""):
        """Log a quiz answer"""
        cursor = self.conn.cursor()
        
        # Update word statistics
        if is_correct:
            cursor.execute(
                "UPDATE words SET correct_count = correct_count + 1, last_reviewed = CURRENT_TIMESTAMP WHERE word_id = ?",
                (word_id,)
            )
        else:
            cursor.execute(
                "UPDATE words SET wrong_count = wrong_count + 1, last_reviewed = CURRENT_TIMESTAMP WHERE word_id = ?",
                (word_id,)
            )
        
        # Log in study log
        cursor.execute(
            "INSERT INTO study_log (word_id, is_correct, file_name, sheet_name) VALUES (?, ?, ?, ?)",
            (word_id, is_correct, file_name, sheet_name)
        )
        
        # Update next review date if wrong
        if not is_correct:
            self._update_review_date(word_id)
        
        self.conn.commit()
    
    def _update_review_date(self, word_id: int):
        """Update next review date using spaced repetition algorithm"""
        cursor = self.conn.cursor()
        
        # Get word's wrong count
        cursor.execute("SELECT wrong_count FROM words WHERE word_id = ?", (word_id,))
        result = cursor.fetchone()
        if not result:
            return
        
        wrong_count = result[0]
        
        # Spaced repetition intervals
        intervals = {
            1: 1,      # First wrong: review in 1 day
            2: 3,      # Second wrong: review in 3 days
            3: 7,      # Third wrong: review in 7 days
            4: 14,     # Fourth wrong: review in 14 days
            5: 30,     # Fifth+ wrong: review in 30 days
        }
        
        days = intervals.get(min(wrong_count, 5), 30)
        next_date = datetime.now() + timedelta(days=days)
        
        cursor.execute(
            "UPDATE words SET next_review_date = ? WHERE word_id = ?",
            (next_date, word_id)
        )
        self.conn.commit()
    
    def get_weak_words(self, language: Optional[str] = None) -> List[Dict]:
        """Get words that need review (wrong_count > 0 and next_review_date <= today)"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT word_id, word, language, level, wrong_count, correct_count, last_reviewed
            FROM words
            WHERE wrong_count > 0 AND (next_review_date IS NULL OR next_review_date <= datetime('now'))
        """
        
        if language:
            query += " AND language = ?"
            cursor.execute(query + " ORDER BY wrong_count DESC", (language,))
        else:
            cursor.execute(query + " ORDER BY wrong_count DESC")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_word_stats(self, word_id: int) -> Optional[Dict]:
        """Get detailed stats for a word"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT word_id, word, language, level, wrong_count, correct_count, 
                   last_reviewed, next_review_date
            FROM words
            WHERE word_id = ?
            """,
            (word_id,)
        )
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def get_all_stats(self) -> List[Dict]:
        """Get stats for all words"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT word_id, word, language, level, wrong_count, correct_count, 
                   last_reviewed, next_review_date
            FROM words
            ORDER BY wrong_count DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics_by_language(self) -> Dict[str, Dict]:
        """Get summary statistics grouped by language"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT language,
                   COUNT(*) as total_words,
                   SUM(wrong_count) as total_wrong,
                   SUM(correct_count) as total_correct,
                   AVG(CAST(correct_count AS FLOAT) / (correct_count + wrong_count)) as accuracy
            FROM words
            GROUP BY language
            """
        )
        
        stats = {}
        for row in cursor.fetchall():
            lang = row[0]
            stats[lang] = {
                'total_words': row[1],
                'total_wrong': row[2] or 0,
                'total_correct': row[3] or 0,
                'accuracy': round(row[4] * 100, 2) if row[4] else 0,
            }
        
        return stats
    
    def get_study_log(self, word_id: Optional[int] = None, days: int = 30) -> List[Dict]:
        """Get study log entries"""
        cursor = self.conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if word_id:
            cursor.execute(
                """
                SELECT log_id, word_id, is_correct, timestamp, file_name, sheet_name
                FROM study_log
                WHERE word_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                """,
                (word_id, cutoff_date)
            )
        else:
            cursor.execute(
                """
                SELECT log_id, word_id, is_correct, timestamp, file_name, sheet_name
                FROM study_log
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
                """,
                (cutoff_date,)
            )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def reset_word(self, word_id: int):
        """Reset a word's progress (for testing or starting over)"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE words 
            SET wrong_count = 0, correct_count = 0, last_reviewed = NULL, next_review_date = NULL
            WHERE word_id = ?
            """,
            (word_id,)
        )
        self.conn.commit()
    
    def delete_word(self, word_id: int):
        """Delete a word and its study log"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM study_log WHERE word_id = ?", (word_id,))
        cursor.execute("DELETE FROM review_schedule WHERE word_id = ?", (word_id,))
        cursor.execute("DELETE FROM words WHERE word_id = ?", (word_id,))
        self.conn.commit()
    
    def clear_old_logs(self, days: int = 90):
        """Delete study logs older than specified days"""
        cursor = self.conn.cursor()
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor.execute("DELETE FROM study_log WHERE timestamp < ?", (cutoff_date,))
        self.conn.commit()
        return cursor.rowcount
    
    def __del__(self):
        """Ensure database connection is closed"""
        self.close()


if __name__ == "__main__":
    # Test database
    db = StudyHistoryDB()
    
    # Test adding words
    print("Testing Database...")
    w1 = db.add_or_update_word("hello", "English")
    w2 = db.add_or_update_word("world", "English")
    w3 = db.add_or_update_word("xin chào", "Vietnamese")
    
    # Test logging answers
    db.log_answer(w1, True, "test.xlsx", "Sheet1")
    db.log_answer(w2, False, "test.xlsx", "Sheet1")  # Wrong
    db.log_answer(w3, False, "test.xlsx", "Sheet1")  # Wrong
    
    # Test getting weak words
    weak = db.get_weak_words()
    print(f"\n📚 Weak words needing review: {len(weak)}")
    for w in weak:
        print(f"  - {w['word']} ({w['language']}) - Wrong: {w['wrong_count']}, Last: {w['last_reviewed']}")
    
    # Test statistics
    stats = db.get_statistics_by_language()
    print(f"\n📊 Statistics by language:")
    for lang, stat in stats.items():
        print(f"  {lang}: {stat}")
    
    print("\n✅ Database test passed!")
    db.close()
