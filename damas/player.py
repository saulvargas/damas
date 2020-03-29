import random
from abc import ABC, abstractmethod

import numpy as np

from damas.board import Board, DrawException
from damas.display import Display


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
    DRAW_SCORE = -500
    LOSE_SCORE = -1000
    WIN_SCORE = 1000

    def __init__(self, board: Board, player: int, depth: int, seed=None, conservative=False, compact=True):
        super().__init__(board, player)
        self._depth = depth
        self._rs = random.Random(seed)
        self._conservative = conservative
        self._compact = compact

    def _score(self, board: Board, moves):
        if not moves:
            winner = -board.turn_for
            if self._player == winner:
                return self.WIN_SCORE
            else:
                return self.LOSE_SCORE

        # TODO: replace really bad heuristic!
        balance = np.sum(board.values) * self._player
        total_pieces = np.sum(np.abs(board.values))
        if self._conservative:
            return balance + total_pieces
        else:
            return balance

    def _minimax(self, board: Board, moves, depth: int, alpha, beta):
        if (depth == 0) or (not moves):
            return self._score(board, moves), None

        if board.turn_for == self._player:
            best_score, best_move = -1000000, None
        else:
            best_score, best_move = +1000000, None

        self._rs.shuffle(moves)
        for move in moves:
            next_board = board.copy()

            try:
                more_moves = next_board.move(move)
            except DrawException:
                score = self.DRAW_SCORE
            else:
                while self._compact and (len(more_moves) == 1):
                    more_moves = next_board.move(more_moves[0])

                next_moves = more_moves if more_moves else next_board.get_all_moves()
                score, _ = self._minimax(next_board, next_moves, depth - 1, alpha, beta)

            if board.turn_for == self._player:
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
        if len(moves) == 1:
            return moves[0]

        alpha = -np.inf
        beta = np.inf
        best_score, best_move = self._minimax(self._board, moves, self._depth, alpha, beta)

        return best_move


class HumanPlayer(Player):

    def __init__(self, board: Board, player: int, display: Display):
        super().__init__(board, player)
        self._display = display

    def choose_move(self, moves):
        return self._display.select_move(moves)
