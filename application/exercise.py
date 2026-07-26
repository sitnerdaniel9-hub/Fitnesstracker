from sqlalchemy.orm import Session
from repository.exercise_repository import ExerciseRepository
from models.exercise import Exercise

#Sucht eine Exercise anhand ihres Namens
def find_exercise_by_name(session: Session, name: str) -> Exercise | None:
    repo = ExerciseRepository(session)
    exercise = repo.find_by_name(name)
    return exercise

#Sucht alle Exercises
def find_all_exercises(session: Session) -> list[Exercise]:
    repo = ExerciseRepository(session)
    return repo.find_all()

#Sucht eine Exercise anhand ihrer ID
def find_exercise_by_id(session: Session, exercise_id: int) -> Exercise | None:
    return ExerciseRepository(session).find_by_id(exercise_id)

#Legt eine neue Exercise an
def create_exercise(session: Session, name: str) -> Exercise:
    if not name or not name.strip():
        raise ValueError("name must not be empty")

    repo = ExerciseRepository(session)
    if repo.find_by_name(name) is not None:
        raise ValueError(f"exercise with name '{name}' already exists")

    try:
        exercise = repo.create(Exercise(name=name))
        session.commit()
        return exercise
    except Exception:
        session.rollback()
        raise

