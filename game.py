from copy import deepcopy
import random


class TictactoeError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class Tictactoe(object):
    def __init__(self, board=None):
        if board is None:
            self.board = [0] * 9
        else:
            self.board = deepcopy(board)

    def allowed_moves(self):
        moves = []
        for i, v in enumerate(self.board):
            if v == 0:
                moves.append(i)
        return moves

    def put_at(self, at, mark):
        game = Tictactoe(self.board)
        if game.board[at] != 0:
            raise (TictactoeError("invalid put"))

        game.board[at] = mark
        return game

    def is_win(self, mark):
        win_patterns = [
                (0, 1, 2),
                (3, 4, 5),
                (6, 7, 8),
                (0, 3, 6),
                (1, 4, 7),
                (2, 5, 8),
                (0, 4, 8),
                (2, 4, 6)
        ]
        for pat in win_patterns:
            if self.board[pat[0]] == mark and self.board[pat[1]] == mark and self.board[pat[2]] == mark:
                return True
        return False

    def is_end(self):
        return self.is_win(1) or self.is_win(-1) or all(map(lambda x: x != 0, self.board))


class GameManager(object):
    def __init__(self, p1, p2):
        self.players = [p1, p2]

    def shuffle(self):
        random.shuffle(self.players)

    def start(self):
        self.game = Tictactoe()
        self.turn = 0
        self.mark = 1
        self.players[0].set_mark(1)
        self.players[1].set_mark(-1)

    def __turn_player(self):
        return self.players[self.turn % 2]

    def __another_player(self):
        return self.players[(self.turn + 1) % 2]

    def is_end(self):
        return self.game.is_end()

    def do_turn(self):
        action = self.__turn_player().next_action(self.game)
        new_state = self.game.put_at(action, self.mark)
        self.players[0].update(self.game, new_state)
        self.players[1].update(self.game, new_state)

        if new_state.is_win(self.__turn_player().get_mark()):
            self.__turn_player().win(new_state)
            self.__another_player().lose(new_state)
        elif new_state.is_end():
            self.__turn_player().draw(new_state)
            self.__another_player().draw(new_state)
        self.game = new_state
        self.turn += 1
        self.mark *= -1


class Agent(object):
    def __init__(self, alpha):
        self.values = {}
        self.alpha = alpha
        self.debug = False

    def set_mark(self, mark):
        self.mark = mark

    def get_mark(self):
        return self.mark

    def win(self, game):
        pass

    def lose(self, game):
        pass

    def draw(self, game):
        pass

    def next_action(self, game):
        game = self.__convert_game_for_me(game)
        moves = game.allowed_moves()
        _, next_move = self.__choice_next_move(game, moves)
        return next_move

    def update(self, state, new_state):
        state = self.__convert_game_for_me(state)
        new_state = self.__convert_game_for_me(new_state)

        best_next_value = 0
        if not new_state.is_end():
            moves = new_state.allowed_moves()
            best_next_value = max([self.__get_v(new_state.put_at(m, 1).board) for m in moves])

        reward = self.__get_reward(new_state)
        self.values[tuple(state.board)] = (1 - self.alpha) * self.__get_v(state.board) + self.alpha * (reward + best_next_value)

    def __convert_game_for_me(self, game):
        """
        covert game to my mark is 1
        """
        if self.mark == 1:
            return game
        new_board = []
        for mark in game.board:
            new_board.append(mark * -1)
        return Tictactoe(new_board)

    def __choice_next_move(self, game, next_moves):
        next_states = []
        for m in next_moves:
            next_state = game.put_at(m, 1)
            value = self.__get_v(next_state.board)
            next_states.append((m, next_state, value))
            if self.debug is True:
                print(m, value)
        random.shuffle(next_states)
        next_states.sort(key=lambda x: x[2], reverse=True)
        best_move = next_states[0][0]
        next_move = best_move
        if random.random() < 0.05:
            next_move = random.choice(next_states)[0]
        return best_move, next_move

    def __get_v(self, board):
        return self.values.get(tuple(board), 0)

    def __get_reward(self, game):
        r = 1
        if game.is_win(1):
            r = 100
        elif game.is_win(-1):
            r = -100
        if self.debug is True:
            print("reward: " + str(r))
        return r


def board_str(board):
    def f(x):
        if x[1] == 1:
            return 'o'
        elif x[1] == -1:
            return 'x'
        return str(x[0])
    return """
+-+-+-+
|{}|{}|{}|
+-+-+-+
|{}|{}|{}|
+-+-+-+
|{}|{}|{}|
+-+-+-+
    """.strip().format(*list(map(f, enumerate(board))))


class User(object):
    def __init__(self):
        pass

    def win(self, game):
        print("you win")
        print(board_str(game.board))

    def lose(self, game):
        print("you lose")
        print(board_str(game.board))

    def draw(self, game):
        print("draw")
        print(board_str(game.board))

    def set_mark(self, mark):
        print("You are {}".format('o' if mark == 1 else 'x'))
        self.mark = mark

    def get_mark(self):
        return self.mark

    def update(self, state, new_state):
        pass

    def next_action(self, game):
        allowed_moves = game.allowed_moves()
        while True:
            try:
                print(board_str(game.board))
                print("1...9")
                print(">", end="")
                at = int(input())
                if not (0 <= at < 9):
                    continue
                if at not in allowed_moves:
                    continue
                break
            except EOFError:
                pass
            except ValueError:
                pass
        return at
