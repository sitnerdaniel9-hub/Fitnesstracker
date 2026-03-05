from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime
from .base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .plan_exercise import PlanExercise

class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    plan_exercises: Mapped[list[PlanExercise]] = relationship(
        "PlanExercise",
        back_populates="training_plan",
        cascade="all, delete-orphan",
        order_by="PlanExercise.order_index",
    )