import curses
from abc import ABC, abstractmethod

from damas.board import Board, NUM_ROWS, NUM_COLS


class Display(ABC):

    @abstractmethod
    def render_board(self, board: Board):
        pass

    @abstractmethod
    def new_turn(self, player):
        pass

    @abstractmethod
    def end_turn(self, player):
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

    def end_turn(self, player):
        pass

    def end_game(self, winner):
        return True

    def select_move(self, moves):
        pass


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
        self.status_window.clear()
        self.status_window.addstr(0, 0, f"TURN FOR {self._player_name(player)}")
        self.status_window.refresh()

    def end_turn(self, player):
        self.status_window.clear()
        self.status_window.addstr(0, 0, f"END OF {self._player_name(player)} TURN - PRESS ANY KEY TO CONTINUE")
        self.status_window.getkey()

    def end_game(self, winner):
        self.status_window.clear()
        self.status_window.addstr(0, 0, f"{self._player_name(winner)} WIN - (R)ESTART OR (Q)UIT?")

        while True:
            key = self.status_window.getkey().lower()
            if key in ["r", "q"]:
                break

        return key == "q"

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
