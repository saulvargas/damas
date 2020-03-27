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

        turns = 0
        moves = None

        while True:
            if not moves:
                moves = self.board.get_all_moves()

                if moves and (turns > 0):
                    self.display.end_turn(-self.board.turn_for)
                elif not moves:
                    self.display.end_game(winner=-self.board.turn_for)
                    return -self.board.turn_for, turns

                self.display.new_turn(self.board.turn_for)
                if self.board.turn_for == +1:
                    turns += 1

            move = self.players[self.board.turn_for].choose_move(moves)
            moves = self.board.move(move)
            self.display.render_board(self.board)

    async def async_loop(self):
        await self.display.render_board(self.board)

        turns = 0
        moves = None

        while True:
            if not moves:
                moves = self.board.get_all_moves()

                if moves and (turns > 0):
                    await self.display.end_turn(-self.board.turn_for)
                elif not moves:
                    await self.display.end_game(winner=-self.board.turn_for)
                    return -self.board.turn_for, turns

                await self.display.new_turn(self.board.turn_for)
                if self.board.turn_for == +1:
                    turns += 1

            move = self.players[self.board.turn_for].choose_move(moves)
            if asyncio.iscoroutine(move):
                move = await move
            moves = self.board.move(move)
            await self.display.render_board(self.board)
