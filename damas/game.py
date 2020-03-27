import asyncio

from damas.board import Board
from damas.display import Display
from damas.player import Player


class Game:

    def __init__(self, board: Board, display: Display, player_w: Player, player_b: Player):
        self.board = board
        self.display = display
        self.players = {+1: player_w, -1: player_b}

    def loop(self):
        self.display.render_board(self.board)

        player, opponent = -1, +1
        turns = 0
        moves = None

        while True:
            if not moves:
                player, opponent = opponent, player
                moves = self.board.get_all_moves(player)

                if moves and (turns > 0):
                    self.display.end_turn(opponent)
                elif not moves:
                    self.display.end_game(winner=opponent)
                    return opponent, turns

                self.display.new_turn(player)
                if player == +1:
                    turns += 1

            move = self.players[player].choose_move(moves)
            moves = self.board.move(player, move)
            self.display.render_board(self.board)
            print(f"{turns}\t{player}\t{move}")

    async def async_loop(self):
        await self.display.render_board(self.board)

        player, opponent = -1, +1
        turns = 0
        moves = None

        while True:
            if not moves:
                player, opponent = opponent, player
                moves = self.board.get_all_moves(player)

                if moves and (turns > 0):
                    await self.display.end_turn(opponent)
                elif not moves:
                    await self.display.end_game(winner=opponent)
                    return opponent, turns

                await self.display.new_turn(player)
                if player == +1:
                    turns += 1

            move = self.players[player].choose_move(moves)
            if asyncio.iscoroutine(move):
                move = await move
            moves = self.board.move(player, move)
            await self.display.render_board(self.board)
            print(f"{turns}\t{player}\t{move}")
