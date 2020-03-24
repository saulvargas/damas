from abc import ABC, abstractmethod
from typing import List, Tuple

import numpy as np

from damas.settings import NUM_PIECES, NUM_ROWS, NUM_COLS


class Board:

    def __init__(self):
        self._cells = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.int8)

    def __getitem__(self, pos: Tuple[int, int]) -> int:
        return self._cells[pos]

    def __setitem__(self, pos: Tuple[int, int], value: int):
        self._cells[pos] = value

    def copy(self):
        board = Board()
        board._cells = self._cells.copy()

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

    def _get_moves_from(self, pos_a: Tuple[int, int]):
        jumps = []
        simples = []

        value_a = self[pos_a]

        def is_valid(pos: np.ndarray):
            row, col = pos
            return (row >= 0) and (row < NUM_ROWS) and (col >= 0) and (col < NUM_COLS)

        def moves_to(length: int) -> List[Tuple[int, int]]:
            xy = np.array(pos_a)
            fl = xy + np.array([+1, -1]) * length * np.sign(value_a)
            fr = xy + np.array([+1, +1]) * length * np.sign(value_a)
            bl = xy + np.array([-1, -1]) * length * np.sign(value_a)
            br = xy + np.array([-1, +1]) * length * np.sign(value_a)

            positions = [fl, fr]
            if np.abs(value_a) == 2:
                positions += [bl, br]

            return [tuple(pos_b) for pos_b in positions if is_valid(pos_b)]

        # check jump
        for pos_b in moves_to(length=2):
            value_b = self[pos_b]
            pos_c = tuple((np.array(pos_a) + np.array(pos_b)) // 2)
            value_c = self[pos_c]

            if (value_b == 0) and (value_a * value_c < 0):
                jumps.append((pos_a, pos_b))

        # check simple move
        for pos_b in moves_to(length=1):
            value_b = self[pos_b]

            if value_b == 0:
                simples.append((pos_a, pos_b))

        return jumps, simples

    def get_all_moves(self, player):
        jumps = []
        simples = []

        for xy in np.transpose(np.nonzero(self._cells * player > 0)):
            pos_a = tuple(xy)
            pos_jumps, pos_simples = self._get_moves_from(pos_a)
            jumps += pos_jumps
            simples += pos_simples

        if jumps:
            return jumps
        else:
            return simples

    def move(self, player, move):
        pos_a, pos_b = move

        value = self[pos_a]
        self[pos_a] = 0
        self[pos_b] = value

        more_moves = []
        if np.abs(pos_a[0] - pos_b[0]) == 2:
            pos_c = tuple((np.array(pos_a) + np.array(pos_b)) // 2)
            self[pos_c] = 0
            jumps, _ = self._get_moves_from(pos_b)

            more_moves = jumps

        if (player == +1) and (pos_b[0] == NUM_ROWS - 1):
            self[pos_b] = +2

        if (player == -1) and (pos_b[0] == 0):
            self[pos_b] = -2

        return more_moves


class Player(ABC):

    def __init__(self, board: Board):
        self._board = board

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
