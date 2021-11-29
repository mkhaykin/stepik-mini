import time
import requests
from uuid import uuid4


class NoSuchSessionException(Exception):
    """no such session"""


class NoWorldException(Exception):
    """no such user"""


class WorldParamException(Exception):
    """no valid params for world creation"""


class WorldGetException(Exception):
    """can't create labyrinth"""


class WorldGenerateException(Exception):
    """can't create labyrinth"""


class NoGameStatusException(Exception):
    """no such session"""


class NextStepParamException(Exception):
    """no valid params for next step"""


class NextStepWallException(Exception):
    """no valid params for next step"""


class EndGameException(Exception):
    """no valid params for next step"""


class Session:
    _char_blank = ' '
    _char_wall = 'X'

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
        self._step = 0
        self._pos_hero = None
        self._ninja = False
        self._pos_ninja = None

        # результат игры
        self._game_status = None
        self._game_result = None

    def __str__(self):
        return self._matrix_to_str(self._field)

    def get_session(self):
        return {'name': self._user_name,
                'height': self._field_size_y,
                'width': self._field_size_x,
                'difficult': self._field_difficult,
                'exit_count': self._field_exit_count,
                'ninja': self._ninja,
                'game_status': self._game_status,
                'game_result': self._game_result}

    def get_game(self):
        return {'height': self._field_size_y,
                'width': self._field_size_x,
                'labyrinth': self._field,
                'hero': self._pos_hero,
                'ninja': self._pos_ninja,
                'step': self._step,
                # для остановки
                'game_status': self._game_status,
                'game_result': self._game_result
                }

    def _parse_params(self, **kwargs):
        self._user_name = kwargs['name']
        self._field_size_y = kwargs['height']
        self._field_size_x = kwargs['width']
        self._field_difficult = kwargs['difficult']
        self._field_exit_count = kwargs['exit_count']
        self._ninja = kwargs['ninja']

        # TODO drop
        print('я распарсил )))')

    def start_game(self, **kwargs):

        self._parse_params(**kwargs)
        params = '&'.join([f'{param}={kwargs[param]}' for param in ('height', 'width', 'difficult', 'exit_count')])
        params += f'&char_blank="{self._char_blank}"&char_wall="{self._char_wall}"&borders=True'
        try:
            data = requests.get("http://labyrinths.herokuapp.com/get?" + params).json()
        except Exception as err:
            raise WorldGetException from None

        self._step = 0
        self._field = data['labyrinth']

        try:
            # устанавливаем позицию героя и противника
            # TODO сделать нормально
            self._pos_hero = self._get_near_position_for_char((self._field_size_x // 2, self._field_size_y // 2),
                                                              self._char_blank)
            if self._pos_hero == (-1, -1):
                # TODO ошибка генерации лабиринта
                raise Exception

            # устанавливаем позицию противника
            if kwargs['ninja']:
                self._pos_ninja = self._get_near_position_for_char((1, 1), self._char_blank)
                if self._pos_ninja == (-1, -1):
                    # TODO ошибка генерации лабиринта
                    raise Exception
            else:
                self._pos_ninja = (-1, -1)
        except Exception as err:
            self._step = None
            self._field = None
            raise WorldGetException from None

        # самыми последними
        self._game_status = 'continue'
        self._game_result = None

        # TODO drop
        print(self._field)

    def next_move(self, action, direction):
        if self._game_status != 'continue':
            raise EndGameException

        # ход охотника
        self._hero_move(action, direction)

        # ход охотника
        self._ninja_move()

        # check game result
        self._check_game_result()

        print(f"action: {action}. direction: {direction}")
        return {'action': 'success'}

    def _hero_move(self, action, direction):
        # NextStepWallException
        # NextStepEndGameException
        if action == 'move' and direction in ('up', 'down', 'left', 'right'):
            diff = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
            pos_new = tuple(map(lambda a, b: a + b, self._pos_hero, diff[direction]))
            if self._field[pos_new[1]][pos_new[0]] == self._char_blank:
                self._pos_hero = pos_new
                # если я на границе и нет рядом охотника, то выиграл!
                # если охотник рядом, то проиграл
            else:
                raise NextStepWallException
        elif action == 'action' and direction == 'sleep':
            pass
        else:
            raise NextStepParamException

    def _ninja_move(self):
        if self._pos_ninja == (-1, -1):
            return

        # считаем ходы от героя
        matrix = self._path_calc(self._pos_hero)
        # количество шагов от героя до охотника
        ninja_step = matrix[self._pos_ninja[1]][self._pos_ninja[0]]
        # выбираем любую точку с меньшим индексом из ближайших. отправляет туда охотника
        position = self._pos_ninja
        for pos in self._get_near_points(self._pos_ninja, 1):
            if self._field[pos[1]][pos[0]] == self._char_blank and matrix[pos[1]][pos[0]] < ninja_step:
                position = pos
                break
        self._pos_ninja = position

    def _check_game_result(self):
        # если дельта координат меньше или равна 1, то проиграл
        if abs(self._pos_ninja[0] - self._pos_hero[0]) + abs(self._pos_ninja[1] - self._pos_hero[1]) <= 1:
            self._game_status = 'end'
            self._game_result = 'lose'
            raise EndGameException
        # если герой на выходе, то выиграл
        elif self._pos_hero[0] in (0, self._field_size_x - 1) or self._pos_hero[1] in (0, self._field_size_y - 1):
            self._game_status = 'end'
            self._game_result = 'win'
            raise EndGameException

    @staticmethod
    def _get_diffs(distance: int) -> set:
        """
        Возвращает множество со сдвигом координат (относительно (0, 0)) на указанную дистанцию (количество ходов).
        Используется в _get_diffs.

        :param distance: количество шагов
        :return: кортеж кортежей
        """
        return set([(x, distance - x) for x in range(0, distance + 1)] +
                   [(x, x - distance) for x in range(0, distance + 1)] +
                   [(-x, distance - x) for x in range(0, distance + 1)] +
                   [(-x, x - distance) for x in range(0, distance + 1)])

    def _get_near(self, position, diffs):
        """
        Возвращает позиции на расстоянии смещения diffs с учетом размеров матрицы.
        Используется только в _get_near_points.

        :param position: позиция
        :param diffs: смещение
        :param size_x: размер матрицы по горизонтали
        :param size_y: размер матрицы по вертикали
        :param borders: True - возвращать позиции на границе. False - нет.
        :return:
        """
        size_x = self._field_size_x
        size_y = self._field_size_y

        return [(position[0] + diff[0], position[1] + diff[1])
                for diff in diffs
                if 0 < position[0] + diff[0] < (size_x - 1) and 0 < position[1] + diff[1] < (size_y - 1)]

    def _get_near_points(self, position: tuple, distance=1) -> list:
        """
        Возвращает множество ближайших к указанной в матрице matrix точке position на расстоянии distance.

        :param position: позиция с которой считать (x, y).
        :param distance: расстояние.
        :return: множество точек на расстоянии distance от position в matrix
        """

        if distance == 0:
            result = set(position)
        elif distance >= 1:
            result = set(self._get_near(position, self._get_diffs(distance)))
        else:
            raise ValueError("_get_near_points: не корректная дистанция.")
        return result

    def _get_near_position_for_char(self, position, char_find):
        """
        Поиск любой (первой попавшейся) ближайшей позиции со значением равным char_find к указанной position.
        Границы матрицы из поиска исключаются!
        В случае неудачи, возвращает (-1, -1)

        :param position: начиная с позиции (x, y)
        :param char_find: по какому символу ищем (пустые клетки или стены)
        :return: возвращает список ближайших точек к позиции
        """
        # проверка позиции
        if position[0] <= 0 or position[1] <= 0 or \
                position[0] >= self._field_size_x - 1 or \
                position[1] >= self._field_size_y - 1:
            raise ValueError("_find_near_position: не корректно передана стартовая позиция")
        if str(char_find).isdigit():
            raise ValueError("_find_near_position: символ поиска не может быть числом")

        # size_x = self._field_size_x
        # size_y = self._field_size_y

        distance = 0
        check_list = [position]
        while check_list:
            for pos in check_list:
                if self._field[pos[1]][pos[0]] == char_find:
                    return pos
            distance += 1
            check_list = self._get_near_points(position, distance)
        return -1, -1

    def _path_calc(self, position: tuple = (1, 1)) -> list:
        """
        Рассчет стоимости пути из точки: рассчитывается для всех ячеек сразу,
        position - координаты начала точки рассчета (если передана стена, выбирается ближайшая свободная),
        при отсутствии берется первая пустая: ближайшая пустая рядом с (1, 1).

        :param position: позиция с которой строятся пути
        :return: матрицу с путями
        :rtype: list
        """
        # на копии или premise
        matrix = [item.copy() for item in self._field]

        # возвращаем ближайшие свободные к переданной
        position = self._get_near_position_for_char(position, self._char_blank)
        if position == (-1, -1):
            raise Exception('_path_calc: не найти свободное поле.')

        # в стартовую ячейку 0 шаг, т.к. мы уже там
        step = 0
        matrix[position[1]][position[0]] = step
        # решение через очередь: начинаем со стартовой и далее
        # ищем близлежащие ячейки, берем не заполненные или с большей стоимостью пути
        # ставим им путь +1 и бросаем в очередь обсчета
        # список точек, которые надо обработать
        pos4proc = [(position[0], position[1])]
        size_x = len(matrix[0])
        size_y = len(matrix)

        while pos4proc:
            pos = pos4proc.pop(0)
            step = matrix[pos[1]][pos[0]] + 1
            near_list = self._get_near_points(pos, distance=1)

            # пробегаемся по координатам из near_list
            # если пусто или цифра, меньше step, то присваиваем step
            # и координаты запихиваем в очередь
            for (x, y) in near_list:
                if matrix[y][x] == self._char_blank or \
                        str(matrix[y][x]).isdigit() and matrix[y][x] > step:
                    matrix[y][x] = step
                    pos4proc.append((x, y))
        return matrix

    @staticmethod
    def _matrix_to_str(matrix: list) -> str:
        """
        Возвращает строку для представления двумерной матрицы.
        Используется для отладки и в .__str__

        :param matrix: матрица
        :return: строка для печати
        """
        size_x = len(matrix[0])
        s = '|' + '|'.join(map(lambda x: x.center(3, ' '), map(str, range(size_x)))) + '|\n'
        s += '+' + '-' * (size_x * 4 - 1) + '+\n'
        y = 0
        for line in matrix:
            s += '|' + '|'.join(map(lambda x: x.center(3, ' '), map(str, line))) + '|' + str(y) + '\n'
            y += 1
        s += '+' + '-' * (size_x * 4 - 1) + '+\n'
        return s


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
            raise WorldParamException from None
        except Exception as e:
            print(e)

    def next_move(self, session_id, action, direction):
        if session_id is None or session_id not in self._sessions:
            raise NoSuchSessionException
        session = self._sessions[session_id]
        session.next_move(action, direction)

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