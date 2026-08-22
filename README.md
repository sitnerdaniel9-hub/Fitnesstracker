# Fitnesstracker – Backend

REST-API für einen persönlichen Fitness-Tracker: Übungen, Workouts,
Trainingspläne und Fortschritts-Analysen. Gebaut mit **FastAPI + SQLAlchemy +
SQLite**, ausgeliefert über Docker.

Dieses Repo enthält **nur das Backend**. Die dazugehörige App (React
Native / Expo) liegt hier:
**[Fitnesstracker-Frontend](https://github.com/sitnerdaniel9-hub/Fitnesstracker-Frontend)**

---

## Hier anfangen

Das Backend ist der Einstiegspunkt. Starte es **zuerst** – die App zeigt ohne
laufende API nichts an. Wenn das Backend läuft, geht es weiter im
[Frontend-Repo](https://github.com/sitnerdaniel9-hub/Fitnesstracker-Frontend).

---


## Architektur

Sauber geschichtet nach **Repository → Application → API**:

- **Repository-Layer** – Datenzugriff (SQLAlchemy), keine Geschäftslogik.
- **Application-Layer** – Geschäftslogik, Validierung, wirft `ValueError` bei
  fachlichen Fehlern.
- **API-Layer** – FastAPI-Router, dünn; globaler Exception-Handler übersetzt
  `ValueError` → HTTP 400 und `SQLAlchemyError` → HTTP 500.

CORS ist aktiviert, damit das Frontend im Web-Weg (Browser) die API
cross-origin erreichen kann.

---

## Setup für Reviewer

Es gibt ein eigenes Compose-File für das Review, das die API mit
**vorgeneriertem Seed-Datensatz** startet – so ist sofort etwas zu sehen, ohne
erst manuell Daten anzulegen.

> **Hinweis zu den Daten:** Das Setup startet mit einem festen Testdatensatz.
> Eigene Eingaben (geloggte Workouts, angelegte Übungen) sind während der
> laufenden Sitzung normal nutzbar, werden beim Neustart des Containers aber
> zurückgesetzt – jeder Start beginnt wieder mit dem Standard-Testset.

### 1. Repo klonen

```bash
git clone https://github.com/sitnerdaniel9-hub/Fitnesstracker.git
cd Fitnesstracker
```

### 2. Backend mit Seed-Daten starten

```bash
docker compose -f docker-compose.reviewer.yml up --build
```

Beim ersten Start wird das Image gebaut, die Seed-Daten werden angelegt und die
API startet auf **`http://localhost:8000`**.

### 3. Prüfen, dass es läuft

Am einfachsten die automatische API-Doku im Browser öffnen:

```
http://localhost:8000/docs
```

Kommt die Swagger-Oberfläche hoch, läuft das Backend. Alternativ per Terminal
ein Endpoint direkt testen:

```bash
curl http://localhost:8000/api/exercises
```

Das sollte JSON mit den Seed-Übungen zurückgeben.

### 4. Weiter zum Frontend

Sobald die API läuft, im
[Frontend-Repo](https://github.com/sitnerdaniel9-hub/Fitnesstracker-Frontend)
weitermachen (empfohlen: Web-Weg, `EXPO_PUBLIC_API_URL=http://localhost:8000`).

---

## API

Alle Endpoints liegen unter dem Prefix **`/api`**. Vollständige, interaktive
Übersicht mit allen Routen und Schemas:

```
http://localhost:8000/docs
```

Grobe Struktur:

- `/api/exercises` – Übungen (inkl. Fortschritts- und PR-Analysen)
- `/api/workouts` – Workouts mit Sätzen und Übungszuordnung
- `/api/training_plans` – Trainingspläne

---

## Stoppen

Backend stoppen:

```bash
docker compose -f docker-compose.reviewer.yml down
```

---

## Tech-Stack

- **FastAPI** (Python)
- **SQLAlchemy** ORM
- **SQLite** als Datenbank
- **Docker** / Docker Compose