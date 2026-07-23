from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .exercise import Exercise

class PlanExercise(Base):
    __tablename__ = "plan_exercises"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_index: Mapped[int] = mapped_column(nullable=False)
    targeted_weight: Mapped[float | None] = mapped_column(nullable=True)
    min_targeted_reps: Mapped[int | None] = mapped_column(nullable=True)
    max_targeted_reps: Mapped[int | None] = mapped_column(nullable=True)
    min_targeted_duration_time: Mapped[float | None] = mapped_column(nullable=True)
    max_targeted_duration_time: Mapped[float | None] = mapped_column(nullable=True)
    break_time: Mapped[float | None] = mapped_column(nullable=True)


    training_plan_id: Mapped[int] = mapped_column(
        ForeignKey("training_plans.id"),
        nullable=False
    )

    training_plan = relationship("TrainingPlan", back_populates="plan_exercises")

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"),
        nullable=False
    )

    exercise: Mapped[Exercise] = relationship("Exercise")


