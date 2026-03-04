import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.llm_router import LLMRouter
from app.core.search_router import SearchRouter
from app.services.deduplication import DeduplicationEngine
from app.models.schema import Question, Topic, Subject, DailyMiningLog

class DailyMiningEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.llm_router = LLMRouter()
        self.search_router = SearchRouter()
        self.deduplicator = DeduplicationEngine(db_session)
        
    def mine_for_subject(self, subject_name: str, target_count: int = 100):
        subject = self.db.query(Subject).filter(Subject.name == subject_name).first()
        if not subject:
            logging.error(f"Subject '{subject_name}' not found.")
            return

        topics = self._rotate_topics(subject)
        questions_added = 0
        
        for topic in topics:
            if questions_added >= target_count:
                break
                
            logging.info(f"Mining for Topic: {topic.name}")
            
            # Step 2: Search Query Generator
            queries = self._generate_search_queries(subject.name, topic.name)
            
            for query in queries:
                if questions_added >= target_count:
                    break
                    
                # Step 3 & 4: Web Scrape via APIs & Extract
                raw_content = self.search_router.search(query, self.llm_router)
                
                # Step 5: LLM Structuring
                structured_mcqs = self._structure_mcqs(raw_content, subject.name, topic.name)
                
                # Step 6: Deduplication & Step 7: DB Insert
                for mcq in structured_mcqs:
                    if questions_added >= target_count:
                        break
                    
                    if not self.deduplicator.is_duplicate(mcq['question_text']):
                        new_q = Question(
                            subject_id=subject.id,
                            topic_id=topic.id,
                            question_text=mcq['question_text'],
                            options=mcq['options'],
                            correct_index=mcq['correct_index'],
                            explanation=mcq['explanation'],
                            difficulty=mcq.get('difficulty', 'medium'),
                            source=mcq.get('source', 'web'),
                            hash=self.deduplicator.hash_question(mcq['question_text'])
                        )
                        self.db.add(new_q)
                        questions_added += 1

        self.db.commit()
        
        # Log mining stats
        log = DailyMiningLog(
            subject_id=subject.id,
            questions_added=questions_added,
            status="SUCCESS"
        )
        self.db.add(log)
        self.db.commit()
        logging.info(f"Finished mining {questions_added} questions for {subject_name}")

    def _rotate_topics(self, subject: Subject):
        # Rotate logic: Get topics ordered by last mined date or lowest question count
        return self.db.query(Topic).filter(Topic.subject_id == subject.id).all()

    def _generate_search_queries(self, subject_name: str, topic_name: str) -> list:
        prompt = f"Generate 5 high-quality search queries for SSC-level {subject_name} MCQs on {topic_name}."
        res = self.llm_router.explain(prompt) # Using general model
        # parse raw lines... (Mocked for now)
        return [f"{topic_name} MCQs for competitive exams"]

    def _structure_mcqs(self, raw_content, subject_name: str, topic_name: str) -> list:
        # Step 5: Send raw text to Gemini to extract JSON
        prompt = f"""
        Extract up to 5 high-quality MCQs from this text in strict JSON format.
        Text: {raw_content}
        Expected JSON Format:
        [{{
            "question_text": "text", "options": ["A", "B", "C", "D"], 
            "correct_index": 0, "explanation": "text", "difficulty": "medium", "source": "web"
        }}]
        """
        res = self.llm_router.structure_json(prompt)
        
        # Assuming we get a valid JSON response string
        try:
            # Mocking the JSON response parsing
            return [
                {
                    "question_text": f"Sample mock q for {topic_name}?",
                    "options": ["Ans 1", "Ans 2", "Ans 3", "Ans 4"],
                    "correct_index": 0,
                    "explanation": "Because it's right.",
                    "difficulty": "medium",
                    "source": "tavily"
                }
            ]
        except Exception:
            return []
