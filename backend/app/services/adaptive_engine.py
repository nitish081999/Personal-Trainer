import logging
from typing import Optional

from sqlalchemy import select, func, desc, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    UserAttempt, Question, Topic, Subject, WeakTopic,
)

logger = logging.getLogger(__name__)

RECENT_WINDOW = 50  # Number of recent attempts to consider
WEAKNESS_THRESHOLD = 0.6  # Below this accuracy = weak


async def calculate_user_analytics(db: AsyncSession, user_id: str) -> dict:
    """Calculate comprehensive analytics for a user."""
    # Total attempts
    total_result = await db.execute(
        select(
            func.count(UserAttempt.id).label("total"),
            func.sum(func.cast(UserAttempt.is_correct, type_=func.count(UserAttempt.id).type)).label("correct"),
        ).where(UserAttempt.user_id == user_id)
    )
    row = total_result.one_or_none()
    total_attempts = row.total if row and row.total else 0
    total_correct = row.correct if row and row.correct else 0
    overall_accuracy = (total_correct / total_attempts) if total_attempts > 0 else 0.0

    # Recent accuracy (last 50)
    recent_result = await db.execute(
        select(UserAttempt)
        .where(UserAttempt.user_id == user_id)
        .order_by(desc(UserAttempt.attempt_date))
        .limit(RECENT_WINDOW)
    )
    recent_attempts = recent_result.scalars().all()
    recent_correct = sum(1 for a in recent_attempts if a.is_correct)
    recent_total = len(recent_attempts)
    recent_accuracy = (recent_correct / recent_total) if recent_total > 0 else 0.0

    # Average time
    time_result = await db.execute(
        select(func.avg(UserAttempt.time_taken))
        .where(UserAttempt.user_id == user_id, UserAttempt.time_taken.isnot(None))
    )
    avg_time = time_result.scalar() or 0.0

    # Subject-wise breakdown
    subject_stats = []
    subjects = await db.execute(select(Subject))
    for subject in subjects.scalars().all():
        sub_result = await db.execute(
            select(
                func.count(UserAttempt.id).label("total"),
                func.sum(
                    case(
                        (UserAttempt.is_correct == True, 1),  # noqa: E712
                        else_=0,
                    )
                ).label("correct"),
            )
            .join(Question, UserAttempt.question_id == Question.id)
            .where(
                UserAttempt.user_id == user_id,
                Question.subject_id == subject.id,
            )
        )
        sub_row = sub_result.one_or_none()
        sub_total = sub_row.total if sub_row and sub_row.total else 0
        sub_correct = sub_row.correct if sub_row and sub_row.correct else 0

        if sub_total == 0:
            continue

        # Topic breakdown for this subject
        topic_stats = []
        topics = await db.execute(
            select(Topic).where(Topic.subject_id == subject.id)
        )
        for topic in topics.scalars().all():
            topic_result = await db.execute(
                select(
                    func.count(UserAttempt.id).label("total"),
                    func.sum(
                        case(
                            (UserAttempt.is_correct == True, 1),  # noqa: E712
                            else_=0,
                        )
                    ).label("correct"),
                )
                .join(Question, UserAttempt.question_id == Question.id)
                .where(
                    UserAttempt.user_id == user_id,
                    Question.topic_id == topic.id,
                )
            )
            t_row = topic_result.one_or_none()
            t_total = t_row.total if t_row and t_row.total else 0
            t_correct = t_row.correct if t_row and t_row.correct else 0

            if t_total > 0:
                topic_stats.append({
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "total": t_total,
                    "correct": t_correct,
                    "accuracy": round(t_correct / t_total, 4),
                })

        subject_stats.append({
            "subject_id": subject.id,
            "subject_name": subject.name,
            "total": sub_total,
            "correct": sub_correct,
            "accuracy": round(sub_correct / sub_total, 4) if sub_total > 0 else 0.0,
            "topics": topic_stats,
        })

    return {
        "user_id": user_id,
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "overall_accuracy": round(overall_accuracy, 4),
        "recent_accuracy": round(recent_accuracy, 4),
        "average_time": round(avg_time, 2),
        "subjects": subject_stats,
    }


async def update_weak_topics(db: AsyncSession, user_id: str) -> list[dict]:
    """Recalculate and update weak topics for a user."""
    analytics = await calculate_user_analytics(db, user_id)
    weak_topics = []

    for subject in analytics["subjects"]:
        for topic in subject["topics"]:
            if topic["total"] < 3:
                continue  # Not enough data

            accuracy = topic["accuracy"]
            # Weakness formula: (1 - accuracy) * recency_weight
            # Recency weight increases weakness for recently-attempted weak topics
            weakness_score = round((1.0 - accuracy) * 1.0, 4)

            if weakness_score > (1.0 - WEAKNESS_THRESHOLD):
                # Update or create weak topic entry
                existing = await db.execute(
                    select(WeakTopic).where(
                        WeakTopic.user_id == user_id,
                        WeakTopic.topic_id == topic["topic_id"],
                    )
                )
                weak = existing.scalar_one_or_none()
                if weak:
                    weak.weakness_score = weakness_score
                else:
                    weak = WeakTopic(
                        user_id=user_id,
                        topic_id=topic["topic_id"],
                        weakness_score=weakness_score,
                    )
                    db.add(weak)

                # Get topic details
                topic_obj = await db.get(Topic, topic["topic_id"])
                subject_obj = await db.get(Subject, subject["subject_id"])

                weak_topics.append({
                    "topic_id": topic["topic_id"],
                    "topic_name": topic["topic_name"],
                    "subject_name": subject["subject_name"],
                    "weakness_score": weakness_score,
                    "accuracy": accuracy,
                })

    # Remove topics that are no longer weak
    all_weak = await db.execute(
        select(WeakTopic).where(WeakTopic.user_id == user_id)
    )
    for wt in all_weak.scalars().all():
        is_still_weak = any(w["topic_id"] == wt.topic_id for w in weak_topics)
        if not is_still_weak:
            await db.delete(wt)

    await db.commit()
    return weak_topics


async def generate_adaptive_quiz(
    db: AsyncSession,
    user_id: str,
    count: int = 20,
    focus_weak: bool = True,
) -> dict:
    """Generate an adaptive quiz focusing on user's weak areas."""
    weak_topics = await update_weak_topics(db, user_id)
    questions = []
    focus_areas = []

    if focus_weak and weak_topics:
        # 70% questions from weak topics, 30% random
        weak_count = int(count * 0.7)
        random_count = count - weak_count

        # Sort by weakness score (highest first)
        weak_topics.sort(key=lambda x: x["weakness_score"], reverse=True)

        # Get questions from weak topics
        for wt in weak_topics[:5]:  # Top 5 weak topics
            per_topic = max(weak_count // min(len(weak_topics), 5), 2)
            topic_questions = await db.execute(
                select(Question)
                .where(Question.topic_id == wt["topic_id"])
                .order_by(func.random())
                .limit(per_topic)
            )
            questions.extend(topic_questions.scalars().all())
            focus_areas.append(f"{wt['subject_name']} - {wt['topic_name']}")

        # Fill remaining with random questions
        existing_ids = [q.id for q in questions]
        if existing_ids:
            random_q = await db.execute(
                select(Question)
                .where(Question.id.notin_(existing_ids))
                .order_by(func.random())
                .limit(random_count)
            )
        else:
            random_q = await db.execute(
                select(Question)
                .order_by(func.random())
                .limit(random_count)
            )
        questions.extend(random_q.scalars().all())
    else:
        # No weak topics or not focusing - get random questions
        result = await db.execute(
            select(Question).order_by(func.random()).limit(count)
        )
        questions = list(result.scalars().all())

    # Trim to exact count
    questions = questions[:count]

    return {
        "questions": [
            {
                "id": q.id,
                "subject_id": q.subject_id,
                "topic_id": q.topic_id,
                "question_text": q.question_text,
                "options": q.options,
                "difficulty": q.difficulty,
            }
            for q in questions
        ],
        "focus_areas": focus_areas,
    }
