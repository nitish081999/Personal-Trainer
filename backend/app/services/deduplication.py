import hashlib
import logging

class DeduplicationEngine:
    def __init__(self, db_session):
        self.db = db_session

    def hash_question(self, question_text: str) -> str:
        normalized = question_text.strip().lower()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def is_duplicate(self, question_text: str) -> bool:
        # Basic hash check
        q_hash = self.hash_question(question_text)
        from app.models.schema import Question
        exists = self.db.query(Question).filter(Question.hash == q_hash).first()
        
        # Advanced check (cosine similarity) would use pgvector in Postgres
        # For MVP, hash match is sufficient
        if exists:
            logging.info(f"Duplicate found with hash {q_hash}")
            return True
        return False
