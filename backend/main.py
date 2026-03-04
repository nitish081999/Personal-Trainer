from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db, init_db
from app.services.mining_engine import DailyMiningEngine
from app.services.adaptive_learning import AdaptiveLearningEngine
from app.models.schema import Subject, Topic
import threading

app = FastAPI(title="Personal Trainer AI Orchestrator API")

@app.on_event("startup")
def startup_event():
    init_db()
    # Mock some initial data for testing if DB is empty
    db = next(get_db())
    if not db.query(Subject).first():
        english = Subject(name="English")
        polity = Subject(name="Indian Polity")
        db.add_all([english, polity])
        db.commit()
        db.add(Topic(subject_id=polity.id, name="Parliament"))
        db.add(Topic(subject_id=polity.id, name="Constitution"))
        db.add(Topic(subject_id=english.id, name="Grammar"))
        db.commit()
    db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Personal Trainer API Orchestrator"}

@app.post("/mine/{subject}")
def trigger_mining(subject: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    engine = DailyMiningEngine(db)
    # Target count set to 10 for faster demonstration
    background_tasks.add_task(engine.mine_for_subject, subject, 10)
    return {"message": f"Mining triggered in background for {subject}"}

@app.get("/revision_test/{user_id}")
def get_revision_test(user_id: str, db: Session = Depends(get_db)):
    engine = AdaptiveLearningEngine(db)
    # Before test, update weakness score
    engine.calculate_weakness_score(user_id)
    test_questions = engine.generate_revision_test(user_id, total_questions=10)
    return {"questions": test_questions}
