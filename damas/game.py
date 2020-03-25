from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from damas.settings import NUM_PIECES, NUM_ROWS, NUM_COLS

FWD_MOVES = np.array([[+1, -1], [+1, +1]], dtype=np.int8)
ALL_MOVES = np.array([[+1, -1], [+1, +1], [-1, -1], [-1, +1]], dtype=np.int8)


class Board:

    def __init__(self):
        self.values = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.int8)

    def __getitem__(self, pos: Tuple[int, int]) -> int:
        return self.values[pos]

    def __setitem__(self, pos: Tuple[int, int], value: int):
        self.values[pos] = value

    def copy(self) -> "Board":
        board = Board()
        board.values = self.values.copy()

        return board

    def add(self, pos: Tuple[int, int], value: int):
        self[pos] = value

    def start(self):
        for value in [+1, -1]:
            for i in range(NUM_PIECES):
                row = (2 * i) // NUM_COLS
                col = (2 * i) % NUM_COLS + row % 2
                if value < 0:
                    row = NUM_ROWS - 1 - row
                    col = NUM_COLS - 1 - col

                self.add((row, col), value)

    @staticmethod
    def _moves_to(pos_a: Tuple[int, int], value_a: int, length: int) -> np.ndarray:
        b = np.array(pos_a, dtype=np.int8)
        a = length * np.sign(value_a)

        if np.abs(value_a) == 1:
            positions = FWD_MOVES * a + b
        else:
            positions = ALL_MOVES * a + b

        valid = (positions[:, 0] >= 0) & (positions[:, 0] < NUM_ROWS) & \
                (positions[:, 1] >= 0) & (positions[:, 1] < NUM_COLS)

        return positions[valid]

    def _get_moves1_from(self, pos_a: Tuple[int, int]):
        value_a = self[pos_a]

        poss_b = Board._moves_to(pos_a, value_a, length=1)
        values_b = self[(poss_b[:, 0], poss_b[:, 1])]
        valid = values_b == 0
        moves1 = [(pos_a, tuple(xy)) for xy in poss_b[valid]]

        return moves1

    def _get_moves2_from(self, pos_a: Tuple[int, int]):
        value_a = self[pos_a]

        poss_b = Board._moves_to(pos_a, value_a, length=2)
        values_b = self[(poss_b[:, 0], poss_b[:, 1])]
        poss_c = (np.array(pos_a) + poss_b) // 2
        values_c = self[(poss_c[:, 0], poss_c[:, 1])]
        valid = (values_b == 0) & (value_a * values_c < 0)
        moves2 = [(pos_a, tuple(xy)) for xy in poss_b[valid]]

        return moves2

    def get_all_moves(self, player):
        poss_a = [tuple(xy) for xy in np.transpose(np.nonzero(self.values * player > 0))]

        moves2 = [m for pos_a in poss_a for m in self._get_moves2_from(pos_a)]
        if moves2:
            return moves2

        moves1 = [m for pos_a in poss_a for m in self._get_moves1_from(pos_a)]

        return moves1

    def move(self, player, move):
        pos_a, pos_b = move

        self[pos_a], self[pos_b] = 0, self[pos_a]

        more_moves = []
        if np.abs(pos_a[0] - pos_b[0]) == 2:
            pos_c = tuple((np.array(pos_a) + np.array(pos_b)) // 2)
            self[pos_c] = 0
            more_moves = self._get_moves2_from(pos_b)

        if (player == +1) and (pos_b[0] == NUM_ROWS - 1):
            self[pos_b] = +2

        if (player == -1) and (pos_b[0] == 0):
            self[pos_b] = -2

        return more_moves


class Player(ABC):

    def __init__(self, board: Board, player: int):
        self._board = board
        self._player = player

    @abstractmethod
    def choose_move(self, moves):
        pass


class Display(ABC):

    @abstractmethod
    def render_board(self, board: Board):
        pass

    @abstractmethod
    def notify(self, msg: str, confirm: bool):
        pass


def player_name(player):
    if player == +1:
        return "WHITES"
    else:
        return "BLACKS"


class Game:

    def __init__(self, board: Board, display: Display, player_w: Player, player_b: Player):
        self.board = board
        self.display = display
        self.player1 = player_w
        self.player2 = player_b
        self.turn = +1

    def _next_turn(self):
        self.turn *= -1

    def _ask_move(self, moves):
        player = self.player1 if self.turn == +1 else self.player2
        return player.choose_move(moves)

    def loop(self):
        self.display.render_board(self.board)

        possible_moves = self.board.get_all_moves(self.turn)
        while possible_moves:
            self.display.notify(f"TURN FOR {player_name(self.turn)}", confirm=False)

            move = self._ask_move(possible_moves)

            more_moves = self.board.move(self.turn, move)
            self.display.render_board(self.board)

            while more_moves:
                move = self._ask_move(more_moves)
                more_moves = self.board.move(self.turn, move)

                self.display.render_board(self.board)

            this_turn = player_name(self.turn)

            self._next_turn()
            possible_moves = self.board.get_all_moves(self.turn)

            if possible_moves:
                self.display.notify(f"END OF {this_turn} TURN - PRESS ANY KEY TO CONTINUE", confirm=True)
            else:
                self.display.notify(f"{this_turn} WIN - PRESS ANY KEY TO EXIT", confirm=True)
