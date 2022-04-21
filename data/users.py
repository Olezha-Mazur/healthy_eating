import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from . import db_session
from .activities import Activities


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    weight = sqlalchemy.Column(sqlalchemy.Integer)
    height = sqlalchemy.Column(sqlalchemy.Integer)
    gender = sqlalchemy.Column(sqlalchemy.String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    entered_details = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    activities = orm.relation("Activities", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


    def get_week(self, back=0):
        year, weekn = (datetime.date.today() - datetime.timedelta(weeks=back)).isocalendar()[:2]
        week = []
        db_sess = db_session.create_session()
        for i in range(1, 8):
            n = f'{year}:{weekn}:{i}'
            day = db_sess.query(Activities).filter(Activities.user_id == self.id) \
                .filter(Activities.n == n).first()
            if day is None:
                day = Activities(
                    n = n,
                    breakfast = 0,
                    lunch = 0,
                    dinner = 0,
                    other_gains = 0,
                    lost = 0,
                    note = "",
                    user_id = self.id,
                )
                db_sess.add(day)
                db_sess.commit()
            week.append(day)

        return [weekn, week]
