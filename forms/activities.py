from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class ActivityForm(FlaskForm):
    date = StringField('Заголовок', validators=[DataRequired()])
    breakfast = TextAreaField("Завтрак")
    lunch = TextAreaField("Обед")
    dinner = TextAreaField("Ужин")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')