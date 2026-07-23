from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime
from .base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plan_exercise import PlanExercise
    from .workout_exercise import WorkoutExercise

class Exercise(Base):
    __tablename__ = "exercises"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)