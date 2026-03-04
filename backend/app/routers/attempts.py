from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import Question, UserAttempt
from app.models.schemas import AttemptCreate, AttemptResult, AttemptOut

router = APIRouter(prefix="/attempts", tags=["Attempts"])


@router.post("", response_model=AttemptResult)
async def record_attempt(
    attempt: AttemptCreate,
    db: AsyncSession = Depends(get_db),
):
    """Record a user's attempt at a question."""
    question = await db.get(Question, attempt.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = attempt.selected_option == question.correct_index

    db_attempt = UserAttempt(
        user_id=attempt.user_id,
        question_id=attempt.question_id,
        selected_option=attempt.selected_option,
        is_correct=is_correct,
        time_taken=attempt.time_taken,
    )
    db.add(db_attempt)
    await db.commit()
    await db.refresh(db_attempt)

    return AttemptResult(
        is_correct=is_correct,
        correct_index=question.correct_index,
        explanation=question.explanation,
        attempt=AttemptOut(
            id=db_attempt.id,
            user_id=db_attempt.user_id,
            question_id=db_attempt.question_id,
            selected_option=db_attempt.selected_option,
            is_correct=db_attempt.is_correct,
            time_taken=db_attempt.time_taken,
            attempt_date=db_attempt.attempt_date,
        ),
    )
