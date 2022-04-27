from flask import abort
from data import db_session
from data.activities import Activities
from flask import jsonify
from data.users import User
from flask_restful import reqparse, abort, Resource

day_parser = reqparse.RequestParser()
day_parser.add_argument('title', required=True)
day_parser.add_argument('content', required=True)
day_parser.add_argument('is_private', required=True, type=bool)
day_parser.add_argument('is_published', required=True, type=bool)
day_parser.add_argument('user_id', required=True, type=int)

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', required=True)
user_parser.add_argument('about', required=True)
user_parser.add_argument('email', required=True)
user_parser.add_argument('password', required=True)

# ('breakfast', 'dinner', 'lunch', 'other_gains', 'lost', 'note', 'user_id')

#/days/<int:day_id>
class DaysResource(Resource):
    def get(self, day_id):
        abort_if_day_not_found(day_id)
        session = db_session.create_session()
        days = session.query(Activities).get(day_id)
        return jsonify({'day': days.to_dict(
            only=('breakfast', 'dinner', 'lunch', 'other_gains', 'lost', 'note', 'user_id'))})

    def delete(self, activities_id):
        abort_if_day_not_found(activities_id)
        session = db_session.create_session()
        activities = session.query(Activities).get(activities_id)
        session.delete(activities)
        session.commit()
        return jsonify({'success': 'OK'})

class DaysListResource(Resource):
    def get(self, user_id):
        session = db_session.create_session()

        activities = session.query(Activities).all()
        return jsonify({'days': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in activities]})

    def post(self):
        args = day_parser.parse_args()
        session = db_session.create_session()
        activities = Activities(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_private=args['is_private']
        )
        session.add(activities)
        session.commit()
        return jsonify({'success': 'OK'})


def abort_if_day_not_found(activities_id):
    session = db_session.create_session()
    day = session.query(Activities).get(activities_id)
    if not day:
        abort(404, message=f"Day {day} not found")

#/users/<int:user_id>
class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('name', 'about', 'email'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'about', 'email')) for item in user]})

    def post(self):
        args = user_parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            about=args['about'],
            email=args['email'],
        )
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")

class WeeksResource(Resource):
    def get(self, user_id, week_off):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        week = user.get_week(week_off)[2]
        week = list(map(lambda x: x.to_dict(only=('breakfast', 'dinner', 'lunch', 'other_gains', 'lost', 'note')), week))
        return jsonify(week)

#/users/<int:user_id>/weeks
class WeeksListResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        weeks = [user.get_week(0)[2], user.get_week(1)[2]]
        for i, w in enumerate(weeks):
            weeks[i] = list(map(lambda x: x.to_dict(only=('breakfast', 'dinner', 'lunch', 'other_gains', 'lost', 'note')), w))
        return jsonify(weeks)