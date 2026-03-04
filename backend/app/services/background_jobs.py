"""Background job system for daily question mining."""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from app.core.database import async_session
from app.models.database import Subject
from app.services.mining_engine import mine_questions_for_subject

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# Schedule: staggered mining per subject
MINING_SCHEDULE = [
    ("English", 2, 0),        # 02:00 AM
    ("Indian Polity", 2, 20), # 02:20 AM
    ("Geography", 2, 40),     # 02:40 AM
    ("Economics", 3, 0),      # 03:00 AM
    ("History", 3, 20),       # 03:20 AM
    ("Static GK", 3, 40),     # 03:40 AM
]


async def mine_subject_by_name(subject_name: str):
    """Mine questions for a specific subject by name."""
    try:
        async with async_session() as db:
            result = await db.execute(
                select(Subject).where(Subject.name == subject_name)
            )
            subject = result.scalar_one_or_none()
            if not subject:
                logger.error(f"Subject not found: {subject_name}")
                return

            logger.info(f"Starting daily mining for: {subject_name}")
            mining_result = await mine_questions_for_subject(
                db=db,
                subject_id=subject.id,
                target_count=100,
            )
            logger.info(
                f"Mining completed for {subject_name}: "
                f"{mining_result.get('questions_added', 0)} questions added"
            )
    except Exception as e:
        logger.error(f"Mining job failed for {subject_name}: {e}")


def setup_scheduler():
    """Set up the APScheduler with daily mining jobs."""
    for subject_name, hour, minute in MINING_SCHEDULE:
        scheduler.add_job(
            mine_subject_by_name,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[subject_name],
            id=f"mine_{subject_name.lower().replace(' ', '_')}",
            name=f"Daily mining: {subject_name}",
            replace_existing=True,
        )
    logger.info("Background scheduler configured with daily mining jobs")


def start_scheduler():
    """Start the scheduler."""
    if not scheduler.running:
        setup_scheduler()
        scheduler.start()
        logger.info("Background scheduler started")


def stop_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")
