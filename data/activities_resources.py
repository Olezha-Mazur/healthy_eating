from flask import abort
from data import db_session
from data.activities import Activities
from flask import jsonify
from flask_restful import reqparse, abort, Resource

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


class ActivitiesResource(Resource):
    def get(self, activities_id):
        abort_if_activities_not_found(activities_id)
        session = db_session.create_session()
        activities = session.query(Activities).get(activities_id)
        return jsonify({'activities': activities.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, activities_id):
        abort_if_activities_not_found(activities_id)
        session = db_session.create_session()
        activities = session.query(Activities).get(activities_id)
        session.delete(activities)
        session.commit()
        return jsonify({'success': 'OK'})


class ActivitiesListResource(Resource):
    def get(self):
        session = db_session.create_session()
        activities = session.query(Activities).all()
        return jsonify({'activities': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in activities]})

    def post(self):
        args = parser.parse_args()
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


def abort_if_activities_not_found(activities_id):
    session = db_session.create_session()
    activities = session.query(Activities).get(activities_id)
    if not activities:
        abort(404, message=f"Actitivties {activities_id} not found")
