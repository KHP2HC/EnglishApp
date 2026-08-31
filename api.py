from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from data.database import get_session, engine, init_db
import data.models as models
from core.srs_engine import SRSEngine
from core.reading_test import load_tests, load_test, grade
from pydantic import BaseModel
import os

app = FastAPI(title="EnglishCoachPro API")

# ── CORS ──────────────────────────────────────────────
# Configurable allowed origins via environment variable.
# Development defaults allow common Vite dev/preview ports.
_default_origins = "http://localhost:5173,http://localhost:4173,http://localhost:8000"
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

class SRSRating(BaseModel):
    card_id: int
    quality: int

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/api/vocab/rate")
def rate_card(rating: SRSRating, db: Session = Depends(get_db)):
    progress = db.query(models.UserVocabularyProgress).filter(
        models.UserVocabularyProgress.id == rating.card_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Card progress not found")
        
    updated_progress = SRSEngine.update_card(progress, rating.quality)
    db.commit()
    db.refresh(updated_progress)
    return {"message": "Card updated successfully", "next_review": updated_progress.next_review_date}

@app.get("/api/reading/tests")
def get_reading_tests():
    tests = load_tests()
    return [{"id": t["id"], "title": t.get("title", "Practice Test")} for t in tests]

@app.get("/api/reading/test/{test_id}")
def get_reading_test(test_id: str):
    test = load_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

class ReadingAnswers(BaseModel):
    answers: dict

@app.post("/api/reading/test/{test_id}/grade")
def grade_reading_test(test_id: str, answers: ReadingAnswers):
    test = load_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    result = grade(test, answers.answers)
    return result

# ── Health Check ──────────────────────────────────────
@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}

# Mount the static frontend AFTER the API routes
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "EnglishCoachPro Web API is running (Frontend not found)"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)