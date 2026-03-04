import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db, async_session
from app.routers import subjects, questions, attempts, analytics, quiz, mining
from app.services.seed_data import seed_database
from app.services.background_jobs import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()

    # Seed data
    async with async_session() as db:
        await seed_database(db)

    # Start background scheduler
    start_scheduler()
    logger.info("Application started successfully!")

    yield

    # Shutdown
    stop_scheduler()
    logger.info("Application shut down.")


app = FastAPI(
    title="SSC Exam Prep Platform",
    description="AI-powered SSC exam preparation with adaptive learning and daily question mining",
    version="1.0.0",
    lifespan=lifespan,
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(subjects.router)
app.include_router(questions.router)
app.include_router(attempts.router)
app.include_router(analytics.router)
app.include_router(quiz.router)
app.include_router(mining.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
