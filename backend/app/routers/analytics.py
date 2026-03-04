from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.schemas import UserAnalytics, WeakTopicOut
from app.services.adaptive_engine import calculate_user_analytics, update_weak_topics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/{user_id}", response_model=UserAnalytics)
async def get_user_analytics(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get comprehensive analytics for a user."""
    analytics = await calculate_user_analytics(db, user_id)
    return UserAnalytics(**analytics)


@router.get("/{user_id}/weak-topics", response_model=list[WeakTopicOut])
async def get_weak_topics(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user's weak topics."""
    weak_topics = await update_weak_topics(db, user_id)
    return [WeakTopicOut(**wt) for wt in weak_topics]
