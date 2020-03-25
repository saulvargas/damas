import random

import numpy as np

from damas.game import Player, Board


class RandomPlayer(Player):

    def __init__(self, board: Board, player: int, seed=None):
        super().__init__(board, player)

        self._rs = random.Random(seed)

    def choose_move(self, moves):
        i = self._rs.randrange(len(moves))
        return moves[i]


class MinimaxPlayer(Player):

    def __init__(self, board: Board, player: int, depth: int, seed=None):
        super().__init__(board, player)
        self._depth = depth
        self._rs = random.Random(seed)

    def _score(self, board: Board):
        # TODO: replace really bad heuristic!
        balance = np.sum(board.values)
        return balance * self._player

    def _minimax(self, board: Board, moves, depth: int, player: int):
        if player == self._player:
            best_score, best_moves = -1000, []
        else:
            best_score, best_moves = +1000, []

        if (depth == 0) or (not moves):
            return self._score(board), None

        for move in moves:
            next_board = board.copy()
            next_moves = next_board.move(player, move)
            if next_moves:
                score, _ = self._minimax(next_board, next_moves, depth - 1, player)
            else:
                next_moves = next_board.get_all_moves(-player)
                score, _ = self._minimax(next_board, next_moves, depth - 1, -player)

            if score == best_score:
                best_moves.append(move)
            else:
                if player == self._player:
                    if score > best_score:
                        best_score, best_moves = score, [move]
                else:
                    if score < best_score:
                        best_score, best_moves = score, [move]

        return best_score, best_moves

    def choose_move(self, moves):
        best_score, best_moves = self._minimax(self._board, moves, self._depth, self._player)

        i = self._rs.randrange(len(best_moves))
        return best_moves[i]


class HumanPlayer(Player):
    key_to_pos = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]

    def __init__(self, board: Board, player: int, window):
        super().__init__(board, player)
        self._window = window

    def choose_move(self, moves):
        self._window.clear()
        for i, move in enumerate(moves):
            pos_a, pos_b = move
            self._window.addstr(i, 0, f"{self.key_to_pos[i].upper()}: {pos_a}->{pos_b}")

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
