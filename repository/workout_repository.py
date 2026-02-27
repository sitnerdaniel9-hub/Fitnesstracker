from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.workout import Workout

class WorkoutRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, workout: Workout) -> Workout:
        self.session.add(workout)
        return workout
    
    def find_by_id(self, workout_id: int) -> Workout | None:
        return self.session.get(Workout, workout_id)
    
    def find_by_date(self, start: datetime, end: datetime) -> list[Workout]:
        stmt = select(Workout).where(Workout.started_at.between(start, end)).order_by(Workout.started_at.desc())
        return self.session.scalars(stmt).all()
    
    def find_all(self) -> list[Workout]:
        return self.session.scalars(select(Workout).order_by(Workout.started_at.desc())).all()
    
    def find_by_name(self, search: str) -> list[Workout]:
        stmt = select(Workout).where(Workout.name.ilike(f"%{search}%")).order_by(Workout.started_at.desc())
        return self.session.scalars(stmt).all()
    
    def find_by_training_plan_id(self, training_plan_id: int) -> list[Workout]:
        stmt = select(Workout).where(Workout.training_plan_id == training_plan_id).order_by(Workout.started_at.desc())
        return self.session.scalars(stmt).all()
    
    def update(self, workout: Workout) -> Workout:
        return workout
    
    def delete(self, workout: Workout) -> None:
        self.session.delete(workout)
