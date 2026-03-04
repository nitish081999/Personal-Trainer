import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./ssc_exam.db"
    )

    # LLM API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

    # Search API Keys
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")

    # Mining config
    QUESTIONS_PER_SUBJECT_PER_DAY: int = 100
    MINING_BATCH_SIZE: int = 5

    # Rate limits (daily)
    GROQ_DAILY_TOKEN_LIMIT: int = 500000
    GEMINI_DAILY_CALL_LIMIT: int = 1500
    MISTRAL_DAILY_TOKEN_LIMIT: int = 500000
    TAVILY_DAILY_LIMIT: int = 1000
    SERPER_DAILY_LIMIT: int = 2500

    class Config:
        env_file = ".env"


settings = Settings()
