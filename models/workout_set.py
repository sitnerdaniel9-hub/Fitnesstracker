from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from .base import Base

class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id: Mapped[int] = mapped_column(primary_key=True)
    weight: Mapped[float | None] = mapped_column(nullable=True)
    reps: Mapped[int | None] = mapped_column(nullable=True)
    duration_time: Mapped[float | None] = mapped_column(nullable=True)
    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id"),
        nullable=False
    )
    workout_exercise = relationship("WorkoutExercise", back_populates="sets")

