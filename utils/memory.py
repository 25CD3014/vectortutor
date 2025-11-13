"""
Knowledge Memory Module (SQLite)
Shared database for all agents to read/write knowledge, progress, and data
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class KnowledgeMemory:
    def __init__(self, db_path: str = "vectortutor.db"):
        """Initialize SQLite database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # PDF Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Flashcards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                topic TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)
        
        # Quizzes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer INTEGER,
                difficulty TEXT,
                topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)
        
        # Quiz Attempts/Performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER,
                user_answer INTEGER,
                is_correct INTEGER,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        """)
        
        # Revision Plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS revision_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                plan_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)
        
        # Chat History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_document(self, filename: str, content: str, metadata: Optional[Dict] = None) -> int:
        """Add a new document and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute("""
            INSERT INTO documents (filename, content, metadata)
            VALUES (?, ?, ?)
        """, (filename, content, metadata_json))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """Retrieve a document by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row["id"],
                "filename": row["filename"],
                "content": row["content"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
                "uploaded_at": row["uploaded_at"]
            }
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row["id"],
            "filename": row["filename"],
            "content": row["content"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else None,
            "uploaded_at": row["uploaded_at"]
        } for row in rows]
    
    def add_flashcard(self, document_id: int, question: str, answer: str, 
                     topic: Optional[str] = None, difficulty: Optional[str] = None) -> int:
        """Add a flashcard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO flashcards (document_id, question, answer, topic, difficulty)
            VALUES (?, ?, ?, ?, ?)
        """, (document_id, question, answer, topic, difficulty))
        
        flashcard_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return flashcard_id
    
    def get_flashcards(self, document_id: Optional[int] = None) -> List[Dict]:
        """Get flashcards, optionally filtered by document"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if document_id:
            cursor.execute("""
                SELECT * FROM flashcards WHERE document_id = ? ORDER BY created_at DESC
            """, (document_id,))
        else:
            cursor.execute("SELECT * FROM flashcards ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row["id"],
            "document_id": row["document_id"],
            "question": row["question"],
            "answer": row["answer"],
            "topic": row["topic"],
            "difficulty": row["difficulty"],
            "created_at": row["created_at"]
        } for row in rows]
    
    def add_quiz(self, document_id: int, question: str, options: List[str], 
                correct_answer: int, difficulty: str, topic: Optional[str] = None) -> int:
        """Add a quiz question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        options_json = json.dumps(options)
        cursor.execute("""
            INSERT INTO quizzes (document_id, question, options, correct_answer, difficulty, topic)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (document_id, question, options_json, correct_answer, difficulty, topic))
        
        quiz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return quiz_id
    
    def get_quizzes(self, document_id: Optional[int] = None, 
                   difficulty: Optional[str] = None) -> List[Dict]:
        """Get quiz questions, optionally filtered"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM quizzes WHERE 1=1"
        params = []
        
        if document_id:
            query += " AND document_id = ?"
            params.append(document_id)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row["id"],
            "document_id": row["document_id"],
            "question": row["question"],
            "options": json.loads(row["options"]),
            "correct_answer": row["correct_answer"],
            "difficulty": row["difficulty"],
            "topic": row["topic"],
            "created_at": row["created_at"]
        } for row in rows]
    
    def record_quiz_attempt(self, quiz_id: int, user_answer: int, is_correct: bool):
        """Record a quiz attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quiz_attempts (quiz_id, user_answer, is_correct)
            VALUES (?, ?, ?)
        """, (quiz_id, user_answer, 1 if is_correct else 0))
        
        conn.commit()
        conn.close()
    
    def get_performance_stats(self, document_id: Optional[int] = None) -> Dict:
        """Get performance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if document_id:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_attempts,
                    SUM(is_correct) as correct_attempts
                FROM quiz_attempts qa
                JOIN quizzes q ON qa.quiz_id = q.id
                WHERE q.document_id = ?
            """, (document_id,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_attempts,
                    SUM(is_correct) as correct_attempts
                FROM quiz_attempts
            """)
        
        row = cursor.fetchone()
        conn.close()
        
        total = row[0] or 0
        correct = row[1] or 0
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy": round(accuracy, 2)
        }
    
    def add_revision_plan(self, document_id: int, plan_data: Dict) -> int:
        """Add a revision plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        plan_json = json.dumps(plan_data)
        cursor.execute("""
            INSERT INTO revision_plans (document_id, plan_data)
            VALUES (?, ?)
        """, (document_id, plan_json))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plan_id
    
    def get_revision_plans(self, document_id: Optional[int] = None) -> List[Dict]:
        """Get revision plans"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if document_id:
            cursor.execute("""
                SELECT * FROM revision_plans WHERE document_id = ? ORDER BY created_at DESC
            """, (document_id,))
        else:
            cursor.execute("SELECT * FROM revision_plans ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row["id"],
            "document_id": row["document_id"],
            "plan_data": json.loads(row["plan_data"]),
            "created_at": row["created_at"]
        } for row in rows]
    
    def add_chat_message(self, document_id: int, question: str, answer: str):
        """Add a chat message to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (document_id, question, answer)
            VALUES (?, ?, ?)
        """, (document_id, question, answer))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, document_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """Get chat history"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if document_id:
            cursor.execute("""
                SELECT * FROM chat_history WHERE document_id = ? 
                ORDER BY asked_at DESC LIMIT ?
            """, (document_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM chat_history ORDER BY asked_at DESC LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row["id"],
            "document_id": row["document_id"],
            "question": row["question"],
            "answer": row["answer"],
            "asked_at": row["asked_at"]
        } for row in rows]

