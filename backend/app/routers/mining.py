from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import DailyMiningLog, Subject
from app.models.schemas import MiningTriggerRequest, MiningLogOut, APIUsageOut
from app.services.mining_engine import mine_questions_for_subject
from app.services.llm_router import usage_tracker
from app.services.search_router import search_usage

router = APIRouter(prefix="/mining", tags=["Mining"])


@router.post("/trigger")
async def trigger_mining(
    req: MiningTriggerRequest,
    db: AsyncSession = Depends(get_db),
):
    """Trigger question mining for a subject."""
    result = await mine_questions_for_subject(
        db=db,
        subject_id=req.subject_id,
        topic_name=req.topic_name,
        target_count=req.count,
    )
    return result


@router.post("/trigger-all")
async def trigger_mining_all(
    count_per_subject: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Trigger mining for all subjects."""
    subjects_result = await db.execute(select(Subject))
    subjects = subjects_result.scalars().all()

    results = []
    for subject in subjects:
        result = await mine_questions_for_subject(
            db=db,
            subject_id=subject.id,
            target_count=count_per_subject,
        )
        results.append(result)

    return {"results": results}


@router.get("/logs", response_model=list[MiningLogOut])
async def get_mining_logs(
    subject_id: Optional[int] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get mining logs."""
    query = select(DailyMiningLog).order_by(desc(DailyMiningLog.mined_date))
    if subject_id:
        query = query.where(DailyMiningLog.subject_id == subject_id)
    query = query.limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        MiningLogOut(
            id=log.id,
            subject_id=log.subject_id,
            questions_added=log.questions_added,
            api_used=log.api_used,
            tokens_used=log.tokens_used,
            status=log.status,
            mined_date=log.mined_date,
        )
        for log in logs
    ]


@router.get("/api-usage", response_model=APIUsageOut)
async def get_api_usage():
    """Get current API usage stats."""
    llm_usage = usage_tracker.get_usage()
    search_use = search_usage.get_usage()
    return APIUsageOut(
        **llm_usage,
        **search_use,
    )
