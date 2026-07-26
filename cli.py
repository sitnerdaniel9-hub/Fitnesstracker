from datetime import datetime
from sqlalchemy.orm import Session

from application.analysis import (
    count_workouts_in_date_range,
    count_avg_workouts_per_week,
    get_pr_for_exercise,
    get_avg_weight_gain,
    get_avg_rep_increase,
    get_avg_time_increase,
)

from application.training_plan import (
    create_training_plan,
    get_all_training_plans,
    add_plan_exercise,
    remove_plan_exercise,
    rename_training_plan,
    toggle_training_plan_status,
    reorder_plan_exercise,
)

from application.exercise import create_exercise, find_exercise_by_name

from application.workout import (
    create_workout,
    get_workouts,
    get_workout,
    remove_workout,
    end_workout,
    add_workout_exercise,
    remove_workout_exercise,
    add_workout_set,
    remove_workout_set,
    save_as_training_plan,
)

from application.inputs.plan_exercise_input import PlanExerciseInput
from application.inputs.workout_set_input import WorkoutSetInput
from application.inputs.workout_exercise_input import WorkoutExerciseInput


# State
class AppState:
    def __init__(self):
        self.current_workout_id: int | None = None
        self.current_plan_id: int | None = None



# Helper
def parse_datetime(text: str) -> datetime | None:
    if not text.strip():
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        return datetime.strptime(text, "%Y-%m-%d")


def input_datetime(prompt: str):
    return parse_datetime(input(prompt))


def input_float(prompt: str):
    v = input(prompt)
    return float(v) if v else None


def input_int(prompt: str):
    v = input(prompt)
    return int(v) if v else None


def input_exercise_id(session: Session, prompt: str) -> int:
    name = input(prompt)
    exercise = find_exercise_by_name(session, name)
    if exercise is None:
        raise ValueError(f"Exercise '{name}' nicht gefunden")
    return exercise.id


def select_from_list(items, label_fn):
    if not items:
        print("Keine Einträge vorhanden")
        return None

    for i, item in enumerate(items, start=1):
        print(f"{i} - {label_fn(item)}")

    idx = int(input("Auswahl: "))
    return items[idx - 1]


# Anzeige Funktionen
def print_training_plan_detail(plan):
    print(f"\n=== Trainingsplan: {plan.name} (id={plan.id}, active={plan.active}) ===")

    if not plan.plan_exercises:
        print("Keine Exercises vorhanden")
        return

    for ex in sorted(plan.plan_exercises, key=lambda e: e.order_index):
        if ex.min_targeted_reps is not None:
            target = f"{ex.min_targeted_reps}-{ex.max_targeted_reps} reps"
        else:
            target = f"{ex.min_targeted_duration_time}-{ex.max_targeted_duration_time} sec"

        weight = f"{ex.targeted_weight}kg" if ex.targeted_weight is not None else "bodyweight"

        print(f"{ex.order_index}. [id={ex.id}] {ex.exercise.name} | {weight} | {target}")


def print_workout_detail(workout):
    print(f"\n=== Workout: {workout.name} (id={workout.id}) ===")
    print(f"Started: {workout.started_at} | Completed: {workout.completed_at}")

    if not workout.workout_exercises:
        print("Keine Exercises vorhanden")
        return

    for ex in workout.workout_exercises:
        print(f"\n[id={ex.id}] {ex.exercise.name}")

        if not ex.sets:
            print("   Keine Sets")
            continue

        for i, s in enumerate(ex.sets, start=1):
            if s.reps is not None:
                detail = f"{s.weight}kg x {s.reps}"
            else:
                detail = f"{s.weight}kg | {s.duration_time}s"

            warmup = " (Warmup)" if s.isWarmup else ""
            print(f"   Set {i} [id={s.id}]: {detail}{warmup}")



def print_training_plans_overview(plans):
    if not plans:
        print("Keine Trainingspläne vorhanden")
        return

    for p in plans:
        print(f"[id={p.id}] {p.name} (active={p.active}, {len(p.plan_exercises)} Exercises)")


def print_workouts_overview(workouts):
    if not workouts:
        print("Keine Workouts vorhanden")
        return

    for w in workouts:
        status = "abgeschlossen" if w.completed_at is not None else "läuft"
        print(f"[id={w.id}] {w.name} | gestartet: {w.started_at} | {status} | {len(w.workout_exercises)} Exercises")


# Auswahl
def select_workout(session: Session):
    workouts = get_workouts(session)
    return select_from_list(workouts, lambda w: f"{w.id} - {w.name}")


def select_training_plan(session: Session):
    plans = get_all_training_plans(session)
    return select_from_list(plans, lambda p: f"{p.id} - {p.name} (active={p.active})")


# Workout Menü
def workout_menu(session: Session, state: AppState):
    while True:
        print("\n=== Workout Menü ===")
        print(f"Aktiv: {state.current_workout_id}")
        print("1 Workout auswählen")
        print("2 Workout erstellen")
        print("3 Exercise hinzufügen")
        print("4 Exercise entfernen")
        print("5 Set hinzufügen")
        print("6 Set entfernen")
        print("7 Workout beenden")
        print("8 Workout löschen")
        print("9 Als Trainingsplan speichern")
        print("10 Alle Workouts anzeigen")
        print("0 Zurück")

        c = input("Auswahl: ")

        try:
            if c == "1":
                w = select_workout(session)
                if w:
                    state.current_workout_id = w.id
                    print_workout_detail(w)

            elif c == "2":
                name = input("Name: ")
                plan = select_training_plan(session)
                started = input_datetime("Startzeit: ")
                w = create_workout(session, name, plan.id if plan else None, started)
                state.current_workout_id = w.id
                print_workout_detail(w)

            elif c == "3":
                wid = state.current_workout_id
                sets = []
                while input("Set? y/n: ") == "y":
                    sets.append(
                        WorkoutSetInput(
                            weight=input_float("Weight: "),
                            reps=input_int("Reps: "),
                            duration_time=input_float("Duration: "),
                            is_warmup=(input("Warmup y/n: ") == "y"),
                        )
                    )

                ex = WorkoutExerciseInput(
                    exercise_id=input_exercise_id(session, "Exercise Name: "),
                    plan_exercise_id=input_int("PlanExercise ID: "),
                    sets=sets,
                )

                w = add_workout_exercise(session, wid, ex)
                print_workout_detail(w)

            elif c == "4":
                w = remove_workout_exercise(
                    session,
                    state.current_workout_id,
                    int(input("Exercise ID: "))
                )
                print_workout_detail(w)

            elif c == "5":
                wid = state.current_workout_id
                ex_id = int(input("Exercise ID: "))

                s = WorkoutSetInput(
                    weight=input_float("Weight: "),
                    reps=input_int("Reps: "),
                    duration_time=input_float("Duration: "),
                    is_warmup=(input("Warmup y/n: ") == "y"),
                )

                w = add_workout_set(session, wid, ex_id, s)
                print_workout_detail(w)

            elif c == "6":
                w = remove_workout_set(
                    session,
                    state.current_workout_id,
                    int(input("Exercise ID: ")),
                    int(input("Set ID: "))
                )
                print_workout_detail(w)

            elif c == "7":
                w = end_workout(session, state.current_workout_id)
                print_workout_detail(w)

            elif c == "8":
                remove_workout(session, state.current_workout_id)
                state.current_workout_id = None
                print("Workout gelöscht")

            elif c == "9":
                plan = save_as_training_plan(session, state.current_workout_id)
                print(f"Neuer Plan: {plan.id}")

            elif c == "10":
                print_workouts_overview(get_workouts(session))

            elif c == "0":
                return

        except Exception as e:
            print(f"Fehler: {e}")


# Trainingsplan Menü
def training_plan_menu(session: Session, state: AppState):
    while True:
        print("\n=== Trainingsplan Menü ===")
        print(f"Aktiv: {state.current_plan_id}")
        print("1 Plan auswählen")
        print("2 Plan erstellen")
        print("3 Exercise hinzufügen")
        print("4 Exercise entfernen")
        print("5 Umbenennen")
        print("6 Aktiv togglen")
        print("7 Reihenfolge ändern")
        print("8 Alle Pläne anzeigen")
        print("0 Zurück")

        c = input("Auswahl: ")

        try:
            if c == "1":
                p = select_training_plan(session)
                if p:
                    state.current_plan_id = p.id
                    print_training_plan_detail(p)

            elif c == "2":
                name = input("Name: ")
                plan = create_training_plan(session, name, [])
                state.current_plan_id = plan.id
                print_training_plan_detail(plan)

            elif c == "3":
                ex = PlanExerciseInput(
                    exercise_id=input_exercise_id(session, "Exercise Name: "),
                    targeted_weight=input_float("Weight: "),
                    min_targeted_reps=input_int("Min reps: "),
                    max_targeted_reps=input_int("Max reps: "),
                    min_duration_time=input_float("Min duration: "),
                    max_duration_time=input_float("Max duration: "),
                    rest_sec=input_float("Rest: "),
                )
                plan = add_plan_exercise(session, state.current_plan_id, ex)
                print_training_plan_detail(plan)

            elif c == "4":
                plan = remove_plan_exercise(
                    session,
                    state.current_plan_id,
                    int(input("Exercise ID: "))
                )
                print_training_plan_detail(plan)

            elif c == "5":
                plan = rename_training_plan(
                    session,
                    state.current_plan_id,
                    input("Name: ")
                )
                print_training_plan_detail(plan)

            elif c == "6":
                plan = toggle_training_plan_status(session, state.current_plan_id)
                print_training_plan_detail(plan)

            elif c == "7":
                plan = reorder_plan_exercise(
                    session,
                    state.current_plan_id,
                    int(input("Exercise ID: ")),
                    int(input("Neue Position: "))
                )
                print_training_plan_detail(plan)

            elif c == "8":
                print_training_plans_overview(get_all_training_plans(session))

            elif c == "0":
                return

        except Exception as e:
            print(f"Fehler: {e}")



# Analyse Menü
def analysis_menu(session: Session):
    while True:
        print("\n=== Analyse ===")
        print("1 Count Workouts")
        print("2 Avg/Woche")
        print("3 PR")
        print("4 Gewichtsentwicklung")
        print("5 Rep Entwicklung")
        print("6 Zeit Entwicklung")
        print("0 Zurück")

        c = input("Auswahl: ")

        try:
            if c == "1":
                print(count_workouts_in_date_range(session,
                    input_datetime("Start: "),
                    input_datetime("End: ")
                ))

            elif c == "2":
                print(count_avg_workouts_per_week(session,
                    input_datetime("Start: "),
                    input_datetime("End: ")
                ))

            elif c == "3":
                print(get_pr_for_exercise(session, int(input("Exercise ID: "))))

            elif c == "4":
                print(get_avg_weight_gain(session, int(input("Exercise ID: "))))

            elif c == "5":
                print(get_avg_rep_increase(session,
                    int(input("Exercise ID: ")),
                    input_float("Weight: ")
                ))

            elif c == "6":
                print(get_avg_time_increase(session,
                    int(input("Exercise ID: ")),
                    input_float("Weight: ")
                ))

            elif c == "0":
                return

        except Exception as e:
            print(f"Fehler: {e}")



# Main Menü
def run_cli(session: Session):
    state = AppState()

    while True:
        print("\n=== Hauptmenü ===")
        print("1 Workout Menü")
        print("2 Trainingsplan Menü")
        print("3 Analyse")
        print("4 Exercise anlegen")
        print("0 Exit")

        c = input("Auswahl: ")

        if c == "1":
            workout_menu(session, state)
        elif c == "2":
            training_plan_menu(session, state)
        elif c == "3":
            analysis_menu(session)
        elif c == "4":
            try:
                exercise = create_exercise(session, input("Name: "))
                print(f"Exercise angelegt: [id={exercise.id}] {exercise.name}")
            except Exception as e:
                print(f"Fehler: {e}")
        elif c == "0":
            break