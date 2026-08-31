import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from .models import Base

DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data.db')
DB_URI = f"sqlite:///{DB_FILE}"

engine = create_engine(DB_URI, echo=False, future=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def migrate_schema():
    with engine.begin() as conn:
        inspector = inspect(conn)
        if "study_plans" in inspector.get_table_names():
            columns = {col["name"] for col in inspector.get_columns("study_plans")}
            if "week_start" not in columns:
                conn.execute(text("ALTER TABLE study_plans ADD COLUMN week_start DATE"))
            if "daily_tasks" not in columns:
                conn.execute(text("ALTER TABLE study_plans ADD COLUMN daily_tasks JSON"))
        if "users" in inspector.get_table_names():
            columns = {col["name"] for col in inspector.get_columns("users")}
            if "theme_mode" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN theme_mode VARCHAR(20) DEFAULT 'dark'"))
            if "daily_schedule" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN daily_schedule JSON"))
        if "study_sessions" in inspector.get_table_names():
            columns = {col["name"] for col in inspector.get_columns("study_sessions")}
            if "xp_earned" not in columns:
                conn.execute(text("ALTER TABLE study_sessions ADD COLUMN xp_earned INTEGER DEFAULT 0"))
            if "items_studied" not in columns:
                conn.execute(text("ALTER TABLE study_sessions ADD COLUMN items_studied INTEGER DEFAULT 0"))
            if "items_correct" not in columns:
                conn.execute(text("ALTER TABLE study_sessions ADD COLUMN items_correct INTEGER DEFAULT 0"))
        if "vocabulary_cards" in inspector.get_table_names():
            columns = {col["name"] for col in inspector.get_columns("vocabulary_cards")}
            if "synonym" not in columns:
                conn.execute(text("ALTER TABLE vocabulary_cards ADD COLUMN synonym VARCHAR(100)"))
            if "antonym" not in columns:
                conn.execute(text("ALTER TABLE vocabulary_cards ADD COLUMN antonym VARCHAR(100)"))


def init_db():
    Base.metadata.create_all(bind=engine)
    migrate_schema()


def get_session():
    return SessionLocal()
