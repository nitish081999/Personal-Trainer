from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import Subject, Topic, Question
from app.models.schemas import SubjectOut, TopicOut

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=list[SubjectOut])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    """List all subjects with topic and question counts."""
    result = await db.execute(select(Subject))
    subjects = result.scalars().all()

    out = []
    for s in subjects:
        # Count topics
        topic_count_result = await db.execute(
            select(func.count(Topic.id)).where(Topic.subject_id == s.id)
        )
        topic_count = topic_count_result.scalar() or 0

        # Count questions
        q_count_result = await db.execute(
            select(func.count(Question.id)).where(Question.subject_id == s.id)
        )
        q_count = q_count_result.scalar() or 0

        out.append(SubjectOut(
            id=s.id,
            name=s.name,
            topic_count=topic_count,
            question_count=q_count,
        ))

    return out


@router.get("/{subject_id}/topics", response_model=list[TopicOut])
async def list_topics(subject_id: int, db: AsyncSession = Depends(get_db)):
    """List all topics for a subject with question counts."""
    result = await db.execute(
        select(Topic).where(Topic.subject_id == subject_id)
    )
    topics = result.scalars().all()

    out = []
    for t in topics:
        q_count_result = await db.execute(
            select(func.count(Question.id)).where(Question.topic_id == t.id)
        )
        q_count = q_count_result.scalar() or 0
        out.append(TopicOut(
            id=t.id,
            subject_id=t.subject_id,
            name=t.name,
            question_count=q_count,
        ))

    return out
