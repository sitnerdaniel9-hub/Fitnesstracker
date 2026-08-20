import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fitness_tracker.db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()