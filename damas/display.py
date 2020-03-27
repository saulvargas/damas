from abc import ABC, abstractmethod

from damas.board import Board


class Display(ABC):

    @abstractmethod
    def render_board(self, board: Board):
        pass

    @abstractmethod
    def new_turn(self, player):
        pass

    @abstractmethod
    def end_game(self, winner):
        pass

    @abstractmethod
    def select_move(self, moves):
        pass


class NoDisplay(Display):

    def render_board(self, board: Board):
        pass

    def new_turn(self, player):
        pass

    def end_game(self, winner):
        pass

    def select_move(self, moves):
        pass
