import json
from flask_bootstrap import Bootstrap

from config import SECRET_KEY, PORT, COOKIE
from forms import NewGameForm
from game import *


from flask import Flask
from flask import redirect
from flask import render_template
from flask import make_response
from flask import request
from flask import jsonify


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = SECRET_KEY


the_game = Game()


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    """Главная страница"""
    # TODO drop
    print('-------')
    print(f'//index: method {request.method} args {request.args}')

    session_id = request.cookies.get(COOKIE)
    try:
        # здесь проверяем наличие сессии
        session_info = the_game.get_session(session_id=session_id)
        # # здесь проверяем наличие мира
        # game_info = the_game.get_game(session_id=session_id)
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
        # print(game_info)
        resp = render_template('index.html',
                               user_name=session_info['name'],
                               game_run=(session_info['game_status'] == 'continue'))

    return resp


@app.route('/new', methods=['GET', 'POST'])
@app.route('/new.html', methods=['GET', 'POST'])
def new():
    """Параметры игры"""
    # TODO drop
    print('-------')
    print(f'//new: method {request.method} args {request.args}')

    session_id = request.cookies.get(COOKIE)
    try:
        # здесь проверяем наличие сессии
        session_info = the_game.get_session(session_id=session_id)
    except NoSuchSessionException as e:
        return redirect('/index', code=302, Response=None)
    except Exception as e:
        print('warning: an unhandled exception')  # !
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        return render_template('error.html', exception=e)

    form = NewGameForm()

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

    # присваиваем сессионные значение полям.
    form.name.data = session_info['name']
    form.height.data = session_info['height']
    form.width.data = session_info['width']
    form.difficult.data = session_info['difficult']
    form.exit_count.data = session_info['exit_count']
    form.ninja.data = session_info['ninja']

    # TODO drop
    form.name.data = 'qwe'
    form.height.data = '15'
    form.width.data = '25'
    form.difficult.data = 60
    form.exit_count.data = 10
    form.ninja.data = True

    return render_template('new.html',
                           form=form,
                           game_run=(session_info['game_status'] == 'continue'))


@app.route('/game', methods=['GET', 'POST'])
@app.route('/game.html', methods=['GET', 'POST'])
def game():
    """Собственно страницы игры."""
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
    """Информация о состоянии объекта Game.
    Фактические возвращается лабиринт с координатами.
    Используется для отрисовки без обновления страницы."""
    session_id = request.cookies.get(COOKIE)
    data = dict()
    try:
        data = the_game.get_game(session_id)
    except NoSuchSessionException as e:
        print('NoSuchSessionException exception')  # todo drop
        data['status'] = 'error'
        data['message'] = 'no session'
    except NoWorldException as e:
        print('NoWorldException exception')  # todo drop
        data['status'] = 'error'
        data['message'] = 'no world'
    except EndGameException:
        print('EndGameException exception')  # todo drop
        data['status'] = 'error'
        data['message'] = 'end game'
    except Exception as e:
        print(f'exception: {e}')  # todo drop
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
    """ вызов хода игры
    примечание: вызов надуманный (можно в один параметр передавать), но такое требование к проекту"""

    session_id = request.cookies.get(COOKIE)
    data = dict()
    try:
        data = the_game.next_move(session_id, action, direction)
    except NoSuchSessionException:
        print('NoSuchSessionException exception')  # todo drop
        # data['status'] = 'error'
        # data['message'] = 'no session'
    except NoWorldException:
        print('NoWorldException exception')  # todo drop
        # data['status'] = 'error'
        # data['message'] = 'no world'
    except EndGameException:
        print('EndGameException exception')  # todo drop
        # data['status'] = 'error'
        # data['message'] = 'end game'
    except Exception as e:
        print(e)
        # data['status'] = 'error'
        # data['message'] = str(e)
    else:
        pass
        # data['status'] = 'ok'
        # data['message'] = ''
    json_data = json.dumps(data)
    return jsonify(json_data), 200


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


# TODO логирование (тут и в heroku)
# https://logtail.com/tutorials/how-to-start-logging-with-heroku/


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
    # app.run(host='0.0.0.0', port=port, debug=False)
