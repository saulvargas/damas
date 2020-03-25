import random
from abc import ABC, abstractmethod

import numpy as np

from damas.board import Board


class Player(ABC):

    def __init__(self, board: Board, player: int):
        self._board = board
        self._player = player

    @abstractmethod
    def choose_move(self, moves):
        pass


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

    def _minimax(self, board: Board, moves, depth: int, alpha, beta, player: int):
        if player == self._player:
            best_score, best_move = -1000, None
        else:
            best_score, best_move = +1000, None

        if (depth == 0) or (not moves):
            return self._score(board), None

        self._rs.shuffle(moves)
        for move in moves:
            next_board = board.copy()
            next_moves = next_board.move(player, move)
            if next_moves:
                score, _ = self._minimax(next_board, next_moves, depth - 1, alpha, beta, player)
            else:
                next_moves = next_board.get_all_moves(-player)
                score, _ = self._minimax(next_board, next_moves, depth - 1, alpha, beta, -player)

            if player == self._player:
                if score > best_score:
                    best_score, best_move = score, move
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            else:
                if score < best_score:
                    best_score, best_move = score, move
                beta = min(beta, best_score)
                if alpha >= beta:
                    break

        return best_score, best_move

    def choose_move(self, moves):
        alpha = -np.inf
        beta = np.inf
        best_score, best_move = self._minimax(self._board, moves, self._depth, alpha, beta, self._player)

        return best_move


class HumanPlayer(Player):
    key_to_pos = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                  "q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]

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
