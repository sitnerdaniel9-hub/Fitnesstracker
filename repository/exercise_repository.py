#Enthält die Persistenzoperationen für Exercises. Kapselt den Datenbankzugriff (CRUD) auf Exercise-Entitäten.

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.exercise import Exercise

class ExerciseRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, exercise: Exercise) -> Exercise:
        self.session.add(exercise)
        return exercise

    def find_by_id(self, exercise_id: int) -> Exercise | None:
        return self.session.get(Exercise, exercise_id)

    def find_by_name(self, name: str) -> Exercise | None:
        stmt = select(Exercise).where(Exercise.name == name)
        return self.session.scalars(stmt).first()

    def find_all(self) -> list[Exercise]:
        return self.session.scalars(select(Exercise).order_by(Exercise.id)).all()
