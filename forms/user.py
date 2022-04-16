from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField
from wtforms.fields import EmailField, BooleanField
from wtforms.validators import DataRequired, NumberRange


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class DetailsForm(FlaskForm):
    age = IntegerField('Возраст', validators=[DataRequired(), NumberRange(min=12,
                                                                          message="Вы должны быть %(min) лет или старше")])
    gender = BooleanField('Пол', validators=[DataRequired()])
    height = IntegerField('Рост', validators=[DataRequired()])
    weight = IntegerField('Вес', validators=[DataRequired()])
