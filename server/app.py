from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# Schema objects (created once, reused in every route)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
workout_exercise_schema = WorkoutExerciseSchema()


# ---------- WORKOUTS ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(jsonify(workouts_schema.dump(workouts)), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)
    return make_response(jsonify(workout_schema.dump(workout)), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    try:
        data = workout_schema.load(request.get_json() or {})
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return make_response(jsonify({'errors': str(err)}), 400)
    return make_response(jsonify(workout_schema.dump(workout)), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)
    db.session.delete(workout)
    db.session.commit()
    return make_response(jsonify({'message': 'Workout deleted'}), 200)


# ---------- EXERCISES ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(jsonify(exercises_schema.dump(exercises)), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)
    data = exercise_schema.dump(exercise)
    data['workouts'] = workouts_schema.dump(
        [we.workout for we in exercise.workout_exercises])
    return make_response(jsonify(data), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json() or {})
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return make_response(jsonify({'errors': str(err)}), 400)
    return make_response(jsonify(exercise_schema.dump(exercise)), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)
    db.session.delete(exercise)
    db.session.commit()
    return make_response(jsonify({'message': 'Exercise deleted'}), 200)


# ----- ADD EXERCISE TO WORKOUT ----------

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
           methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if not workout or not exercise:
        return make_response(jsonify({'error': 'Workout or Exercise not found'}), 404)
    try:
        data = workout_exercise_schema.load(request.get_json() or {})
        we = WorkoutExercise(workout=workout, exercise=exercise, **data)
        db.session.add(we)
        db.session.commit()
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return make_response(jsonify({'errors': str(err)}), 400)
    return make_response(jsonify(workout_exercise_schema.dump(we)), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)