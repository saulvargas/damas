import curses
import sys

from damas.ai import HumanPlayer, MinimaxPlayer, RandomPlayer
from damas.game import Game, Board, Display
from damas.settings import NUM_COLS, NUM_ROWS


class NoDisplay(Display):

    def render_board(self, board: Board):
        pass

    def notify(self, msg: str, confirm: bool):
        pass


class CursesDisplay(Display):
    MAX_WIDTH = 80

    def __init__(self):

        y = 0
        self.status_window = curses.newwin(1, self.MAX_WIDTH, y, 0)
        y += 2
        self.board_window = curses.newwin(NUM_ROWS + 2, 2 * NUM_COLS + 3, y, 0)
        y += NUM_ROWS + 2 + 1
        self.moves_window = curses.newwin(20, self.MAX_WIDTH, y, 0)

    value_to_char = {0: " ", +1: "w", +2: "W", -1: "b", -2: "B"}

    def render_board(self, board: Board):
        for row in range(NUM_ROWS - 1, -1, -1):
            y = NUM_ROWS - 1 - row
            x = 0

            self.board_window.addstr(y, x, f"{row} |")
            for col in range(NUM_COLS):
                value = board[(row, col)]
                char = self.value_to_char[value]
                self.board_window.addstr(f"{char}|")

        y = NUM_ROWS
        x = 0
        self.board_window.addstr(y, x, "   ")
        for col in range(NUM_COLS):
            self.board_window.addstr(f"{col} ")

        self.board_window.refresh()

    def notify(self, msg: str, confirm: bool):
        self.status_window.clear()
        self.status_window.addstr(0, 0, msg)

        if confirm:
            self.status_window.getkey()
        else:
            self.status_window.refresh()


def main(gui: bool = True):
    board = Board()
    board.start()

    if gui:
        display = CursesDisplay()
    else:
        display = NoDisplay()

    # player1 = HumanPlayer(board, +1, display.moves_window)
    player1 = RandomPlayer(board, +1)
    # player1 = MinimaxPlayer(board, +1, depth=4)
    player2 = MinimaxPlayer(board, -1, depth=4)

    game = Game(board, display, player1, player2)
    game.loop()


if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "--no-gui"):
        main(gui=False)
    else:
        curses.wrapper(main)
