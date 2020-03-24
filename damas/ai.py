import random
from typing import List

from damas.game import Move, Player, Board


class RandomPlayer(Player):

    def choose_move(self, moves: List[Move]) -> Move:
        i = random.randrange(len(moves))
        return moves[i]


class HumanPlayer(Player):
    key_to_pos = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]

    def __init__(self, board: Board, window):
        super().__init__(board)
        self._window = window

    def choose_move(self, moves: List[Move]) -> Move:
        self._window.clear()
        for i, move in enumerate(moves):
            self._window.addstr(i, 0, f"{self.key_to_pos[i].upper()}: {repr(move)}")

        self._window.refresh()

        while True:
            key = self._window.getkey().lower()
            try:
                pos = self.key_to_pos.index(key)
                if pos < len(moves):
                    break
            except ValueError:
                pass

        self._window.clear()
        self._window.refresh()

        return moves[pos]
