from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, JSON, Enum, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class ExamType(enum.Enum):
    TOEIC = "TOEIC"
    IELTS = "IELTS"
    TOEFL = "TOEFL"
    VSTEP = "VSTEP"

class BandLevel(enum.Enum):
    A1 = "A1"; A2 = "A2"; B1 = "B1"; B2 = "B2"; C1 = "C1"; C2 = "C2"

class SessionType(enum.Enum):
    VOCABULARY = "vocabulary"; GRAMMAR = "grammar"; LISTENING = "listening"
    READING = "reading"; WRITING = "writing"; SPEAKING = "speaking"; MOCK = "mock"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    avatar_emoji = Column(String(4), default="😊")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    target_exam = Column(Enum(ExamType))
    target_score = Column(Float)          # e.g. 7.5 for IELTS
    current_band = Column(Float)          # from placement test
    exam_date = Column(Date)
    daily_free_minutes = Column(JSON)     # {"mon": 60, "tue": 90, ...}
    daily_schedule = Column(JSON)         # {"mon": {"morning": 30, "afternoon": 20, "evening": 10}}
    preferred_session_time = Column(String(10))  # MORNING, AFTERNOON, EVENING
    theme_mode = Column(String(20), default="dark")  # dark, light, system
    
    streak_days = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    vocab_progress = relationship("UserVocabularyProgress", back_populates="user")
    sessions = relationship("StudySession", back_populates="user")
    errors = relationship("ErrorJournalEntry", back_populates="user")

class VocabularyCard(Base):
    __tablename__ = "vocabulary_cards"
    id = Column(Integer, primary_key=True)
    word = Column(String(100), unique=True, nullable=False)
    phonetic = Column(String(50))
    synonym = Column(String(100))
    antonym = Column(String(100))
    meaning_en = Column(Text)
    meaning_vi = Column(Text)
    example_sentence = Column(Text)
    audio_url = Column(String(200))
    image_url = Column(String(200))
    exam_type = Column(Enum(ExamType))     # which exam this word appears in
    difficulty_level = Column(Enum(BandLevel))
    category = Column(String(50))          # e.g., "business", "academic"

class UserVocabularyProgress(Base):
    __tablename__ = "user_vocab_progress"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    card_id = Column(Integer, ForeignKey("vocabulary_cards.id"))
    srs_interval = Column(Integer, default=1)       # days
    srs_easiness = Column(Float, default=2.5)
    srs_repetitions = Column(Integer, default=0)
    next_review_date = Column(Date)
    last_quality = Column(Integer)                  # 0-5
    times_seen = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    user = relationship("User", back_populates="vocab_progress")

class StudySession(Base):
    __tablename__ = 'study_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_type = Column(Enum(SessionType))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    score = Column(Float)
    xp_earned = Column(Integer, default=0)
    items_studied = Column(Integer, default=0)
    items_correct = Column(Integer, default=0)
    user = relationship('User', back_populates='sessions')


class ErrorJournalEntry(Base):
    __tablename__ = 'error_journal'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(Integer, ForeignKey('study_sessions.id'))
    error_category = Column(String(100))
    question_snapshot = Column(Text)
    user_answer = Column(Text)
    correct_answer = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='errors')


class StudyPlan(Base):
    __tablename__ = 'study_plans'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    week_start = Column(Date)
    daily_tasks = Column(JSON)
    plan = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentCache(Base):
    __tablename__ = 'content_cache'
    id = Column(Integer, primary_key=True)
    content_type = Column(String(50))
    source_url = Column(String(500))
    title = Column(String(300))
    body = Column(Text)
    difficulty_level = Column(String(20))
    fetched_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)