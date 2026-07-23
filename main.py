from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from cli import run_cli

engine = create_engine("sqlite:///fitness_tracker.db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def main():
    session = SessionLocal()
    try:
        run_cli(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
