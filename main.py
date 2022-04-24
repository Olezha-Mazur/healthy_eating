import matplotlib.figure
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, url_for
from flask import Response
from data import db_session, apis
from data.users import User
from data.activities import Activities
from forms.user_forms import RegisterForm, LoginForm, DetailsForm, DayForm
from forms.activities import ActivityForm, ProfileForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, AnonymousUserMixin
from flask_restful import abort, Api
from matplotlib import pyplot
from io import StringIO

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
            return redirect('/details/'+str(current_user.id))
        activities = db_sess.query(Activities).filter(
            (Activities.user == current_user) | (Activities.is_private is not True))
        cs = {
            'M': [66.5, 13.75, 5.003, 6.75],
            'F': [655.1, 9.563, 1.850, 4.676],
            'O': [655.1, 9.563, 1.850, 4.676],
        }
        c = cs[current_user.gender]
        bmr = c[0] + c[1] * current_user.weight + c[2] * current_user.height - c[3] * current_user.age
    else:
        activities = db_sess.query(Activities).filter(Activities.is_private is not True)
    return render_template("index.html", activities=activities, bmr=bmr)

dynamic_data = {}
@app.route('/dynamic/<path>', methods=['GET'])
def dynamic(path):
    #with open('dynamic/'+path, 'rb') as f:
    #    return f.read()
    #return None
    if not path in dynamic_data:
        return None
    data = dynamic_data[path]
    return Response(data[0], mimetype=data[1])

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


@app.route("/details/<int:id>", methods=['GET', 'POST'])
def details(id):
    if not current_user.is_authenticated:
        return redirect('/register')
    form = DetailsForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    if user is None:
        return abort(404)
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
    return render_template('details.html', form=form, title='Изменение информации')


@app.route("/change_details/<int:id>", methods=['GET', 'POST'])
def change_details(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    if user is None:
        return abort(404)
    form = DetailsForm()
    if request.method == 'GET':
        if user:
            form.age.data = user.age
            form.weight.data = user.weight
            form.height.data = user.height
            form.gender.data = user.gender
        else:
            return abort(404)
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


@app.route('/week/<int:week_off>', methods=['GET'])
@login_required
def week(week_off):
    global dynamic_data
    if not current_user.entered_details:
        redirect('/details/' + str(current_user.id))
    week_off = max(0, min(1, week_off))
    uw = current_user.get_week(week_off)
    title = 'Неделя #' + str(uw[1]) + ', ' + str(uw[0])
    s_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    week_rel = 'Перейти к ' + ['прошлой', 'текущей'][week_off] + ' неделе'
    week = uw[2]
    day_total = []
    for day in week:
        gain = day.breakfast + day.lunch + day.dinner + day.other_gains
        day_total.append(gain - day.lost)
    week = [[str(x.id), names[i], str(day_total[i])] for i, x in enumerate(week)]
    graph_file = 'wg_' + str(current_user.id) + '.svg'
    data = StringIO()
    figure = matplotlib.figure.Figure()
    axis = figure.add_subplot(title='Недельная статистика')
    axis.set_xlabel('Дни')
    axis.set_ylabel('Калории')
    axis.set_xticks(range(len(day_total)), s_names)
    axis.bar(range(len(day_total)), day_total)
    figure.savefig(data, format='svg')
    data.seek(0)
    dynamic_data[graph_file] = [data.read(), 'image/svg+xml']
    data.close()
    return render_template('week.html', graph_file=graph_file, week=week, title=title, weekr=week_rel,
                           style=url_for('static', filename='css/week.css'), weeko=str(1 - week_off))


@app.route('/day/<int:id>', methods=['GET', 'POST'])
@login_required
def day_edit(id):
    db_sess = db_session.create_session()
    day = db_sess.query(Activities).get(id)
    if day.user_id != current_user.id:
        return redirect('/')
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
        return redirect('/week/0')
    form.breakfast.data = day.breakfast
    form.lunch.data = day.lunch
    form.dinner.data = day.dinner
    form.other_gains.data = day.other_gains
    form.lost.data = day.lost
    form.note.data = day.note
    return render_template('day_edit.html', form=form, week=current_user.get_week())


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id)
    if user is None:
        return abort(404)
    if current_user.is_anonymous:
        is_current = False
    else:
        is_current = id == current_user.id
    if is_current and request.method == 'POST':
        f = request.files['avatar']
        with open(f'static/img/avatar/{current_user.id}.jpg', mode='wb') as g:
            g.write(f.read())
            current_user.change_avatar(128)
    return render_template('profile.html', title='Profile', user=user, is_current=is_current)


api.add_resource(apis.DaysResource, '/api/days/<int:day_id>')
api.add_resource(apis.UsersResource, '/api/users/<int:user_id>')
api.add_resource(apis.WeeksResource, '/api/users/<int:user_id>/weeks/<int:week_off>')
api.add_resource(apis.WeeksListResource, '/api/users/<int:user_id>/weeks')


def main():
    db_session.global_init("db/users.sqlite")
    app.run(host='0.0.0.0')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found!!!'}), 404)


if __name__ == '__main__':
    main()
