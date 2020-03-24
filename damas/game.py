from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple

from damas.settings import NUM_PIECES, NUM_ROWS, NUM_COLS


# TODO: callback system for giving orders


class Colour(Enum):
    BLACK = -1
    WHITE = +1

    def __repr__(self):
        if self == Colour.BLACK:
            return "black"
        else:
            return "white"


@dataclass
class Position:
    row: int
    col: int

    def __repr__(self):
        return f"({self.row},{self.col})"

    def is_valid(self) -> bool:
        return (self.row >= 0) and (self.row < NUM_ROWS) and (self.col >= 0) and (self.col < NUM_COLS)

    def __add__(self, other: "Position") -> "Position":
        return Position(self.row + other.row, self.col + other.col)

    def __floordiv__(self, b: int) -> "Position":
        return Position(self.row // b, self.col // b)

    def __mul__(self, b: int) -> "Position":
        return Position(self.row * b, self.col * b)


@dataclass
class Piece:
    colour: Colour
    position: Position
    is_king: bool

    def __repr__(self):
        char = "w" if self.colour == Colour.WHITE else "b"
        if self.is_king:
            char = char.capitalize()
        return f"{char}@{self.position}"

    def moves_to(self, length: int) -> List[Position]:
        fl = self.position + Position(+1, -1) * length * self.colour.value
        fr = self.position + Position(+1, +1) * length * self.colour.value
        bl = self.position + Position(-1, -1) * length * self.colour.value
        br = self.position + Position(-1, +1) * length * self.colour.value

        positions = [fl, fr]
        if self.is_king:
            positions += [bl, br]

        return [pos for pos in positions if pos.is_valid()]


@dataclass
class Move:
    position_from: Position
    position_to: Position
    captures: Optional[Position]

    def __repr__(self):
        if self.captures is None:
            return f"{self.position_from}->{self.position_to}"
        else:
            return f"{self.position_from}->{self.position_to} captures {self.captures}"


class Board:

    def __init__(self):
        self.cells: List[List[Optional[Piece]]] = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self.pieces: Dict[Colour, List[Piece]] = {}

    def piece_at(self, position: Position):
        return self.cells[position.row][position.col]

    def add_piece(self, piece: Piece):
        self.pieces[piece.colour].append(piece)
        self.cells[piece.position.row][piece.position.col] = piece

    def capture(self, position: Position):
        piece = self.piece_at(position)
        self.cells[position.row][position.col] = None
        self.pieces[piece.colour].remove(piece)

    def move(self, position_from: Position, position_to: Position):
        piece = self.piece_at(position_from)
        self.cells[position_from.row][position_from.col] = None
        self.cells[position_to.row][position_to.col] = piece
        piece.position = position_to

    def start(self):
        for colour in Colour:
            self.pieces[colour] = []
            for i in range(NUM_PIECES):
                row = (2 * i) // NUM_COLS
                col = (2 * i) % NUM_COLS + row % 2
                if colour == Colour.BLACK:
                    row = NUM_ROWS - 1 - row
                    col = NUM_COLS - 1 - col

                piece = Piece(colour, Position(row, col), is_king=False)

                self.add_piece(piece)


class Player(ABC):

    def __init__(self, board: Board):
        self._board = board

    @abstractmethod
    def choose_move(self, moves: List[Move]) -> Move:
        pass


class Display(ABC):

    @abstractmethod
    def render_board(self, board: Board):
        pass

    @abstractmethod
    def notify(self, msg: str, confirm: bool):
        pass


class Game:

    def __init__(self, board: Board, display: Display, player_w: Player, player_b: Player):
        self.board = board
        self.display = display
        self.player1 = player_w
        self.player2 = player_b
        self.turn = Colour.WHITE

    def next_turn(self):
        if self.turn == Colour.WHITE:
            self.turn = Colour.BLACK
        else:
            self.turn = Colour.WHITE

    def ask_move(self, moves: List[Move]) -> Move:
        player = self.player1 if self.turn == Colour.WHITE else self.player2
        return player.choose_move(moves)

    def possible_moves_piece(self, piece: Piece) -> Tuple[List[Move], List[Move]]:
        jumps = []
        simples = []

        pos_from = piece.position

        # check jump
        for pos_to in piece.moves_to(length=2):
            cell_over = self.board.piece_at((pos_from + pos_to) // 2)
            cell_to = self.board.piece_at(pos_to)
            if (cell_to is None) and isinstance(cell_over, Piece) and cell_over.colour != self.turn:
                jumps.append(Move(piece.position, pos_to, cell_over.position))

        # check simple move
        for pos_to in piece.moves_to(length=1):
            cell_to = self.board.piece_at(pos_to)
            if cell_to is None:
                simples.append(Move(piece.position, pos_to, captures=None))

        return jumps, simples

    def possible_moves(self) -> List[Move]:
        jumps = []
        simples = []
        for piece in self.board.pieces[self.turn]:
            piece_jumps, piece_simples = self.possible_moves_piece(piece)
            jumps += piece_jumps
            simples += piece_simples

        if jumps:
            return jumps
        else:
            return simples

    def do_move(self, move: Move) -> List[Move]:
        self.board.move(move.position_from, move.position_to)
        piece = self.board.piece_at(move.position_to)

        more_moves = []
        if move.captures is not None:
            self.board.capture(move.captures)
            jumps, _ = self.possible_moves_piece(piece)

            more_moves = jumps

        if ((self.turn == Colour.WHITE) and (move.position_to.row == NUM_ROWS - 1)) or \
                ((self.turn == Colour.BLACK) and (move.position_to.row == 0)):
            piece.is_king = True

        return more_moves

    def loop(self):
        self.display.render_board(self.board)

        possible_moves = self.possible_moves()
        while possible_moves:
            self.display.notify(f"TURN FOR {repr(self.turn).upper()}S", confirm=False)

            move = self.ask_move(possible_moves)

            more_moves = self.do_move(move)
            self.display.render_board(self.board)

            while more_moves:
                move = self.ask_move(more_moves)
                more_moves = self.do_move(move)

                self.display.render_board(self.board)

            this_turn = repr(self.turn).upper() + "S"

            self.next_turn()
            possible_moves = self.possible_moves()

            if possible_moves:
                self.display.notify(f"END OF {this_turn} TURN - PRESS ANY KEY TO CONTINUE", confirm=True)
            else:
                self.display.notify(f"{this_turn} WIN - PRESS ANY KEY TO EXIT", confirm=True)
