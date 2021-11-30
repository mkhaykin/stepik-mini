import json
import logging
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

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


the_game = Game()


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    # app.logger.debug('This is a DEBUG log record.')
    # app.logger.info('This is an INFO log record.')
    # app.logger.warning('This is a WARNING log record.')
    # app.logger.error('This is an ERROR log record.')
    # app.logger.critical('This is a CRITICAL log record.')

    """Главная страница"""
    session_id = request.cookies.get(COOKIE)
    try:
        # здесь проверяем наличие сессии
        session_info = the_game.get_session(session_id=session_id)
    except NoSuchSessionException:
        # новый пользователь: отправляем куки
        session_id = the_game.new_session()
        resp = make_response(render_template('index.html'))
        resp.set_cookie(COOKIE, session_id)
    except Exception as e:
        app.logger.error(f'An unhandled exception: {str(e)}')
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        resp = render_template('error.html', exception=e)
    else:
        resp = render_template('index.html',
                               user_name=session_info['name'],
                               game_run=(session_info['game_status'] == 'continue'))
    return resp


@app.route('/new', methods=['GET', 'POST'])
@app.route('/new.html', methods=['GET', 'POST'])
def new():
    """Параметры игры"""
    session_id = request.cookies.get(COOKIE)
    try:
        # здесь проверяем наличие сессии
        session_info = the_game.get_session(session_id=session_id)
    except NoSuchSessionException as e:
        # на главную, если сесии нет
        return redirect('/index', code=302, Response=None)
    except Exception as e:
        app.logger.error(f'An unhandled exception:\n\tclass "{e.__class__.__name__}"\n\tmessage {str(e)}')
        # перенаправление на страницу с ошибкой
        # используем render_template для сокрытия адреса
        return render_template('error.html', exception=e)

    form = NewGameForm()

    if form.validate_on_submit():
        # создаем игру из переданных параметров
        try:
            the_game.new_game(session_id, **form.data)
        except NoSuchSessionException as e:
            # на главную, если сесии нет
            return redirect('/index', code=302, Response=None)
        except WorldGenerateException as e:
            app.logger.warning(f'new game generate exception: {str(e)}')
            # TODO определиться куда идем
            return render_template('error.html', exception=e)
            # return redirect('/index', code=302, Response=None)
        except Exception as e:
            app.logger.error(f'An unhandled exception:\n\tclass "{e.__class__.__name__}"\n\tmessage {str(e)}')
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

    return render_template('new.html',
                           form=form,
                           game_run=(session_info['game_status'] == 'continue'))


@app.route('/game', methods=['GET', 'POST'])
@app.route('/game.html', methods=['GET', 'POST'])
def game():
    """Собственно страница игры."""

    session_id = request.cookies.get(COOKIE)
    try:
        _ = the_game.get_game(session_id)
    except NoSuchSessionException as e:
        resp = redirect('/index', code=302, Response=None)
    except Exception as e:
        app.logger.error(f'An unhandled exception:\n\tclass "{e.__class__.__name__}"\n\tmessage {str(e)}')
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
    # при обработке ошибок перенаправления нет, т.к. дергает JS
    # перенаправление в script.js
    # в теории мы не должны "дергать" отсутствующую сессию, но хероку засыпает, проверим ...
    except NoSuchSessionException as e:
        app.logger.warning('/state: NoSuchSessionException exception')
        data['status'] = 'error'
        data['message'] = 'Сессия истекла или не существовала.'
    except EndGameException:
        data['status'] = 'stop'
        data['message'] = 'Конец игры.'
    except Exception as e:
        app.logger.error(f'An unhandled exception:\n\tclass "{e.__class__.__name__}"\n\tmessage {str(e)}')
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
    """Вызов хода игры.
    Примечание: вызов надуманный (можно в один параметр передавать), но такое требование к проекту"""

    session_id = request.cookies.get(COOKIE)
    data = dict()
    try:
        data = the_game.next_move(session_id, action, direction)
    except NoSuchSessionException:
        print('NoSuchSessionException exception')  # todo drop
        # data['status'] = 'error'
        # data['message'] = 'no session'
    except EndGameException:
        print('EndGameException exception')  # todo drop
        # data['status'] = 'error'
        # data['message'] = 'end game'
    except NextStepParamException:
        # TODO write log
        # так-то надо крашиться, передают лажу (
        print('param')
        pass
    except NextStepWallException:
        print('wall')
        pass
    except Exception as e:
        app.logger.error(f'An unhandled exception:\n\tclass "{e.__class__.__name__}"\n\tmessage {str(e)}')
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
    # TODO возврат списка сессий и текущих ошибок
    data = the_game.get_status()
    s = ''
    for key, value in data.items():
        s += f'{key}: \t {value}\n'
    return "status \n" + s


# TODO логирование (тут и в heroku)
# https://logtail.com/tutorials/how-to-start-logging-with-heroku/


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
    # app.run(host='0.0.0.0', port=port, debug=False)
