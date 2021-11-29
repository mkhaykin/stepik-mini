import json
from typing import Optional
from flask_bootstrap import Bootstrap

from config import SECRET_KEY, PORT, COOKIE
from forms import NewGameForm
from game import *

import uuid

from flask import Flask
from flask import redirect
from flask import url_for
from flask import render_template
from flask import make_response
from flask import request
from flask import jsonify
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

# app = Flask(__name__)
app = Flask(__name__)
bootstrap = Bootstrap(app)  # test
app.config['SECRET_KEY'] = SECRET_KEY


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

    session_id = request.cookies.get(COOKIE)
    try:
        # здесь проверяем наличие сессии
        session_info = the_game.get_session(session_id=session_id)
        # здесь проверяем наличие мира
        game_info = the_game.get_game(session_id=session_id)
    except NoSuchSessionException as e:
        print('NoSuchSessionException exception')  # todo drop
        # generate new user id and set cookies
        session_id = the_game.new_session()
        resp = make_response(render_template('index.html'))
        resp.set_cookie(COOKIE, session_id)
    except NoWorldException as e:
        print('NoWorldException exception')  # todo drop
        resp = render_template('index.html', user_name='', game_run=False)
    except Exception as e:
        print('warning: an unhandled exception')  # !
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        resp = render_template('error.html', exception=e)
    else:
        # TODO drop
        print(session_info)
        print(game_info)
        game_run = True if game_info['labyrinth'] else False
        resp = render_template('index.html', user_name=session_info['name'], game_run=game_run)


    return resp


@app.route('/new', methods=['GET', 'POST'])
@app.route('/new.html', methods=['GET', 'POST'])
def new():
    """Указываем параметры игры ...
    если пользователя нет, то сначала всегда на index.html
    """
    # TODO drop
    print('-------')
    print(f'//new: method {request.method} args {request.args}')

    form = NewGameForm()

    session_id = request.cookies.get(COOKIE)
    try:
        _ = the_game.get_session(session_id=session_id)
        # если есть сессия, присваиваем старые значение полям.
        # TODO drop
        # form.name.data = 'test'
        # form.height.data = 20
        # form.width.data = 20
        # # form.difficult.data
        # form.exit_count.data = 5
        # form.ninja.data = True
    except NoSuchSessionException as e:
        return redirect('/index', code=302, Response=None)
    except Exception as e:
        print('warning: an unhandled exception')  # !
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        return render_template('error.html', exception=e)
    else:
        if request.form.get('btn_index') == 'Cancel':
            print('Cancel button')
            return render_template('index.html')
            # return redirect('/index', code=302, Response=None)  # не работает
        elif request.form.get('btn_submit') == 'New game':
            print('Submit button')
        else:
            pass  # unknown

        if form.validate_on_submit():  # request.method == 'POST' and
            # заполняем параметрами мира поля ввода.
            # делаем предупреждение, что мир существует и мы его перезатрем.
            # делаем другие названия кнопок
            try:
                the_game.new_game(session_id, **form.data)
            except NoSuchSessionException as e:
                return redirect('/index', code=302, Response=None)
            except Exception as e:
                # перенаправление на страницу с ошибкой
                # используем render_template для сокрытия адреса
                return render_template('error.html', exception=e)
            else:
                return redirect('/game', code=302, Response=None)

            # for item in form.data:
            #     print(item)
            # return redirect('/game', code=302, Response=None)  # не работает

        resp = render_template('new.html', form=form)

    return resp

# TODO логирование (тут и в heroku)
# https://logtail.com/tutorials/how-to-start-logging-with-heroku/


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
    # return render_template('game.html', world='qwe')

    session_id = request.cookies.get(COOKIE)
    try:
        _ = the_game.get_game(session_id)
    except NoSuchSessionException as e:
        resp = redirect('/index', code=302, Response=None)
    except NoWorldException as e:
        resp = redirect('/new', code=302, Response=None)
    except Exception as e:
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        resp = render_template('error.html', exception=e)
    else:
        resp = render_template('game.html')
    return resp


@app.route('/state', methods=['GET'])
@app.route('/state.html', methods=['GET'])
def get_state():
    """ информация о состоянии объекта Game"""
    session_id = request.cookies.get(COOKIE)
    data = dict()
    try:
        data = the_game.get_game(session_id)
    except NoSuchSessionException as e:
        data['status'] = 'error'
        data['message'] = 'no session'
    except NoWorldException as e:
        data['status'] = 'error'
        data['message'] = 'no world'
    except Exception as e:
        data['status'] = 'error'
        data['message'] = str(e)
    else:
        data['status'] = 'ok'
        data['message'] = ''
    json_data = json.dumps(data)
    return jsonify(json_data), 200


@app.route('/<string:action>:<string:direction>/', methods=['GET'])
# @app.route('/<int:action><direction>/', methods=['GET'])
def step(action, direction):
    """ вызов хода игры"""
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
    app.run(host='0.0.0.0', port=PORT, debug=True)
    # app.run(host='0.0.0.0', port=port, debug=False)
