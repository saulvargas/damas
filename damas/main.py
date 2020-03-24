import curses

from damas.game import Game, Board, Display
from damas.ai import RandomPlayer, HumanPlayer
from damas.settings import NUM_COLS, NUM_ROWS


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


def main(_):
    board = Board()
    board.start()
    # board.add((7, 0), +2)
    # board.add((6, 1), -1)

    display = CursesDisplay()
    player1 = HumanPlayer(board, display.moves_window)
    # player1 = RandomPlayer(board)
    player2 = RandomPlayer(board)

    game = Game(board, display, player1, player2)
    game.loop()


if __name__ == '__main__':
    curses.wrapper(main)
