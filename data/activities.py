import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Activities(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'days'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    n = sqlalchemy.Column(sqlalchemy.String)
    breakfast = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    dinner = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    supper = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    other_gains = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    lost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    note = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relation('User')
