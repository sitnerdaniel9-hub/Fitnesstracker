import random
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from application.exercise import create_exercise
from application.training_plan import create_training_plan, add_plan_exercise
from application.workout import create_workout, add_workout_exercise
from application.inputs.plan_exercise_input import PlanExerciseInput
from application.inputs.workout_exercise_input import WorkoutExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput

engine = create_engine("sqlite:///fitness_tracker.db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Deterministisch, damit Auswertungen zwischen Seeds reproduzierbar bleiben.
random.seed(42)

WEEKS = 14                       
SESSION_HOUR = 18                
SESSION_DAYS = [0, 2, 4]         
SESSION_ORDER = ["Push", "Pull", "Legs"]
DELOAD_EVERY = 5                 


EXERCISES = {
    "kniebeuge":    dict(name="Kniebeuge (Test)",          kind="weight",   base=70.0, inc=2.5,  step=2.5,  sets=3, reps=(6, 10),  rest=150, target=85.0,  warmup=True),
    "kreuzheben":   dict(name="Kreuzheben (Test)",         kind="weight",   base=90.0, inc=2.5,  step=2.5,  sets=2, reps=(4, 6),   rest=180, target=105.0, warmup=True),
    "bankdruecken": dict(name="Bankdrücken (Test)",        kind="weight",   base=52.5, inc=1.25, step=1.25, sets=3, reps=(6, 10),  rest=150, target=65.0,  warmup=True),
    "schulterdr":   dict(name="Schulterdrücken (Test)",    kind="weight",   base=35.0, inc=1.0,  step=1.0,  sets=3, reps=(6, 10),  rest=120, target=45.0,  warmup=True),
    "rudern":       dict(name="Langhantelrudern (Test)",   kind="weight",   base=45.0, inc=1.25, step=1.25, sets=3, reps=(8, 12),  rest=120, target=55.0,  warmup=True),
    "bizeps":       dict(name="Bizepscurl (Test)",         kind="weight",   base=12.0, inc=0.5,  step=0.5,  sets=3, reps=(8, 12),  rest=90,  target=17.5,  warmup=False),
    "klimmzug":     dict(name="Klimmzug (Test)",           kind="bw_then_weighted", base_reps=5, sets=3, reps=(5, 10), rest=120),
    "dips":         dict(name="Dips (Test)",               kind="bw_reps",  base_reps=6, sets=3, reps=(6, 12), rest=120),
    "beinheben":    dict(name="Hängendes Beinheben (Test)", kind="bw_reps", base_reps=8, sets=3, reps=(8, 15), rest=90),
    "plank":        dict(name="Plank (Test)",              kind="duration", base_dur=30, sets=3, dur=(30, 90), rest=60),
}

SESSIONS = {
    "Push": ["bankdruecken", "schulterdr", "dips"],
    "Pull": ["kreuzheben", "rudern", "klimmzug", "bizeps"],
    "Legs": ["kniebeuge", "beinheben", "plank"],
}


def _round_to(value, step):
    return round(round(value / step) * step, 2)


def _working_weight(c, week):
    """Lineare Progression + Deload + etwas Rauschen, auf Hantelschritt gerundet."""
    w = c["base"] + c["inc"] * week
    if DELOAD_EVERY and week > 0 and week % DELOAD_EVERY == 0:
        w *= 0.9
    w += random.uniform(-c["step"], c["step"])
    return _round_to(max(w, c["step"]), c["step"])


def _working_reps(reps_range, i, n, week):
    """Wdh. innerhalb des Zielbereichs; letzter Satz etwas weniger (Ermüdung)."""
    lo, hi = reps_range
    bias = min(week / WEEKS, 1.0)
    target = lo + (hi - lo) * (0.4 + 0.6 * bias)
    r = int(round(target)) - (1 if i == n - 1 else 0)
    r += random.choice([-1, 0, 0, 0, 1])
    return max(lo - 1, min(hi, r))


def build_sets(key, week):
    """Erzeugt die WorkoutSetInput-Liste für eine Übung in einer bestimmten Woche."""
    c = EXERCISES[key]
    kind = c["kind"]
    n = c["sets"]
    sets = []

    if kind == "weight":
        top = _working_weight(c, week)
        if c.get("warmup"):
            for frac in (0.5, 0.75):
                wu = _round_to(top * frac, c["step"])
                if wu >= c["step"]:
                    sets.append(WorkoutSetInput(weight=wu, reps=8, duration_time=None, is_warmup=True))
        for i in range(n):
            sets.append(WorkoutSetInput(
                weight=top, reps=_working_reps(c["reps"], i, n, week),
                duration_time=None, is_warmup=False,
            ))

    elif kind == "bw_reps":
        base = c["base_reps"] + week // 3  # alle 3 Wochen +1 Wdh.
        for i in range(n):
            reps = max(1, base - i + random.choice([-1, 0, 0]))
            sets.append(WorkoutSetInput(weight=None, reps=reps, duration_time=None, is_warmup=False))

    elif kind == "bw_then_weighted":
        if week < 8:
            base = c["base_reps"] + week
            for i in range(n):
                sets.append(WorkoutSetInput(weight=None, reps=max(1, base - i),
                                            duration_time=None, is_warmup=False))
        else:
            added = _round_to(2.5 * (week - 7), 2.5)
            for i in range(n):
                sets.append(WorkoutSetInput(weight=added, reps=max(3, 8 - i),
                                            duration_time=None, is_warmup=False))

    elif kind == "duration":
        dur = min(c["dur"][1], c["base_dur"] + week * 4)
        for i in range(n):
            sets.append(WorkoutSetInput(weight=None, reps=None,
                                        duration_time=float(max(15, dur - i * 5)), is_warmup=False))

    return sets


def plan_input_for(key):
    c = EXERCISES[key]
    reps = c.get("reps")
    dur = c.get("dur")
    return PlanExerciseInput(
        exercise_id=ex[key].id,
        targeted_weight=c["target"] if c["kind"] == "weight" else None,
        min_targeted_reps=reps[0] if reps else None,
        max_targeted_reps=reps[1] if reps else None,
        min_duration_time=dur[0] if dur else None,
        max_duration_time=dur[1] if dur else None,
        rest_sec=float(c["rest"]),
    )


def seed():
    global ex
    ex = {key: create_exercise(session, c["name"]) for key, c in EXERCISES.items()}
    order = ["bankdruecken", "schulterdr", "dips", "kreuzheben",
             "rudern", "klimmzug", "bizeps", "kniebeuge", "beinheben"]
    plan = create_training_plan(session, "Push/Pull/Legs (Test)", [plan_input_for(k) for k in order])
    pe = {key: plan.plan_exercises[i] for i, key in enumerate(order)}
    pe["plank"] = add_plan_exercise(session, plan.id, plan_input_for("plank"))

    start = datetime.now().replace(hour=SESSION_HOUR, minute=0, second=0, microsecond=0)
    start -= timedelta(weeks=WEEKS)
    start -= timedelta(days=start.weekday())

    plan_workouts = 0
    for week in range(WEEKS):
        for day, sname in zip(SESSION_DAYS, SESSION_ORDER):
            started = start + timedelta(weeks=week, days=day)
            w = create_workout(session, f"{sname} · W{week + 1}",
                                training_plan_id=plan.id, started_at=started)
            for key in SESSIONS[sname]:
                add_workout_exercise(session, w.id, WorkoutExerciseInput(
                    exercise_id=ex[key].id,
                    plan_exercise_id=pe[key].id,
                    sets=build_sets(key, week),
                ))
            w.completed_at = started + timedelta(minutes=random.randint(50, 80))
            session.commit()
            plan_workouts += 1

    beinpresse = create_exercise(session, "Beinpresse (alt)")
    for week in (0, 1, 2):
        started = start + timedelta(weeks=week, days=5, hours=1)
        w = create_workout(session, f"Zusatz Beine · W{week + 1}",
                           training_plan_id=None, started_at=started)
        add_workout_exercise(session, w.id, WorkoutExerciseInput(
            exercise_id=beinpresse.id, plan_exercise_id=None,
            sets=[
                WorkoutSetInput(weight=120.0 + week * 10, reps=12, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=120.0 + week * 10, reps=10, duration_time=None, is_warmup=False),
            ],
        ))
        w.completed_at = started + timedelta(minutes=40)
        session.commit()

    if hasattr(beinpresse, "is_archived"):
        beinpresse.is_archived = True
        session.commit()
    else:
        print("Hinweis: 'is_archived' am Exercise-Modell nicht gefunden – Übung bleibt aktiv.")

    free_workouts = 3
    for i in range(2):
        started = start + timedelta(weeks=WEEKS - 2 + i, days=6, hours=1)  # Sonntag
        w = create_workout(session, f"Freies Training · Arme #{i + 1}",
                           training_plan_id=None, started_at=started)
        add_workout_exercise(session, w.id, WorkoutExerciseInput(
            exercise_id=ex["klimmzug"].id, plan_exercise_id=None,
            sets=[
                WorkoutSetInput(weight=None, reps=10 - i, duration_time=None, is_warmup=False),
                WorkoutSetInput(weight=None, reps=8 - i, duration_time=None, is_warmup=False),
            ],
        ))
        add_workout_exercise(session, w.id, WorkoutExerciseInput(
            exercise_id=ex["bizeps"].id, plan_exercise_id=None,
            sets=[WorkoutSetInput(weight=16.0 + i, reps=12, duration_time=None, is_warmup=False)],
        ))
        w.completed_at = started + timedelta(minutes=35)
        session.commit()
        free_workouts += 1

    running = create_workout(session, "Legs · läuft gerade",
                             training_plan_id=plan.id,
                             started_at=datetime.now() - timedelta(minutes=25))
    add_workout_exercise(session, running.id, WorkoutExerciseInput(
        exercise_id=ex["kniebeuge"].id, plan_exercise_id=pe["kniebeuge"].id,
        sets=[
            WorkoutSetInput(weight=60.0, reps=8, duration_time=None, is_warmup=True),
            WorkoutSetInput(weight=95.0, reps=6, duration_time=None, is_warmup=False),
        ],
    ))
    session.commit()

    total = plan_workouts + free_workouts + 1
    print("Seed abgeschlossen.")
    print(f"  Übungen:       {len(EXERCISES) + 1} (inkl. 1 archiviert)")
    print(f"  Trainingsplan: {plan.name} (id={plan.id}, {len(order) + 1} Planübungen)")
    print(f"  Workouts:      {total} gesamt "
          f"({plan_workouts} plangebunden, {free_workouts} planlos, 1 laufend)")
    print(f"  Zeitraum:      {WEEKS} Wochen, {len(SESSION_ORDER)}x/Woche")


if __name__ == "__main__":
    try:
        seed()
    finally:
        session.close()