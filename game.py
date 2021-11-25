from uuid import uuid4

class NoSuchUserException(Exception):
    """no such user"""


class NoWorldException(Exception):
    """no such user"""


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
