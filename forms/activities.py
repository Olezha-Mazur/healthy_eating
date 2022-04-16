from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    date = StringField('Заголовок', validators=[DataRequired()])
    breakfast = TextAreaField("Завтрак")
    lunch = TextAreaField("Обед")
    dinner = TextAreaField("Ужин")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
