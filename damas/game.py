from damas.board import Board
from damas.display import Display
from damas.player import Player


def player_name(player):
    if player == +1:
        return "WHITES"
    else:
        return "BLACKS"


class Game:

    def __init__(self, board: Board, display: Display, player_w: Player, player_b: Player):
        self.board = board
        self.display = display
        self.players = {+1: player_w, -1: player_b}

    def loop(self):
        self.display.render_board(self.board)

        player = +1
        turns = 0

        possible_moves = self.board.get_all_moves(player)
        while True:
            if player == +1:
                turns += 1

            self.display.notify(f"TURN FOR {player_name(player)}", confirm=False)

            move = self.players[player].choose_move(possible_moves)

            more_moves = self.board.move(player, move)
            self.display.render_board(self.board)

            while more_moves:
                move = self.players[player].choose_move(more_moves)
                more_moves = self.board.move(player, move)

                self.display.render_board(self.board)

            possible_moves = self.board.get_all_moves(-player)

            if possible_moves:
                self.display.notify(f"END OF {player_name(player)} TURN - PRESS ANY KEY TO CONTINUE", confirm=True)
                player = -player
            else:
                self.display.notify(f"{player_name(player)} WIN - PRESS ANY KEY TO EXIT", confirm=True)
                return player, turns
