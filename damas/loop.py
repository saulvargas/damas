import asyncio

from damas.board import Board, DrawException
from damas.display import Display
from damas.player import Player


def loop(board: Board, display: Display, player_w: Player, player_b: Player):
    players = {+1: player_w, -1: player_b}

    display.render_board(board)

    while True:
        moves = board.get_all_moves()
        if not moves:
            break

        display.new_turn(board.turn_for)

        while True:
            move = players[board.turn_for].choose_move(moves)
            try:
                moves = board.move(move)
            except DrawException:
                display.render_board(board)
                display.end_game(winner=0)
                return 0, board.loop_count
            display.render_board(board)
            if not moves:
                break

    display.end_game(winner=-board.turn_for)

    return -board.turn_for, board.loop_count


async def async_loop(board: Board, display: Display, player_w: Player, player_b: Player):
    players = {+1: player_w, -1: player_b}

    await display.render_board(board)

    while True:
        moves = board.get_all_moves()
        if not moves:
            break

        await display.new_turn(board.turn_for)

        while True:
            move = players[board.turn_for].choose_move(moves)
            if asyncio.iscoroutine(move):
                move = await move
            try:
                moves = board.move(move)
            except DrawException:
                await display.render_board(board)
                await display.end_game(winner=0)
                return 0, board.loop_count
            await display.render_board(board)
            if not moves:
                break

    await display.end_game(winner=-board.turn_for)

    return -board.turn_for, board.loop_count
