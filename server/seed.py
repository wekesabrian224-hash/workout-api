#!/usr/bin/env python3

from datetime import date
from app import app
from models import *

with app.app_context():
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    squat = Exercise(name='Squat', category='Strength', equipment_needed=True)
    plank = Exercise(name='Plank', category='Core', equipment_needed=False)

    w1 = Workout(date=date(2025, 1, 15), duration_minutes=45, notes='Leg day')
    w2 = Workout(date=date(2025, 1, 17), duration_minutes=30, notes='Core day')

    db.session.add_all([
        WorkoutExercise(workout=w1, exercise=squat, sets=4, reps=10),
        WorkoutExercise(workout=w2, exercise=plank, sets=3, duration_seconds=60),
    ])
    db.session.commit()
    print("Done seeding!")