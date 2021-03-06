from functools import lru_cache
from typing import Tuple, Union

import numpy as np

NUM_PIECES = 12
NUM_ROWS = 8
NUM_COLS = 8

FWD_MOVES = np.array([[+1, -1], [+1, +1]], dtype=np.int8)
ALL_MOVES = np.array([[+1, -1], [+1, +1], [-1, -1], [-1, +1]], dtype=np.int8)

TURNS_DRAW = 40


class DrawException(Exception):
    pass


class Board:

    def __init__(self, add_pieces=True):
        self.values = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.int8)
        if add_pieces:
            for value in [+1, -1]:
                for i in range(NUM_PIECES):
                    row = (2 * i) // NUM_COLS
                    col = (2 * i) % NUM_COLS + row % 2
                    if value < 0:
                        row = NUM_ROWS - 1 - row
                        col = NUM_COLS - 1 - col

                    self[(row, col)] = value

        self.previous_values = [self.values.tobytes()]

        self.turn_for = +1
        self.loop_count = 1
        self.move_end = False

        self.last_crowned = {+1: 0, -1: 0}
        self.last_captured = {+1: 0, -1: 0}

    def __getitem__(self, pos: Tuple[Union[int, np.ndarray], Union[int, np.ndarray]]) -> Union[np.ndarray, int]:
        return self.values[pos]

    def __setitem__(self, pos: Tuple[int, int], value: int):
        self.values[pos] = value

    def copy(self) -> "Board":
        board = Board(add_pieces=False)
        board.values = self.values.copy()
        board.previous_values = self.previous_values.copy()

        board.turn_for = self.turn_for
        board.loop_count = self.loop_count
        board.move_end = self.move_end

        board.last_crowned = self.last_crowned.copy()
        board.last_captured = self.last_captured.copy()

        return board

    @staticmethod
    @lru_cache(maxsize=None)
    def _moves_to(pos_a: Tuple[int, int], value_a: int, margin: int) -> np.ndarray:
        b = np.array(pos_a, dtype=np.int8)
        a = np.sign(value_a)

        if np.abs(value_a) == 1:
            positions = FWD_MOVES * a + b
        else:
            positions = ALL_MOVES * a + b

        valid = (positions[:, 0] >= margin) & (positions[:, 0] < (NUM_ROWS - margin)) & \
                (positions[:, 1] >= margin) & (positions[:, 1] < (NUM_COLS - margin))

        return positions[valid]

    def _get_moves1_from(self, pos_a: Tuple[int, int]):
        value_a = self[pos_a]

        poss_b = Board._moves_to(pos_a, value_a, margin=0)
        values_b = self[(poss_b[:, 0], poss_b[:, 1])]
        valid_b = values_b == 0

        moves1 = [(pos_a, tuple(xy.tolist())) for xy in poss_b[valid_b]]

        return moves1

    def _get_moves2_from(self, pos_a: Tuple[int, int]):
        value_a = self[pos_a]

        poss_c = Board._moves_to(pos_a, value_a, margin=1)
        values_c = self[(poss_c[:, 0], poss_c[:, 1])]
        valid_c = (value_a * values_c) < 0

        if np.any(valid_c):
            poss_b = 2 * poss_c[valid_c] - np.array(pos_a, dtype=np.int8)
            values_b = self[(poss_b[:, 0], poss_b[:, 1])]
            valid_b = values_b == 0
            moves2 = [(pos_a, tuple(xy.tolist())) for xy in poss_b[valid_b]]

            return moves2
        else:
            return []

    def get_all_moves(self):
        poss_a = [tuple(xy.tolist()) for xy in np.transpose(np.nonzero(self.values * self.turn_for > 0))]

        moves2 = [m for pos_a in poss_a for m in self._get_moves2_from(pos_a)]
        if moves2:
            return moves2

        moves1 = [m for pos_a in poss_a for m in self._get_moves1_from(pos_a)]

        return moves1

    @staticmethod
    def is_jump(move):
        pos_a, pos_b = move

        return np.abs(pos_a[0] - pos_b[0]) == 2

    def move(self, move):
        if self.move_end:
            self.move_end = False
            if self.turn_for == +1:
                self.loop_count += 1

        pos_a, pos_b = move
        self[pos_a], self[pos_b] = 0, self[pos_a]

        more_moves = []
        if self.is_jump(move):
            self.previous_values.clear()
            self.last_captured[self.turn_for] = -1

            pos_c = tuple((np.array(pos_a, dtype=np.int8) + np.array(pos_b, dtype=np.int8)) // 2)
            self[pos_c] = 0
            more_moves = self._get_moves2_from(pos_b)

        if (self.turn_for == +1) and (pos_b[0] == NUM_ROWS - 1) and (self[pos_b] == +1):
            self.previous_values.clear()
            self.last_crowned[+1] = -1
            self[pos_b] = +2

        if (self.turn_for == -1) and (pos_b[0] == 0) and (self[pos_b] == -1):
            self.previous_values.clear()
            self.last_crowned[-1] = -1
            self[pos_b] = -2

        if not more_moves:
            self.previous_values.append(self.values.tobytes())

            self.last_captured[self.turn_for] += 1
            self.last_crowned[self.turn_for] += 1
            self.turn_for = -self.turn_for
            self.move_end = True
            if self.draw_conditions():
                raise DrawException

        return more_moves

    def draw_conditions(self):
        return self.draw_condition_1_32_2() or self.draw_condition_1_32_1()

    def draw_condition_1_32_1(self):
        count = 0
        last = self.previous_values[-1]
        for previous in self.previous_values[:-1]:
            if last == previous:
                count += 1
                if count == 2:
                    return True
        return False

    def draw_condition_1_32_2(self):
        return (self.last_crowned[+1] >= TURNS_DRAW) and \
               (self.last_crowned[-1] >= TURNS_DRAW) and \
               (self.last_captured[+1] >= TURNS_DRAW) and \
               (self.last_captured[-1] >= TURNS_DRAW)
