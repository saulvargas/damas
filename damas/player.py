import random
from abc import ABC, abstractmethod

import numpy as np

from damas.board import Board
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

    def __init__(self, board: Board, player: int, depth: int, seed=None, conservative=False):
        super().__init__(board, player)
        self._depth = depth
        self._rs = random.Random(seed)
        self._conservative = conservative

    def _score(self, board: Board):
        # TODO: replace really bad heuristic!
        balance = np.sum(board.values) * self._player
        total_pieces = np.sum(np.abs(board.values))
        if self._conservative:
            return balance + total_pieces
        else:
            return balance

    def _minimax(self, board: Board, moves, depth: int, alpha, beta, player: int):
        if (depth == 0) or (not moves):
            return self._score(board), None

        if player == self._player:
            best_score, best_move = -1000, None
        else:
            best_score, best_move = +1000, None

        self._rs.shuffle(moves)
        for move in moves:
            next_board = board.copy()
            more_moves = next_board.move(player, move)

            if more_moves:
                next_moves, next_player = more_moves, player
            else:
                next_moves, next_player = next_board.get_all_moves(-player), -player

            next_depth = depth - 1
            # if len(next_moves) == 1:
            #     next_depth = depth
            # else:
            #     next_depth = depth - 1

            score, _ = self._minimax(next_board, next_moves, next_depth, alpha, beta, next_player)

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
        if len(moves) == 1:
            return moves[0]

        alpha = -np.inf
        beta = np.inf
        best_score, best_move = self._minimax(self._board, moves, self._depth, alpha, beta, self._player)

        return best_move


class HumanPlayer(Player):

    def __init__(self, board: Board, player: int, display: Display):
        super().__init__(board, player)
        self._display = display

    def choose_move(self, moves):
        return self._display.select_move(moves)
