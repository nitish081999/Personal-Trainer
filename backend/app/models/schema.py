from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    name = Column(String, index=True)
    
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    question_text = Column(Text)
    options = Column(JSON)
    correct_index = Column(Integer)
    explanation = Column(Text)
    difficulty = Column(String)
    source = Column(String)
    hash = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserAttempt(Base):
    __tablename__ = "user_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_option = Column(Integer)
    is_correct = Column(Integer) # 1 for True, 0 for False
    time_taken = Column(Float)
    attempt_date = Column(DateTime(timezone=True), server_default=func.now())

class WeakTopic(Base):
    __tablename__ = "weak_topics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    weakness_score = Column(Float)

class DailyMiningLog(Base):
    __tablename__ = "daily_mining_logs"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    questions_added = Column(Integer)
    api_used = Column(String)
    token_used = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
