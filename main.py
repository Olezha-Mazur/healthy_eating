from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, url_for
from data import db_session, activities_resources, users_resources
from data.users import User
from data.activities import Activities
from forms.user_forms import RegisterForm, LoginForm, DetailsForm, DayForm
from forms.activities import ActivityForm, ProfileForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from matplotlib import pyplot

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
        db_sess.commit()
        return redirect('/')
    return render_template('details.html', form=form)


@app.route("/change_details/<int:id>", methods=['GET', 'POST'])
def change_details(id):
    form = DetailsForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        usr = db_sess.query(User).get(current_user.id)
        if usr:
            print(usr.age)
            form.age.data = usr.age
            form.weight.data = usr.weight
            form.height.data = usr.height
            form.gender.data = usr.gender
        else:
            print(1)
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        usr = db_sess.query(User).get(current_user.id)
        usr.age = form.age.data
        usr.weight = form.weight.data
        usr.height = form.height.data
        usr.gender = form.gender.data
        db_sess.commit()
        return redirect(f'/profile/{current_user.id}')
    return render_template('details.html', form=form, title='Изменение информации')


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


@app.route('/week', methods=['GET'])
@login_required
def week():
    db_sess = db_session.create_session()
    uw = current_user.get_week()
    title = 'Неделя #' + str(uw[0])
    names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    week = uw[1]
    day_total = []
    for day in week:
        gain = day.breakfast + day.lunch + day.dinner + day.other_gains
        day_total.append(gain - day.lost)
    week = [[str(x.id), names[i], str(day_total[i])] for i, x in enumerate(week)]
    graph_file = 'out.png'
    pyplot.title('Калории за дни недели')
    pyplot.xlabel('Дни')
    pyplot.ylabel('Калории')
    pyplot.xticks(range(len(day_total)), names)
    pyplot.bar(range(len(day_total)), day_total)
    pyplot.savefig('static/' + graph_file)
    return render_template('week.html', graph_file=graph_file, week=week, title=title,
                           style=url_for('static', filename=f'css/week.css'))


@app.route('/day/<int:id>', methods=['GET', 'POST'])
@login_required
def day_edit(id):
    db_sess = db_session.create_session()
    day = db_sess.query(Activities).get(id)
    form = DayForm()
    if form.validate_on_submit():
        day.breakfast = form.breakfast.data
        day.lunch = form.lunch.data
        day.dinner = form.dinner.data
        day.other_gains = form.other_gains.data
        day.lost = form.lost.data
        day.note = form.note.data
        db_sess.merge(day)
        db_sess.commit()
        return redirect('/week')
    form.breakfast.data = day.breakfast
    form.lunch.data = day.lunch
    form.dinner.data = day.dinner
    form.other_gains.data = day.other_gains
    form.lost.data = day.lost
    form.note.data = day.note
    return render_template('day_edit.html', form=form, week=current_user.get_week())


@app.route('/profile/<id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    db_sess = db_session.create_session()
    form = activities = db_sess.query(User).filter(User.id == id,
                                                   ).first()
    if request.method == 'POST':
        f = request.files['file']
        with open(f'static/img/{current_user.id}.jpg', mode='wb') as g:
            g.write(f.read())
    return render_template('profile.html', title='Profile',
                           form=form, method=request.method)


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
