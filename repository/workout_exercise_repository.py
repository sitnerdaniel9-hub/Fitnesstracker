#Enthält Persistenzoperationen für WorkoutExercises, die direkt in der DB ausgewertet werden.

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.workout import Workout
from models.workout_exercise import WorkoutExercise
from models.workout_set import WorkoutSet

class WorkoutExerciseRepository:
    def __init__(self, session: Session):
        self.session = session

    #Liefert den besten Arbeitssatz (PR) für eine Exercise.
    #Höchstes Gewicht gewinnt; bei Gleichstand die höchste Wiederholungszahl, sonst die höchste Zeit.
    def find_pr_set_for_exercise(self, exercise_id: int) -> WorkoutSet | None:
        weight_score = func.coalesce(WorkoutSet.weight, -1.0)
        tie_score = func.coalesce(WorkoutSet.reps, WorkoutSet.duration_time, -1.0)

        stmt = (
            select(WorkoutSet)
            .join(WorkoutExercise, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
            .where(WorkoutExercise.exercise_id == exercise_id)
            .where(WorkoutSet.isWarmup == False)
            .order_by(weight_score.desc(), tie_score.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    #Liefert je abgeschlossenem Workout im Zeitraum das maximale Arbeitsgewicht für eine Exercise.
    def find_max_weight_points_for_exercise(
        self,
        exercise_id: int,
        start: datetime,
        end: datetime,
    ) -> list[tuple[datetime, float]]:
        stmt = (
            select(Workout.completed_at, func.max(WorkoutSet.weight))
            .join(WorkoutExercise, WorkoutExercise.workout_id == Workout.id)
            .join(WorkoutSet, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
            .where(WorkoutExercise.exercise_id == exercise_id)
            .where(WorkoutSet.isWarmup == False)
            .where(WorkoutSet.weight.is_not(None))
            .where(Workout.completed_at.is_not(None))
            .where(Workout.completed_at >= start)
            .where(Workout.completed_at <= end)
            .group_by(Workout.id, Workout.completed_at)
            .order_by(Workout.completed_at)
        )
        return list(self.session.execute(stmt).all())

    #Liefert je abgeschlossenem Workout die maximale Wiederholungszahl für eine Exercise in einer Gewichtsklasse.
    #weight=None -> nur Sets ohne Gewicht (Körpergewicht). Sonst wird auf 0.125 genau normalisiert verglichen.
    def find_best_reps_points_for_exercise(
        self,
        exercise_id: int,
        weight: float | None,
    ) -> list[tuple[datetime, int]]:
        stmt = (
            select(Workout.completed_at, func.max(WorkoutSet.reps))
            .join(WorkoutExercise, WorkoutExercise.workout_id == Workout.id)
            .join(WorkoutSet, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
            .where(WorkoutExercise.exercise_id == exercise_id)
            .where(WorkoutSet.isWarmup == False)
            .where(WorkoutSet.reps.is_not(None))
            .where(Workout.completed_at.is_not(None))
        )

        if weight is None:
            stmt = stmt.where(WorkoutSet.weight.is_(None))
        else:
            normalized_target = round(weight / 0.125) * 0.125
            normalized_weight = func.round(WorkoutSet.weight / 0.125) * 0.125
            stmt = stmt.where(WorkoutSet.weight.is_not(None)).where(normalized_weight == normalized_target)

        stmt = stmt.group_by(Workout.id, Workout.completed_at).order_by(Workout.completed_at)
        return list(self.session.execute(stmt).all())

    #Liefert je abgeschlossenem Workout die maximale Zeit für eine Exercise in einer Gewichtsklasse.
    #weight=None -> nur Sets ohne Gewicht (Körpergewicht). Sonst wird auf 0.125 genau normalisiert verglichen.
    def find_best_duration_points_for_exercise(
        self,
        exercise_id: int,
        weight: float | None,
    ) -> list[tuple[datetime, float]]:
        stmt = (
            select(Workout.completed_at, func.max(WorkoutSet.duration_time))
            .join(WorkoutExercise, WorkoutExercise.workout_id == Workout.id)
            .join(WorkoutSet, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
            .where(WorkoutExercise.exercise_id == exercise_id)
            .where(WorkoutSet.isWarmup == False)
            .where(WorkoutSet.duration_time.is_not(None))
            .where(Workout.completed_at.is_not(None))
        )

        if weight is None:
            stmt = stmt.where(WorkoutSet.weight.is_(None))
        else:
            normalized_target = round(weight / 0.125) * 0.125
            normalized_weight = func.round(WorkoutSet.weight / 0.125) * 0.125
            stmt = stmt.where(WorkoutSet.weight.is_not(None)).where(normalized_weight == normalized_target)

        stmt = stmt.group_by(Workout.id, Workout.completed_at).order_by(Workout.completed_at)
        return list(self.session.execute(stmt).all())
