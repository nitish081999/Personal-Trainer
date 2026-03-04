"""Seed the database with initial subjects, topics, and sample questions."""
import hashlib
import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    Subject, Topic, Question, UserAttempt, WeakTopic, DailyMiningLog,
)
from app.services.mining_engine import SUBJECT_TOPICS

logger = logging.getLogger(__name__)


def _hash_question(text: str) -> str:
    normalized = text.strip().lower()
    normalized = " ".join(normalized.split())
    return hashlib.sha256(normalized.encode()).hexdigest()


SAMPLE_QUESTIONS = [
    {
        "subject": "Indian Polity",
        "topic": "Parliament",
        "questions": [
            {
                "question_text": "How many members can the President of India nominate to the Rajya Sabha?",
                "options": ["10", "12", "14", "16"],
                "correct_index": 1,
                "explanation": "The President can nominate 12 members to the Rajya Sabha from amongst persons having special knowledge in literature, science, art and social service.",
                "difficulty": "easy",
            },
            {
                "question_text": "What is the maximum strength of the Lok Sabha as provided by the Constitution?",
                "options": ["545", "550", "552", "555"],
                "correct_index": 2,
                "explanation": "Article 81 of the Constitution provides that the maximum strength of Lok Sabha shall be 552 (530 from states + 20 from UTs + 2 Anglo-Indians nominated).",
                "difficulty": "medium",
            },
            {
                "question_text": "A Money Bill can be introduced in which House of the Parliament?",
                "options": ["Rajya Sabha only", "Lok Sabha only", "Either House", "Joint Session"],
                "correct_index": 1,
                "explanation": "According to Article 109, a Money Bill can only be introduced in the Lok Sabha and not in the Rajya Sabha.",
                "difficulty": "easy",
            },
            {
                "question_text": "Who presides over the joint sitting of both Houses of Parliament?",
                "options": ["President of India", "Vice President", "Speaker of Lok Sabha", "Prime Minister"],
                "correct_index": 2,
                "explanation": "The Speaker of Lok Sabha presides over the joint sitting of both Houses of Parliament as provided under Article 108.",
                "difficulty": "medium",
            },
            {
                "question_text": "What is the quorum required to constitute a meeting of either House of Parliament?",
                "options": ["One-half of total members", "One-third of total members", "One-tenth of total members", "Two-thirds of total members"],
                "correct_index": 2,
                "explanation": "Article 100(3) states that the quorum to constitute a meeting of either House of Parliament is one-tenth of the total number of members of the House.",
                "difficulty": "hard",
            },
        ],
    },
    {
        "subject": "Geography",
        "topic": "Rivers and Lakes",
        "questions": [
            {
                "question_text": "Which is the longest river in India?",
                "options": ["Yamuna", "Ganga", "Godavari", "Brahmaputra"],
                "correct_index": 1,
                "explanation": "The Ganga is the longest river in India, flowing about 2,525 km from the Gangotri glacier to the Bay of Bengal.",
                "difficulty": "easy",
            },
            {
                "question_text": "The Chilika Lake is located in which state?",
                "options": ["Andhra Pradesh", "Odisha", "West Bengal", "Kerala"],
                "correct_index": 1,
                "explanation": "Chilika Lake is a brackish water lagoon located in Odisha. It is the largest coastal lagoon in India.",
                "difficulty": "easy",
            },
            {
                "question_text": "Which river is known as the 'Sorrow of Bihar'?",
                "options": ["Ganga", "Son", "Kosi", "Gandak"],
                "correct_index": 2,
                "explanation": "The Kosi River is known as the 'Sorrow of Bihar' because of its frequent devastating floods in the state.",
                "difficulty": "medium",
            },
        ],
    },
    {
        "subject": "Economics",
        "topic": "Banking and Finance",
        "questions": [
            {
                "question_text": "The Reserve Bank of India was established in which year?",
                "options": ["1930", "1935", "1940", "1947"],
                "correct_index": 1,
                "explanation": "The Reserve Bank of India was established on April 1, 1935, based on the recommendations of the Hilton Young Commission.",
                "difficulty": "easy",
            },
            {
                "question_text": "What does CRR stand for in banking terms?",
                "options": ["Cash Reserve Ratio", "Credit Reserve Ratio", "Capital Reserve Ratio", "Current Reserve Ratio"],
                "correct_index": 0,
                "explanation": "CRR stands for Cash Reserve Ratio, which is the percentage of deposits that banks must keep as reserves with the RBI.",
                "difficulty": "easy",
            },
            {
                "question_text": "Which committee recommended the establishment of Regional Rural Banks?",
                "options": ["Kelkar Committee", "Narasimham Committee", "Rangarajan Committee", "M. Narasimham Working Group"],
                "correct_index": 3,
                "explanation": "The M. Narasimham Working Group (1975) recommended the establishment of Regional Rural Banks to serve rural areas.",
                "difficulty": "hard",
            },
        ],
    },
    {
        "subject": "History",
        "topic": "Indian National Movement",
        "questions": [
            {
                "question_text": "Who started the Civil Disobedience Movement?",
                "options": ["Jawaharlal Nehru", "Mahatma Gandhi", "Subhas Chandra Bose", "Sardar Patel"],
                "correct_index": 1,
                "explanation": "Mahatma Gandhi started the Civil Disobedience Movement in 1930 with the famous Dandi March (Salt March).",
                "difficulty": "easy",
            },
            {
                "question_text": "The Indian National Congress was founded in which year?",
                "options": ["1880", "1885", "1890", "1895"],
                "correct_index": 1,
                "explanation": "The Indian National Congress was founded on 28 December 1885 by Allan Octavian Hume, Dadabhai Naoroji, and Dinshaw Wacha.",
                "difficulty": "easy",
            },
            {
                "question_text": "Who gave the slogan 'Do or Die'?",
                "options": ["Bhagat Singh", "Subhas Chandra Bose", "Mahatma Gandhi", "Bal Gangadhar Tilak"],
                "correct_index": 2,
                "explanation": "Mahatma Gandhi gave the slogan 'Do or Die' during the Quit India Movement in 1942.",
                "difficulty": "medium",
            },
        ],
    },
    {
        "subject": "English",
        "topic": "Synonyms and Antonyms",
        "questions": [
            {
                "question_text": "Choose the synonym of 'Benevolent':",
                "options": ["Cruel", "Kind", "Angry", "Lazy"],
                "correct_index": 1,
                "explanation": "'Benevolent' means well-meaning and kindly. 'Kind' is the closest synonym.",
                "difficulty": "easy",
            },
            {
                "question_text": "Choose the antonym of 'Verbose':",
                "options": ["Lengthy", "Concise", "Talkative", "Wordy"],
                "correct_index": 1,
                "explanation": "'Verbose' means using more words than needed. 'Concise' (brief and clear) is the antonym.",
                "difficulty": "medium",
            },
            {
                "question_text": "Choose the synonym of 'Ephemeral':",
                "options": ["Permanent", "Transient", "Eternal", "Durable"],
                "correct_index": 1,
                "explanation": "'Ephemeral' means lasting for a very short time. 'Transient' is the closest synonym.",
                "difficulty": "hard",
            },
        ],
    },
    {
        "subject": "Static GK",
        "topic": "Important Days and Dates",
        "questions": [
            {
                "question_text": "World Environment Day is observed on:",
                "options": ["June 5", "March 22", "April 22", "May 31"],
                "correct_index": 0,
                "explanation": "World Environment Day is observed on June 5 every year to raise awareness about environmental issues.",
                "difficulty": "easy",
            },
            {
                "question_text": "National Science Day in India is celebrated on:",
                "options": ["January 26", "February 28", "March 15", "August 15"],
                "correct_index": 1,
                "explanation": "National Science Day is celebrated on February 28 to mark the discovery of the Raman Effect by Sir C.V. Raman in 1928.",
                "difficulty": "medium",
            },
        ],
    },
]


async def seed_database(db: AsyncSession):
    """Seed the database with subjects, topics, and sample questions."""
    # Check if already seeded with the full set of subjects
    result = await db.execute(select(Subject))
    existing_subjects = result.scalars().all()
    expected_subject_count = len(SUBJECT_TOPICS)
    if len(existing_subjects) >= expected_subject_count:
        logger.info("Database already seeded with all subjects, skipping.")
        return

    # If partially seeded (stale data), clear and reseed
    if existing_subjects:
        logger.info(f"Found {len(existing_subjects)} subjects but expected {expected_subject_count}. Reseeding...")
        for model in [UserAttempt, WeakTopic, DailyMiningLog, Question, Topic, Subject]:
            await db.execute(delete(model))
        await db.commit()

    logger.info("Seeding database...")

    # Create subjects
    subjects_map: dict[str, Subject] = {}
    for subject_name in SUBJECT_TOPICS:
        subject = Subject(name=subject_name)
        db.add(subject)
        subjects_map[subject_name] = subject

    await db.flush()

    # Create topics
    topics_map: dict[str, dict[str, Topic]] = {}
    for subject_name, topic_list in SUBJECT_TOPICS.items():
        topics_map[subject_name] = {}
        for topic_name in topic_list:
            topic = Topic(
                subject_id=subjects_map[subject_name].id,
                name=topic_name,
            )
            db.add(topic)
            topics_map[subject_name][topic_name] = topic

    await db.flush()

    # Insert sample questions
    for sample in SAMPLE_QUESTIONS:
        subject_name = sample["subject"]
        topic_name = sample["topic"]
        subject = subjects_map.get(subject_name)
        topic = topics_map.get(subject_name, {}).get(topic_name)

        if not subject:
            continue

        for q_data in sample["questions"]:
            q_hash = _hash_question(q_data["question_text"])
            question = Question(
                subject_id=subject.id,
                topic_id=topic.id if topic else None,
                question_text=q_data["question_text"],
                options=q_data["options"],
                correct_index=q_data["correct_index"],
                explanation=q_data.get("explanation", ""),
                difficulty=q_data.get("difficulty", "medium"),
                source="seed",
                hash=q_hash,
            )
            db.add(question)

    await db.commit()
    logger.info("Database seeded successfully!")
