import curses
from time import sleep

from damas.board import Board
from damas.board import NUM_ROWS, NUM_COLS
from damas.display import Display
from damas.game import Game
from damas.player import HumanPlayer, MinimaxPlayer


class CursesDisplay(Display):
    MAX_WIDTH = 80

    def __init__(self):

        y = 0
        self.status_window = curses.newwin(1, self.MAX_WIDTH, y, 0)
        y += 2
        self.board_window = curses.newwin(NUM_ROWS + 3, 2 * NUM_COLS + 3, y, 0)
        y += NUM_ROWS + 2 + 1
        self.moves_window = curses.newwin(20, self.MAX_WIDTH, y, 0)

    value_to_char = {0: " ", +1: "⛀", +2: "⛁", -1: "⛂", -2: "⛃"}

    def render_board(self, board: Board):
        self.board_window.addstr(0, 0, "  ")
        self.board_window.addstr(" ", curses.A_UNDERLINE)
        for col in range(NUM_COLS):
            self.board_window.addstr(f"  ", curses.A_UNDERLINE)

        for row in range(NUM_ROWS - 1, -1, -1):
            y = NUM_ROWS - row
            x = 0

            self.board_window.addstr(y, x, f"{row} ")
            self.board_window.addstr("|", curses.A_UNDERLINE)
            for col in range(NUM_COLS):
                value = board[(row, col)]
                char = self.value_to_char[value]
                self.board_window.addstr(f"{char}|", curses.A_UNDERLINE)

        y = NUM_ROWS + 1
        x = 0
        self.board_window.addstr(y, x, "   ")
        for col in range(NUM_COLS):
            self.board_window.addstr(f"{col} ")

        self.board_window.refresh()

    @staticmethod
    def _player_name(player):
        if player == +1:
            return "WHITES"
        else:
            return "BLACKS"

    def new_turn(self, player):
        sleep(1)
        self.status_window.clear()
        self.status_window.addstr(0, 0, f"TURN FOR {self._player_name(player)}")
        self.status_window.refresh()

    def end_game(self, winner):
        self.status_window.clear()
        self.status_window.addstr(0, 0, f"{self._player_name(winner)} WIN - PRESS ANY KEY TO QUIT")
        self.status_window.getkey()

    key_to_pos = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                  "q", "w", "e", "r", "t", "y", "u", "i", "o", "p"
                                                               "a", "s", "d", "f", "g", "h", "j", "k", "l"]

    def select_move(self, moves):
        self.moves_window.clear()
        for i, move in enumerate(moves):
            pos_a, pos_b = move
            self.moves_window.addstr(i, 0, f"{self.key_to_pos[i].upper()}: {pos_a}->{pos_b}")

        while True:
            key = self.moves_window.getkey().lower()
            try:
                pos = self.key_to_pos.index(key)
                if pos < len(moves):
                    break
            except ValueError:
                pass

        self.moves_window.clear()
        self.moves_window.refresh()

        return moves[pos]


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
