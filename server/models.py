from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy import CheckConstraint, UniqueConstraint

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = 'exercises'

    __table_args__ = (
        UniqueConstraint('name', name='uq_exercise_name'),
        CheckConstraint("length(trim(name)) > 0", name='ck_exercise_name_not_blank'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='exercise',
        cascade='all, delete-orphan')
    workouts = association_proxy(
        'workout_exercises', 'workout',
        creator=lambda w: WorkoutExercise(workout=w))

    # Model validation
    @validates('name')
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError('Exercise name cannot be blank.')
        return value.strip()


class Workout(db.Model):
    __tablename__ = 'workouts'

    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Relationships
    workout_exercises = db.relationship(
        'WorkoutExercise', back_populates='workout',
        cascade='all, delete-orphan')
    exercises = association_proxy(
        'workout_exercises', 'exercise',
        creator=lambda e: WorkoutExercise(exercise=e))

    # Model validation
    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError('duration_minutes must be a positive integer.')
        return value


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    __table_args__ = (
        UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise'),
        CheckConstraint('reps IS NULL OR reps > 0', name='ck_reps_positive'),
        CheckConstraint('sets IS NULL OR sets > 0', name='ck_sets_positive'),
        CheckConstraint('duration_seconds IS NULL OR duration_seconds > 0',
                        name='ck_duration_positive'),
        CheckConstraint('reps IS NOT NULL OR duration_seconds IS NOT NULL',
                        name='ck_reps_or_duration'),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Relationships
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Model validation
    @validates('reps', 'sets', 'duration_seconds')
    def validate_positive(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(f'{key} must be positive.')
        return value