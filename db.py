from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///fitness_tracker.db")
SessionLocal = sessionmaker(bind=engine)

def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
