from app.models.schema import UserAttempt, WeakTopic, Question
from sqlalchemy.orm import Session
from sqlalchemy import func

class AdaptiveLearningEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def calculate_topic_accuracy(self, user_id: str, topic_id: int):
        attempts = self.db.query(UserAttempt).join(Question, UserAttempt.question_id == Question.id).filter(
            UserAttempt.user_id == user_id,
            Question.topic_id == topic_id
        ).order_by(UserAttempt.attempt_date.desc()).all()
        
        if not attempts:
            return None
            
        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)
        accuracy = correct / total
        
        # Recent accuracy - last 50 attempts
        recent_attempts = attempts[:50]
        recent_correct = sum(1 for a in recent_attempts if a.is_correct)
        recent_accuracy = recent_correct / len(recent_attempts) if recent_attempts else 0
        
        return accuracy, recent_accuracy

    def calculate_weakness_score(self, user_id: str):
        # find unique topics user has attempted
        topic_ids = self.db.query(Question.topic_id).join(UserAttempt, UserAttempt.question_id == Question.id).filter(
            UserAttempt.user_id == user_id
        ).distinct().all()
        
        topic_ids = [t[0] for t in topic_ids]
        
        for topic_id in topic_ids:
            res = self.calculate_topic_accuracy(user_id, topic_id)
            if res:
                accuracy, recent_accuracy = res
                weight_recent = 0.7  # prioritize recent performance
                weight_overall = 0.3
                
                blended_accuracy = (accuracy * weight_overall) + (recent_accuracy * weight_recent)
                weakness_score = 1 - blended_accuracy
                
                # Update or Insert WeakTopic
                weak_topic = self.db.query(WeakTopic).filter_by(user_id=user_id, topic_id=topic_id).first()
                if weak_topic:
                    weak_topic.weakness_score = weakness_score
                else:
                    weak_topic = WeakTopic(user_id=user_id, topic_id=topic_id, weakness_score=weakness_score)
                    self.db.add(weak_topic)
                    
        self.db.commit()

    def generate_revision_test(self, user_id: str, total_questions: int = 10):
        # Fetch the top 3 weakest topics
        weakest_topics = self.db.query(WeakTopic).filter(
            WeakTopic.user_id == user_id
        ).order_by(WeakTopic.weakness_score.desc()).limit(3).all()
        
        topic_ids = [w.topic_id for w in weakest_topics]
        
        if not topic_ids:
            # Fallback to general random questions
            return self.db.query(Question).order_by(func.random()).limit(total_questions).all()
            
        # Select questions from weakest topics that user hasn't seen or frequently gets wrong
        questions = self.db.query(Question).filter(
            Question.topic_id.in_(topic_ids)
        ).order_by(func.random()).limit(total_questions).all()
        
        return questions
