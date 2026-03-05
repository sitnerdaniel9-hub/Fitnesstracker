from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .workout_exercise import WorkoutExercise
    from .training_plan import TrainingPlan

class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    training_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("training_plans.id"),
        nullable=True
    )
    training_plan: Mapped[TrainingPlan] = relationship(
        "TrainingPlan"
    )
    workout_exercises: Mapped[list[WorkoutExercise]] = relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order_index",
    )
    
