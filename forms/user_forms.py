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


class DayForm(FlaskForm):
    breakfast = IntegerField('Получено калорий за завтрак', validators=[NumberRange(min=0)])
    lunch = IntegerField('Получено калорий за обед', validators=[NumberRange(min=0)])
    dinner = IntegerField('Получено калорий за ужин', validators=[NumberRange(min=0)])
    other_gains = IntegerField('Получено калорий вне приёма пищи', validators=[NumberRange(min=0)])
    lost = IntegerField('Всего потрачено калорий за день', validators=[NumberRange(min=0)])
    note = StringField('Заметка (для планов)')
    submit = SubmitField('Сохранить')


class DetailsForm(FlaskForm):
    age = IntegerField('Возраст (лет)', validators=[DataRequired(), NumberRange(min=12,
                                                                          message="Вы должны быть 12 лет или старше")])
    gender = RadioField('Пол', choices=[('M', 'Мужской'), ('F', 'Женский'), ('O', 'Другой')], validators=[DataRequired()])
    height = IntegerField('Рост (см)', validators=[DataRequired(), NumberRange(min=0)])
    weight = IntegerField('Вес (кг)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Завершить")