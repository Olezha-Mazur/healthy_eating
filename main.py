from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, url_for
from data import db_session, activities_resources, users_resources
from data.users import User
from data.activities import Activities
from forms.user_forms import RegisterForm, LoginForm, DetailsForm
from forms.activities import ActivityForm, ProfileForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    bmr = 0
    if current_user.is_authenticated:
        if not current_user.entered_details:
            return redirect('/details')
        activities = db_sess.query(Activities).filter(
            (Activities.user == current_user) | (Activities.is_private is not True))
        cs = {
            'M': [66.5, 13.75, 5.003, 6.75],
            'F': [655.1, 9.563, 1.850, 4.676]
        }
        c = cs[current_user.gender]
        bmr = c[0] + c[1] * current_user.weight + c[2] * current_user.height - c[3] * current_user.age
    else:
        activities = db_sess.query(Activities).filter(Activities.is_private is not True)
    return render_template("index.html", activities=activities, bmr=bmr)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            entered_details=False,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/details')
    return render_template('register.html', form=form)


@app.route("/details", methods=['GET', 'POST'])
def details():
    if not current_user.is_authenticated:
        return redirect('/register')
    if current_user.entered_details:
        return redirect('/')
    form = DetailsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        usr = db_sess.query(User).get(current_user.id)
        usr.age = form.age.data
        usr.weight = form.weight.data
        usr.height = form.height.data
        usr.gender = form.gender.data
        usr.entered_details = True
        db_sess.add(usr)
        print(1)
        db_sess.commit()
        return redirect('/')
    return render_template('details.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/activities', methods=['GET', 'POST'])
@login_required
def add_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        activities = Activities()
        activities.date = form.date.data
        activities.breakfast = form.breakfast.data
        activities.lunch = form.lunch.data
        activities.dinner = form.dinner.data
        activities.is_private = form.is_private.data
        current_user.activities.append(activities)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('activities.html', title='Меню на день',
                           form=form)


@app.route('/activities/<int:id>', methods=['GET', 'POST'])
@login_required
def view_activity(id):
    form = ActivityForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        activities = db_sess.query(Activities).filter(Activities.id == id,
                                                      Activities.user == current_user
                                                      ).first()
        if activities:
            form.date.data = activities.date
            form.breakfast.data = activities.breakfast
            form.lunch.data = activities.lunch
            form.dinner.data = activities.dinner
            form.is_private.data = activities.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        activities = db_sess.query(Activities).filter(Activities.id == id,
                                                      Activities.user == current_user
                                                      ).first()
        activities.date = form.date.data
        activities.breakfast = form.breakfast.data
        activities.lunch = form.lunch.data
        activities.dinner = form.dinner.data
        activities.is_private = form.is_private.data
        print(form.breakfast.data)
        db_sess.commit()
        return redirect('/')
    return render_template('activities.html',
                           title='Редактирование меню',
                           form=form
                           )


@app.route('/activities_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_activity(id):
    db_sess = db_session.create_session()
    activity = db_sess.query(Activities).filter(Activities.id == id).first()
    db_sess.delete(activity)
    db_sess.commit()
    return redirect('/')


@app.route('/profile/<id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    db_sess = db_session.create_session()
    form = activities = db_sess.query(User).filter(User.id == id,
                                                   ).first()
    # if form.validate_on_submit():
    #     # db_sess = db_session.create_session()
    #     # current_user.name = form.username.data
    #     # current_user.about_me = form.about_me.data
    #     # db_sess.commit()
    #     # flash('Your changes have been saved.')
    #     return redirect(url_for('edit_profile'))
    # elif request.method == 'GET':
        # form.username.data = current_user.name
        # form.about_me.data = current_user.about_me
    return render_template('profile.html', title='Profile',
                           form=form)

api.add_resource(activities_resources.ActivitiesListResource, '/api/activities')
api.add_resource(activities_resources.ActivitiesResource, '/api/activities/<int:activities_id>')
api.add_resource(users_resources.UsersListResource, '/api/users')
api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')


def main():
    db_session.global_init("db/users.sqlite")
    app.run(host='0.0.0.0')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found!!!'}), 404)


if __name__ == '__main__':
    main()
