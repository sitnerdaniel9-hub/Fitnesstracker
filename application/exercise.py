from sqlalchemy.orm import Session
from repository.exercise_repository import ExerciseRepository
from models.exercise import Exercise

#Sucht eine Exercise anhand ihres Namens
def find_exercise_by_name(session: Session, name: str) -> Exercise:
    repo = ExerciseRepository(session)
    exercise = repo.find_by_name(name)
    if exercise is None:
        raise ValueError(f"Exercise '{name}' not found")
    return exercise

#Legt eine neue Exercise an
def create_exercise(session: Session, name: str) -> Exercise:
    if not name or not name.strip():
        raise ValueError("name must not be empty")

    repo = ExerciseRepository(session)
    try:
        exercise = repo.create(Exercise(name=name))
        session.commit()
        return exercise
    except Exception:
        session.rollback()
        raise
