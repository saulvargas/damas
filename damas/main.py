import curses

from damas.board import Board
from damas.player import HumanPlayer, MinimaxPlayer
from damas.game import Game
from damas.display import CursesDisplay


def main(_):
    board = Board()
    board.start()

    display = CursesDisplay()

    player1 = HumanPlayer(board, +1, display)
    # player1 = RandomPlayer(board, +1, seed=1)
    # player1 = MinimaxPlayer(board, +1, depth=4, seed=1)
    player2 = MinimaxPlayer(board, -1, depth=4, seed=1)

    game = Game(board, display, player1, player2)
    game.loop()


if __name__ == '__main__':
    curses.wrapper(main)
