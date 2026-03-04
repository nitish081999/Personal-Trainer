import hashlib
import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Question, Subject, Topic, DailyMiningLog
from app.services.llm_router import llm_router, extract_json_from_response
from app.services.search_router import search_router

logger = logging.getLogger(__name__)

# Topic rotation mapping for daily mining
SUBJECT_TOPICS: dict[str, list[str]] = {
    "English": [
        "Synonyms and Antonyms", "Idioms and Phrases", "One Word Substitution",
        "Sentence Correction", "Error Spotting", "Fill in the Blanks",
        "Reading Comprehension", "Cloze Test", "Spelling Check",
        "Active and Passive Voice", "Direct and Indirect Speech",
    ],
    "Indian Polity": [
        "Parliament", "Constitution", "Federalism", "Fundamental Rights",
        "Directive Principles", "President and Vice President", "Prime Minister and Council",
        "Judiciary", "State Government", "Local Government",
        "Constitutional Amendments", "Emergency Provisions",
    ],
    "Geography": [
        "Physical Geography", "Indian Geography", "World Geography",
        "Rivers and Lakes", "Mountains and Plateaus", "Climate and Weather",
        "Soil Types", "Natural Resources", "Agriculture",
        "Indian States and Capitals", "Ocean Currents", "Volcanoes and Earthquakes",
    ],
    "Economics": [
        "Indian Economy", "Budget and Fiscal Policy", "Banking and Finance",
        "International Trade", "Inflation", "GDP and National Income",
        "Five Year Plans", "Poverty and Unemployment", "Agriculture Economics",
        "Industrial Policy", "Tax System", "Money and Credit",
    ],
    "History": [
        "Ancient India", "Medieval India", "Modern India",
        "Indian National Movement", "Mughal Empire", "British Rule",
        "World War I and II", "Indian Independence", "Post Independence India",
        "Maurya Empire", "Gupta Empire", "Delhi Sultanate",
    ],
    "Static GK": [
        "Important Days and Dates", "Awards and Honours",
        "Books and Authors", "Sports and Games", "Science and Technology",
        "First in India and World", "Inventions and Discoveries",
        "National Symbols", "International Organizations",
        "Indian Culture and Heritage", "Famous Personalities",
    ],
}


def _hash_question(text: str) -> str:
    """Create a hash of question text for deduplication."""
    normalized = text.strip().lower()
    # Remove extra whitespace
    normalized = " ".join(normalized.split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def _get_topic_for_day(subject_name: str, day_of_year: int) -> str:
    """Rotate topics daily for a subject."""
    topics = SUBJECT_TOPICS.get(subject_name, ["General"])
    return topics[day_of_year % len(topics)]


async def _generate_search_queries(subject: str, topic: str) -> list[str]:
    """Use LLM to generate search queries for mining."""
    prompt = f"""Generate 5 high-quality search queries for finding SSC exam-level MCQ questions on the following:
Subject: {subject}
Topic: {topic}

The queries should be specific enough to find educational content, practice questions, and study material.
Return ONLY a JSON array of strings, nothing else.

Example output:
["SSC CGL {subject} {topic} MCQ questions with answers", ...]"""

    result = await llm_router.generic_call(prompt)
    if result:
        parsed = extract_json_from_response(result)
        if isinstance(parsed, list):
            return [str(q) for q in parsed[:5]]

    # Fallback: generate queries manually
    return [
        f"SSC CGL {subject} {topic} MCQ questions with answers",
        f"SSC CHSL {subject} {topic} practice questions",
        f"{subject} {topic} competitive exam questions PDF",
        f"{topic} multiple choice questions for government exams",
        f"SSC {subject} {topic} previous year questions",
    ]


async def _extract_mcqs_from_content(
    content: str, subject: str, topic: str, count: int = 20
) -> list[dict]:
    """Use LLM to extract/generate MCQs from raw content."""
    system_prompt = """You are an expert SSC exam question creator. Extract or generate high-quality MCQs from the given content.
Each question must have exactly 4 options, one correct answer, and a brief explanation.
Return ONLY a valid JSON array."""

    prompt = f"""From the following content about {subject} - {topic}, extract or generate {count} high-quality MCQs suitable for SSC CGL/CHSL exam preparation.

Content:
{content[:3000]}

Return a JSON array where each item has:
- "question_text": the question
- "options": array of 4 options
- "correct_index": index of correct answer (0-3)
- "explanation": brief explanation of the answer
- "difficulty": "easy", "medium", or "hard"

IMPORTANT: Return ONLY the JSON array, no other text."""

    result = await llm_router.structure_json(prompt, system_prompt)
    if not result:
        return []

    parsed = extract_json_from_response(result)
    if not isinstance(parsed, list):
        return []

    # Validate each question
    valid_questions = []
    for q in parsed:
        if (
            isinstance(q, dict)
            and "question_text" in q
            and "options" in q
            and isinstance(q["options"], list)
            and len(q["options"]) == 4
            and "correct_index" in q
            and isinstance(q["correct_index"], int)
            and 0 <= q["correct_index"] <= 3
        ):
            valid_questions.append({
                "question_text": str(q["question_text"]),
                "options": [str(o) for o in q["options"]],
                "correct_index": q["correct_index"],
                "explanation": str(q.get("explanation", "")),
                "difficulty": str(q.get("difficulty", "medium")),
            })

    return valid_questions


async def _generate_synthetic_mcqs(
    subject: str, topic: str, count: int = 20
) -> list[dict]:
    """Generate questions purely from LLM when search APIs fail (Self-Healing Mode)."""
    system_prompt = """You are an expert SSC exam question creator. Generate original, high-quality MCQs.
Each question must have exactly 4 options, one correct answer, and a brief explanation.
Return ONLY a valid JSON array."""

    prompt = f"""Generate {count} original SSC-level MCQs on {subject} - {topic}.
Ensure no repetition. Vary difficulty levels.

Return a JSON array where each item has:
- "question_text": the question
- "options": array of 4 options
- "correct_index": index of correct answer (0-3)
- "explanation": brief explanation
- "difficulty": "easy", "medium", or "hard"

IMPORTANT: Return ONLY the JSON array."""

    result = await llm_router.generate_mcq(prompt, system_prompt)
    if not result:
        return []

    parsed = extract_json_from_response(result)
    if not isinstance(parsed, list):
        return []

    valid_questions = []
    for q in parsed:
        if (
            isinstance(q, dict)
            and "question_text" in q
            and "options" in q
            and isinstance(q["options"], list)
            and len(q["options"]) == 4
            and "correct_index" in q
            and isinstance(q["correct_index"], int)
            and 0 <= q["correct_index"] <= 3
        ):
            valid_questions.append({
                "question_text": str(q["question_text"]),
                "options": [str(o) for o in q["options"]],
                "correct_index": q["correct_index"],
                "explanation": str(q.get("explanation", "")),
                "difficulty": str(q.get("difficulty", "medium")),
                "source": "synthetic",
            })

    return valid_questions


async def mine_questions_for_subject(
    db: AsyncSession,
    subject_id: int,
    topic_name: Optional[str] = None,
    target_count: int = 20,
) -> dict:
    """
    Main mining function for a subject.
    Returns dict with mining results.
    """
    # Get subject
    subject = await db.get(Subject, subject_id)
    if not subject:
        return {"error": "Subject not found", "questions_added": 0}

    # Determine topic
    if not topic_name:
        day_of_year = datetime.utcnow().timetuple().tm_yday
        topic_name = _get_topic_for_day(subject.name, day_of_year)

    # Find or create topic
    topic_result = await db.execute(
        select(Topic).where(
            Topic.subject_id == subject_id,
            Topic.name == topic_name,
        )
    )
    topic = topic_result.scalar_one_or_none()
    if not topic:
        topic = Topic(subject_id=subject_id, name=topic_name)
        db.add(topic)
        await db.flush()

    # Create mining log
    mining_log = DailyMiningLog(
        subject_id=subject_id,
        status="running",
        api_used="",
    )
    db.add(mining_log)
    await db.flush()

    all_questions: list[dict] = []
    api_used_list: list[str] = []
    total_tokens = 0

    try:
        # Check if search APIs are available
        if not search_router.all_apis_exhausted():
            # Step 1: Generate search queries
            queries = await _generate_search_queries(subject.name, topic_name)

            # Step 2: Search and collect content
            all_content = ""
            for query in queries[:3]:  # Use top 3 queries
                results, api_name = await search_router.search(query, max_results=5)
                if results:
                    api_used_list.append(api_name)
                    for r in results:
                        all_content += f"\n{r.get('content', '')}\n"

                if len(all_content) > 5000:
                    break

            # Step 3: Extract MCQs from content
            if all_content.strip():
                extracted = await _extract_mcqs_from_content(
                    all_content, subject.name, topic_name, target_count
                )
                all_questions.extend(extracted)

        # Step 4: If not enough questions, switch to synthetic mode
        remaining = target_count - len(all_questions)
        if remaining > 0:
            logger.info(
                f"Switching to synthetic mode for {subject.name} - {topic_name} "
                f"(need {remaining} more questions)"
            )
            synthetic = await _generate_synthetic_mcqs(
                subject.name, topic_name, remaining
            )
            all_questions.extend(synthetic)
            if synthetic:
                api_used_list.append("synthetic")

        # Step 5: Deduplicate and insert
        questions_added = 0
        for q_data in all_questions:
            q_hash = _hash_question(q_data["question_text"])

            # Check for duplicate
            existing = await db.execute(
                select(Question).where(Question.hash == q_hash)
            )
            if existing.scalar_one_or_none():
                continue

            question = Question(
                subject_id=subject_id,
                topic_id=topic.id,
                question_text=q_data["question_text"],
                options=q_data["options"],
                correct_index=q_data["correct_index"],
                explanation=q_data.get("explanation", ""),
                difficulty=q_data.get("difficulty", "medium"),
                source=q_data.get("source", ", ".join(set(api_used_list))),
                hash=q_hash,
            )
            db.add(question)
            questions_added += 1

        # Update mining log
        mining_log.questions_added = questions_added
        mining_log.api_used = ", ".join(set(api_used_list)) if api_used_list else "none"
        mining_log.tokens_used = total_tokens
        mining_log.status = "completed"

        await db.commit()

        return {
            "subject": subject.name,
            "topic": topic_name,
            "questions_added": questions_added,
            "total_found": len(all_questions),
            "apis_used": list(set(api_used_list)),
            "status": "completed",
        }

    except Exception as e:
        logger.error(f"Mining error for {subject.name}: {e}")
        mining_log.status = "failed"
        await db.commit()
        return {
            "error": str(e),
            "questions_added": 0,
            "status": "failed",
        }
