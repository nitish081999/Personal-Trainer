from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Subject ---
class SubjectOut(BaseModel):
    id: int
    name: str
    topic_count: int = 0
    question_count: int = 0

    class Config:
        from_attributes = True


# --- Topic ---
class TopicOut(BaseModel):
    id: int
    subject_id: int
    name: str
    question_count: int = 0

    class Config:
        from_attributes = True


# --- Question ---
class QuestionOut(BaseModel):
    id: int
    subject_id: int
    topic_id: Optional[int] = None
    question_text: str
    options: list[str]
    correct_index: int
    explanation: Optional[str] = None
    difficulty: str
    source: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuestionBrief(BaseModel):
    """Question without answer for quiz mode"""
    id: int
    subject_id: int
    topic_id: Optional[int] = None
    question_text: str
    options: list[str]
    difficulty: str

    class Config:
        from_attributes = True


class GenerateRequest(BaseModel):
    subject_id: int
    topic_id: Optional[int] = None
    count: int = 10
    difficulty: str = "medium"


# --- Attempt ---
class AttemptCreate(BaseModel):
    user_id: str
    question_id: int
    selected_option: int
    time_taken: Optional[float] = None


class AttemptOut(BaseModel):
    id: int
    user_id: str
    question_id: int
    selected_option: int
    is_correct: bool
    time_taken: Optional[float] = None
    attempt_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttemptResult(BaseModel):
    is_correct: bool
    correct_index: int
    explanation: Optional[str] = None
    attempt: AttemptOut


# --- Analytics ---
class TopicAccuracy(BaseModel):
    topic_id: int
    topic_name: str
    total: int
    correct: int
    accuracy: float


class SubjectAccuracy(BaseModel):
    subject_id: int
    subject_name: str
    total: int
    correct: int
    accuracy: float
    topics: list[TopicAccuracy] = []


class UserAnalytics(BaseModel):
    user_id: str
    total_attempts: int
    total_correct: int
    overall_accuracy: float
    recent_accuracy: float  # last 50
    average_time: float
    subjects: list[SubjectAccuracy] = []


class WeakTopicOut(BaseModel):
    topic_id: int
    topic_name: str
    subject_name: str
    weakness_score: float
    accuracy: float

    class Config:
        from_attributes = True


# --- Quiz ---
class AdaptiveQuizRequest(BaseModel):
    user_id: str
    count: int = 20
    focus_weak: bool = True


class AdaptiveQuizOut(BaseModel):
    questions: list[QuestionBrief]
    focus_areas: list[str] = []


# --- Mining ---
class MiningTriggerRequest(BaseModel):
    subject_id: int
    topic_name: Optional[str] = None
    count: int = 20


class MiningLogOut(BaseModel):
    id: int
    subject_id: int
    questions_added: int
    api_used: Optional[str] = None
    tokens_used: int
    status: str
    mined_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- API Usage ---
class APIUsageOut(BaseModel):
    groq_tokens_used: int = 0
    groq_daily_limit: int = 0
    gemini_calls_used: int = 0
    gemini_daily_limit: int = 0
    mistral_tokens_used: int = 0
    mistral_daily_limit: int = 0
    tavily_calls_used: int = 0
    tavily_daily_limit: int = 0
    serper_calls_used: int = 0
    serper_daily_limit: int = 0
