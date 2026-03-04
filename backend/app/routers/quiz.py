from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import AdaptiveQuizRequest, AdaptiveQuizOut, QuestionBrief
from app.services.adaptive_engine import generate_adaptive_quiz

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/adaptive", response_model=AdaptiveQuizOut)
async def get_adaptive_quiz(
    req: AdaptiveQuizRequest,
    db: AsyncSession = Depends(get_db),
):
    """Generate an adaptive quiz based on user's weak areas."""
    result = await generate_adaptive_quiz(
        db=db,
        user_id=req.user_id,
        count=req.count,
        focus_weak=req.focus_weak,
    )
    return AdaptiveQuizOut(
        questions=[QuestionBrief(**q) for q in result["questions"]],
        focus_areas=result["focus_areas"],
    )
