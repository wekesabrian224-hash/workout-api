# Workout Tracker API

A backend API for personal trainers to track workouts and the exercises in them.
Built with Flask, SQLAlchemy and Marshmallow.

Each workout can include many exercises, with sets, reps or duration recorded for
each one. Exercises are reusable, so the same exercise can appear in many workouts.


## Setup

1. Clone the repo and enter the folder:
   git clone git@github.com:wekesabrian224-hash/workout-api.git
   cd workout-api
2. Install dependencies and activate the environment:
   pipenv install
   pipenv shell
3. Set up the database:
   cd server
   export FLASK_APP=app.py
   flask db upgrade head
4. Seed the sample data:
   python seed.py
5. Run the server:
   python app.py

The API runs at http://localhost:5555


## Models

- **Exercise**: id, name, category, equipment_needed
- **Workout**: id, date, duration_minutes, notes
- **WorkoutExercise** (join table): id, workout_id, exercise_id, reps, sets, duration_seconds

## Relationships

- A Workout has many WorkoutExercises, and an Exercise has many WorkoutExercises.
- A WorkoutExercise belongs to one Workout and one Exercise.
- Workouts and Exercises are many-to-many through WorkoutExercise.
- Deleting a Workout or Exercise also deletes its WorkoutExercise rows (cascade).


## Validations

**Table constraints** (database level)
- Exercise names are unique
- Workout duration_minutes must be greater than 0
- The same exercise cannot be added to the same workout twice

**Model validations** (SQLAlchemy `@validates`)
- Exercise name cannot be blank
- Workout duration_minutes must be positive
- reps, sets and duration_seconds must be positive when provided

**Schema validations** (Marshmallow)
- Exercise name length 1-100, category length 1-50, name cannot be only spaces
- Workout duration_minutes between 1 and 600
- reps, sets and duration_seconds must be at least 1
- A WorkoutExercise needs either reps or duration_seconds

## Endpoints

| Method | URL | Description |
|---|---|---|
| GET | /workouts | List all workouts |
| GET | /workouts/<id> | One workout with its exercises, reps, sets and duration |
| POST | /workouts | Create a workout |
| DELETE | /workouts/<id> | Delete a workout and its WorkoutExercises |
| GET | /exercises | List all exercises |
| GET | /exercises/<id> | One exercise with its workouts |
| POST | /exercises | Create an exercise |
| DELETE | /exercises/<id> | Delete an exercise and its WorkoutExercises |
| POST | /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises | Add an exercise to a workout |

### Example: create an exercise

POST /exercises
{"name": "Deadlift", "category": "Strength", "equipment_needed": true}

Response (201):
{"id": 5, "name": "Deadlift", "category": "Strength", "equipment_needed": true}

### Example: validation error

POST /workouts
{"date": "2025-02-01", "duration_minutes": -5}

Response (400):
{"errors": {"duration_minutes": ["Must be greater than or equal to 1 and less than or equal to 600."]}}

## Design decisions

- An exercise can appear only once per workout (unique constraint). To change
  sets or reps, a new workout entry is needed.
- reps, sets and duration are optional individually, but at least one of
  reps or duration is required at the schema level.
- duration_minutes is capped at 600 in the schema.
- Update actions and removing an exercise from a workout are out of scope (per the lab).
