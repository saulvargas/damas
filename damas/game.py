from damas.board import Board
from damas.display import Display
from damas.player import Player


class Game:

    def __init__(self, board: Board, display: Display, player_w: Player, player_b: Player):
        self.board = board
        self.display = display
        self.players = {+1: player_w, -1: player_b}

    def loop(self):
        board = self.board.copy()
        self.display.render_board(board)

        player, opponent = -1, +1
        turns = 0
        moves = None

        while True:
            if not moves:
                player, opponent = opponent, player
                moves = board.get_all_moves(player)

                if moves and (turns > 0):
                    self.display.end_turn(opponent)
                elif not moves:
                    self.display.end_game(winner=opponent)
                    return opponent, turns

                self.display.new_turn(player)
                if player == +1:
                    turns += 1

            move = self.players[player].choose_move(moves)
            moves = board.move(player, move)
            self.display.render_board(board)

    async def async_loop(self):
        board = self.board.copy()
        await self.display.render_board(board)

        player, opponent = -1, +1
        turns = 0
        moves = None

        while True:
            if not moves:
                player, opponent = opponent, player
                moves = board.get_all_moves(player)

                if moves and (turns > 0):
                    await self.display.end_turn(opponent)
                elif not moves:
                    await self.display.end_game(winner=opponent)
                    return opponent, turns

                await self.display.new_turn(player)
                if player == +1:
                    turns += 1

            move = self.players[player].choose_move(moves)
            moves = board.move(player, move)
            await self.display.render_board(board)
