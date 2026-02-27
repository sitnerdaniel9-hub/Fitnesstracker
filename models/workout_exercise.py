from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .workout_set import WorkoutSet
    from .plan_exercise import PlanExercise
    from .workout import Workout

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    order_index: Mapped[int] = mapped_column(nullable=False)
    plan_exercise_id: Mapped[int | None] = mapped_column(
        ForeignKey("plan_exercises.id"),
        nullable=True
    )
    plan_exercise: Mapped[PlanExercise] = relationship(
        "PlanExercise"
    )
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id"),
        nullable=False
    )
    workout = relationship("Workout", back_populates="workout_exercises")

    sets: Mapped[list[WorkoutSet]] = relationship(
        "WorkoutSet",
        back_populates="workout_exercise",
        cascade="all, delete-orphan"
    )