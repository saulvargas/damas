from typing import Tuple

import numpy as np

NUM_PIECES = 12
NUM_ROWS = 8
NUM_COLS = 8

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
    def _moves_to(pos_a: Tuple[int, int], value_a: int, length: int, margin: int) -> np.ndarray:
        b = np.array(pos_a, dtype=np.int8)
        a = length * np.sign(value_a)

        if np.abs(value_a) == 1:
            positions = FWD_MOVES * a + b
        else:
            positions = ALL_MOVES * a + b

        valid = (positions[:, 0] >= margin) & (positions[:, 0] < (NUM_ROWS - margin)) & \
                (positions[:, 1] >= margin) & (positions[:, 1] < (NUM_COLS - margin))

        return positions[valid]

    def _get_moves1_from(self, pos_a: Tuple[int, int]):
        value_a = self[pos_a]

        poss_b = Board._moves_to(pos_a, value_a, length=1, margin=0)
        values_b = self[(poss_b[:, 0], poss_b[:, 1])]
        valid_b = values_b == 0

        moves1 = [(pos_a, tuple(xy.tolist())) for xy in poss_b[valid_b]]

        return moves1

    def _get_moves2_from(self, pos_a: Tuple[int, int]):
        value_a = self[pos_a]

        poss_c = Board._moves_to(pos_a, value_a, length=1, margin=1)
        values_c = self[(poss_c[:, 0], poss_c[:, 1])]
        valid_c = (value_a * values_c) < 0

        if np.any(valid_c):
            poss_b = 2 * poss_c[valid_c] - np.array(pos_a)
            values_b = self[(poss_b[:, 0], poss_b[:, 1])]
            valid_b = values_b == 0
            moves2 = [(pos_a, tuple(xy.tolist())) for xy in poss_b[valid_b]]

            return moves2
        else:
            return []

    def get_all_moves(self, player):
        poss_a = [tuple(xy.tolist()) for xy in np.transpose(np.nonzero(self.values * player > 0))]

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
