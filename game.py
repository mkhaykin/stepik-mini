import time
from uuid import uuid4

class NoSuchUserException(Exception):
    """no such user"""


class NoWorldException(Exception):
    """no such user"""


class User:
    """ игровая сессия или пользователь """
    def __init__(self, name=None):
        assert type(name) is str or name is None

        session_id = str(uuid4().hex)
        self._id = session_id
        self._name = None
        self._timestamp = time.time()  # последнее обращение

    def __str__(self):
        return f'user id: "{self._id}" \nuser name: "{self._name}".'

    @property
    def name(self) -> str:
        self._timestamp = time.time()
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        assert type(value), "Ошибка: передана не строка."
        self._name = value



class Session:
    """ игровая сессия пользователя """
    def __init__(self):
        self._session_id = None

        self._user_name = ''
        self._user_timestamp = time.time()

        # данные лабиринта
        self._field_size_x = 0
        self._field_size_y = 0
        self._field = []    # двумерная матрица

        # позиции игроков
        self._pos_hero = (1, 1)
        self._pos_ninja = (-1, -1)


class Game:
    """ игра 'выход из лабиринта' """
    def __init__(self):
        self._sessions = dict()      # сессии пользователей

    def get_user(self, user_id):
        if user_id is None or user_id not in self._sessions:
            raise NoSuchUserException
        return self._sessions[user_id]

    def get_world(self, user_id):
        if user_id is None or user_id not in self._sessions:
            raise NoSuchUserException

        if not self._sessions[user_id]:
            # user with cookie and session send to game page
            raise NoWorldException
        else:
            return ['word']

    def new_user(self):
        user_id = str(uuid4().hex)
        self._sessions[user_id] = None
        return user_id

    def get_status(self):
        return {'session': self._sessions}


if __name__ == "__main__":
    user = User()
    user.name = 'mixa'
    print(user)