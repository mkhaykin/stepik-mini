from typing import Optional
from flask_bootstrap import Bootstrap

import config
from forms import NewGameForm
from game import *

import uuid

from flask import Flask
from flask import redirect
from flask import url_for
from flask import render_template
from flask import make_response
from flask import request
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

# app = Flask(__name__)
app = Flask(__name__)
bootstrap = Bootstrap(app)  # test
app.config['SECRET_KEY'] = config.SECRET_KEY


the_game = Game()


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    # TODO drop
    print('-------')
    print(f'//index: method {request.method} args {request.args}')

    user_id = request.cookies.get('userID')
    try:
        # todo что-то криво ...
        user = the_game.get_user(user_id=user_id)
    except NoSuchUserException as e:
        print('NoSuchUserException')  # todo drop
        # generate new user id and set cookies
        user_id = the_game.new_user()
        resp = make_response(render_template('index.html'))
        resp.set_cookie('userID', user_id)
    except Exception as e:
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        resp = render_template('error.html', exception=e)
    else:
        # здесь проверяем наличие мира
        resp = render_template('index.html')

    return resp
    # return render_template('index.html')


@app.route('/new', methods=['GET', 'POST'])
@app.route('/new.html', methods=['GET', 'POST'])
def new():
    """Указываем параметры игры ...
    если пользователя нет, то сначала всегда на index.html
    """
    # TODO drop
    print('-------')
    print(f'//new: method {request.method} args {request.args}')

    user_id = request.cookies.get('userID')
    try:
        user = the_game.get_user(user_id=user_id)
    except NoSuchUserException as e:
        return redirect('/index', code=302, Response=None)
    except Exception as e:
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        return render_template('error.html', exception=e)
    else:
        form = NewGameForm()

        if request.form.get('btn_index') == 'Cancel':
            print('Cancel button')
            return render_template('index.html')
            return redirect('/index', code=302, Response=None)  # не работает
            pass  # do something
        elif request.form.get('btn_submit') == 'New game':
            print('Submit button')
            pass  # do something else
        else:
            pass  # unknown

        if form.validate_on_submit():  # request.method == 'POST' and
            name = form.name.data
            # email = form.email.data
            # message = form.message.data
            print(name)

        resp = render_template('new.html', form=form)

    # todo вот это убрать наверное. ...
    # try:
    #     world = the_game.get_world(user_id=user_id)
    # except NoSuchUserException as e:
    #     print('NoSuchUserException')  # todo drop
    #     resp = redirect('/index', code=302, Response=None)
    # except NoWorldException as e:
    #     print('NoWorldException')  # todo drop
    #     # TODO а надо??? какая-то чушь
    #     resp = make_response(render_template('new.html'))
    # except Exception as e:
    #     # перенаправление на страницу с ошибкой
    #     # используем render_template для сокрытия адреса
    #     resp = render_template('error.html', exception=e)
    # else:
    #     # TODO
    #     # заполняем параметрами мира поля ввода.
    #     # делаем предупреждение, что мир существует и мы его перезатрем.
    #     # делаем другие названия кнопок
    #     resp = redirect('/game', code=302, Response=None)
    #     # resp = make_response(render_template('game.html', world=world))

    return resp


@app.route('/game', methods=['GET', 'POST'])
@app.route('/game.html', methods=['GET', 'POST'])
def game():
    """Отправляем пользователя на игру,
    в случае Exception: это новый пользователь и его на стартовую (index.html)
    если пользователь есть, но игры у него пользователя нет, то на настройки (setup.html)
    """
    # TODO drop
    print('-------')
    print(f'//game: method {request.method} args {request.args}')

    user_id = request.cookies.get('userID')
    try:
        world = the_game.get_world(user_id)
    except NoSuchUserException as e:
        resp = redirect('/index', code=302, Response=None)
    except NoWorldException as e:
        resp = redirect('/new', code=302, Response=None)
    except Exception as e:
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        resp = render_template('error.html', exception=e)
    else:
        resp = make_response(render_template('game.html', world=world))
    return resp


@app.route('/<string:action>:<string:direction>/', methods=['GET'])
# @app.route('/<int:action><direction>/', methods=['GET'])
def step(action, direction):
    """ информация о состоянии объекта Game"""
    return f"action {action} direction {direction}"


@app.route('/status', methods=['GET', 'POST'])
@app.route('/status.html', methods=['GET', 'POST'])
def status():
    """ информация о состоянии объекта Game"""
    data = the_game.get_status()
    s = ''
    for key, value in data.items():
        s += f'{key}: \t {value}\n'
    # print(s)
    return "status \n" + s


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=True)
    # app.run(host='0.0.0.0', port=port, debug=False)
