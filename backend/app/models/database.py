import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    topics = relationship("Topic", back_populates="subject", lazy="selectin")
    questions = relationship("Question", back_populates="subject", lazy="selectin")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(200), nullable=False)

    subject = relationship("Subject", back_populates="topics")
    questions = relationship("Question", back_populates="topic", lazy="selectin")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of 4 options
    correct_index = Column(Integer, nullable=False)  # 0-3
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    source = Column(String(500), nullable=True)
    hash = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    subject = relationship("Subject", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    attempts = relationship("UserAttempt", back_populates="question", lazy="selectin")

    __table_args__ = (
        Index("ix_questions_subject", "subject_id"),
        Index("ix_questions_topic", "topic_id"),
        Index("ix_questions_difficulty", "difficulty"),
        Index("ix_questions_hash", "hash"),
    )


class UserAttempt(Base):
    __tablename__ = "user_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Float, nullable=True)  # seconds
    attempt_date = Column(DateTime, default=datetime.datetime.utcnow)

    question = relationship("Question", back_populates="attempts")

    __table_args__ = (
        Index("ix_attempts_user", "user_id"),
        Index("ix_attempts_date", "attempt_date"),
    )


class WeakTopic(Base):
    __tablename__ = "weak_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    weakness_score = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    topic = relationship("Topic")

    __table_args__ = (
        Index("ix_weak_user_topic", "user_id", "topic_id", unique=True),
    )


class DailyMiningLog(Base):
    __tablename__ = "daily_mining_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    questions_added = Column(Integer, default=0)
    api_used = Column(String(100), nullable=True)
    tokens_used = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    mined_date = Column(DateTime, default=datetime.datetime.utcnow)

    subject = relationship("Subject")
