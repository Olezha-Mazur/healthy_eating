from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField, RadioField
from wtforms.fields import EmailField, BooleanField
from wtforms.validators import DataRequired, NumberRange


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class DetailsForm(FlaskForm):
    age = IntegerField('Возраст (лет)', validators=[DataRequired(), NumberRange(min=12,
                                                                          message="Вы должны быть 12 лет или старше")])
    gender = RadioField('Пол', choices=[('M', 'Мужской'), ('F', 'Женский'), ('O', 'Другой')], validators=[DataRequired()])
    height = IntegerField('Рост (см)', validators=[DataRequired(), NumberRange(min=0)])
    weight = IntegerField('Вес (кг)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Завершить")