from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import Question
from app.models.schemas import QuestionOut, QuestionBrief, GenerateRequest
from app.services.mining_engine import mine_questions_for_subject

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=list[QuestionOut])
async def list_questions(
    subject_id: Optional[int] = Query(None),
    topic_id: Optional[int] = Query(None),
    difficulty: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """Get questions with optional filters."""
    query = select(Question)
    if subject_id:
        query = query.where(Question.subject_id == subject_id)
    if topic_id:
        query = query.where(Question.topic_id == topic_id)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    questions = result.scalars().all()

    return [
        QuestionOut(
            id=q.id,
            subject_id=q.subject_id,
            topic_id=q.topic_id,
            question_text=q.question_text,
            options=q.options if isinstance(q.options, list) else [],
            correct_index=q.correct_index,
            explanation=q.explanation,
            difficulty=q.difficulty,
            source=q.source,
            created_at=q.created_at,
        )
        for q in questions
    ]


@router.get("/count")
async def count_questions(
    subject_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get total question count."""
    query = select(func.count(Question.id))
    if subject_id:
        query = query.where(Question.subject_id == subject_id)
    result = await db.execute(query)
    count = result.scalar() or 0
    return {"count": count}


@router.get("/random", response_model=list[QuestionBrief])
async def get_random_questions(
    subject_id: Optional[int] = Query(None),
    count: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get random questions for quiz (without answers)."""
    query = select(Question)
    if subject_id:
        query = query.where(Question.subject_id == subject_id)
    query = query.order_by(func.random()).limit(count)

    result = await db.execute(query)
    questions = result.scalars().all()

    return [
        QuestionBrief(
            id=q.id,
            subject_id=q.subject_id,
            topic_id=q.topic_id,
            question_text=q.question_text,
            options=q.options if isinstance(q.options, list) else [],
            difficulty=q.difficulty,
        )
        for q in questions
    ]


@router.get("/{question_id}", response_model=QuestionOut)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific question with answer."""
    question = await db.get(Question, question_id)
    if not question:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Question not found")

    return QuestionOut(
        id=question.id,
        subject_id=question.subject_id,
        topic_id=question.topic_id,
        question_text=question.question_text,
        options=question.options if isinstance(question.options, list) else [],
        correct_index=question.correct_index,
        explanation=question.explanation,
        difficulty=question.difficulty,
        source=question.source,
        created_at=question.created_at,
    )


@router.post("/generate")
async def generate_questions(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate new questions using AI mining engine."""
    result = await mine_questions_for_subject(
        db=db,
        subject_id=req.subject_id,
        topic_name=None,
        target_count=req.count,
    )
    return result
