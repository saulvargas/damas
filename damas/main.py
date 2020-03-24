import curses

from damas.game import Position, Piece, Colour, Game, Board, Display
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

    def render_board(self, board: Board):
        for row in range(NUM_ROWS - 1, -1, -1):
            y = NUM_ROWS - 1 - row
            x = 0

            self.board_window.addstr(y, x, f"{row} |")
            for col in range(NUM_COLS):
                cell = board.piece_at(Position(row, col))
                if cell is None:
                    self.board_window.addstr(" |")
                elif isinstance(cell, Piece):
                    char = "w" if cell.colour == Colour.WHITE else "b"
                    if cell.is_king:
                        char = char.upper()
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


def print_board(board, window):
    for row in range(NUM_ROWS - 1, -1, -1):
        y = NUM_ROWS - 1 - row
        x = 0

        window.addstr(y, x, f"{row} |")
        for col in range(NUM_COLS):
            cell = board.piece_at(Position(row, col))
            if cell is None:
                window.addstr(" |")
            elif isinstance(cell, Piece):
                char = "w" if cell.colour == Colour.WHITE else "b"
                if cell.is_king:
                    char = char.upper()
                window.addstr(f"{char}|")

    y = NUM_ROWS
    x = 0
    window.addstr(y, x, "   ")
    for col in range(NUM_COLS):
        window.addstr(f"{col} ")

    window.refresh()


def main(_):
    board = Board()
    board.start()

    display = CursesDisplay()
    player1 = HumanPlayer(board, display.moves_window)
    # player1 = RandomPlayer(board)
    player2 = RandomPlayer(board)

    game = Game(board, display, player1, player2)
    game.loop()


if __name__ == '__main__':
    curses.wrapper(main)
