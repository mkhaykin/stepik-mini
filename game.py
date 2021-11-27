import time
from uuid import uuid4


class NoSuchSessionException(Exception):
    """no such session"""


class ErrorWorldParamException(Exception):
    """no valid params for world creation"""


class NoWorldException(Exception):
    """no such user"""


class Session:
    """ игровая сессия пользователя """
    def __init__(self):
        # self._session_id = None

        self._user_name = None
        self._user_timestamp = time.time()

        # данные лабиринта
        self._field_size_x = None
        self._field_size_y = None
        self._field_difficult = None
        self._field_exit_count = None
        self._field = []    # двумерная матрица

        # позиции игроков
        self._pos_hero = None
        self._ninja = False
        self._pos_ninja = None

    def get_session(self):
        return {'name': self._user_name,
                'height': self._field_size_y,
                'width': self._field_size_x,
                'difficult': self._field_difficult,
                'exit_count': self._field_exit_count,
                'ninja': self._ninja}

    def start_game(self, **kwargs):
        self._parse_params(**kwargs)
        self._field = [['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
         ['X', ' ', ' ', 'X', 'X', 'X', ' ', 'X'],
         ['X', ' ', ' ', 'X', 'X', 'X', ' ', 'X'],
         ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
         ['X', 'X', 'X', 'X', ' ', ' ', 'X', 'X'],
         ['X', 'X', 'X', ' ', 'X', ' ', 'X', 'X'],
         ['X', ' ', ' ', ' ', ' ', ' ', 'X', 'X'],
         ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
         ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X']]


    def _parse_params(self, **kwargs):
        self._user_name = kwargs['name']
        self._field_size_y = kwargs['height']
        self._field_size_x = kwargs['width']
        self._field_difficult = kwargs['difficult']
        self._field_exit_count = kwargs['exit_count']
        self._ninja = kwargs['ninja']
        print('я распарсил )))')


class Game:
    """ игра 'выход из лабиринта' """
    def __init__(self):
        self._sessions = dict()      # сессии пользователей

    def get_session(self, session_id: str) -> dict:
        """Возвращает все данные по указанной сессии.  при отсутствии выбрасывает исключение.
        """
        if session_id is None or session_id not in self._sessions:
            raise NoSuchSessionException

        session = self._sessions[session_id]
        return session.get_session()

    def new_session(self):
        """Возвращает ID новой сессии."""
        session_id = str(uuid4().hex)
        self._sessions[session_id] = Session()
        return session_id

    def new_game(self, session_id, **kwargs):
        if session_id is None or session_id not in self._sessions:
            raise NoSuchSessionException
        # заполняем параметры игры
        session = self._sessions[session_id]
        try:
            session.start_game(**kwargs)
        except LookupError as e:
            raise ErrorWorldParamException from None
        except Exception as e:
            print(e)

    def get_game(self, session_id):
        if session_id is None or session_id not in self._sessions:
            raise NoSuchSessionException
        session = self._sessions[session_id]
        try:
            game = session.get_game()
        except Exception as e:
            raise NoWorldException from None

        return game

    def get_status(self):
        return {'session': self._sessions}


if __name__ == "__main__":
    pass