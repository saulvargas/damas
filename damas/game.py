import asyncio

from damas.board import Board, DrawException
from damas.display import Display
from damas.player import Player


class Game:

    def __init__(self, board: Board, display: Display, player_w: Player, player_b: Player):
        self.board = board
        self.display = display
        self.players = {+1: player_w, -1: player_b}

    def loop(self):
        self.display.render_board(self.board)

        while True:
            moves = self.board.get_all_moves()
            if not moves:
                break

            self.display.new_turn(self.board.turn_for)

            while True:
                move = self.players[self.board.turn_for].choose_move(moves)
                try:
                    moves = self.board.move(move)
                except DrawException:
                    self.display.render_board(self.board)
                    self.display.end_game(winner=0)
                    return 0, self.board.loop_count
                self.display.render_board(self.board)
                if not moves:
                    break

        self.display.end_game(winner=-self.board.turn_for)

        return -self.board.turn_for, self.board.loop_count

    async def async_loop(self):
        await self.display.render_board(self.board)

        while True:
            moves = self.board.get_all_moves()
            if not moves:
                break

            await self.display.new_turn(self.board.turn_for)

            while True:
                move = self.players[self.board.turn_for].choose_move(moves)
                if asyncio.iscoroutine(move):
                    move = await move
                try:
                    moves = self.board.move(move)
                except DrawException:
                    await self.display.render_board(self.board)
                    await self.display.end_game(winner=0)
                    return 0, self.board.loop_count
                await self.display.render_board(self.board)
                if not moves:
                    break

        await self.display.end_game(winner=-self.board.turn_for)

        return -self.board.turn_for, self.board.loop_count
