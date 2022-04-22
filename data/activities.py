import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

class Activities(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'activities'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    n = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.String)
    breakfast = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    lunch = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    dinner = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    other_gains = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    lost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    note = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

