from damas.board import Board
from damas.display import Display
from damas.player import Player


class Game:

    def __init__(self, board: Board, display: Display, player_w: Player, player_b: Player):
        self.board = board
        self.display = display
        self.players = {+1: player_w, -1: player_b}

    def loop(self):
        while True:
            board = self.board.copy()

            self.display.render_board(board)

            player = +1
            turns = 0

            possible_moves = board.get_all_moves(player)
            while True:
                if player == +1:
                    turns += 1

                self.display.new_turn(player)

                move = self.players[player].choose_move(possible_moves)

                more_moves = board.move(player, move)
                self.display.render_board(board)

                while more_moves:
                    move = self.players[player].choose_move(more_moves)
                    more_moves = board.move(player, move)

                    self.display.render_board(board)

                possible_moves = board.get_all_moves(-player)

                if possible_moves:
                    self.display.end_turn(player)
                    player = -player
                else:
                    if self.display.end_game(player):
                        return player, turns
                    else:
                        break
