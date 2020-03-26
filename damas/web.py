import asyncio
import json
import sys
import threading
import webbrowser
from os import path

import websockets
from websockets import WebSocketServerProtocol

from damas.board import Board
from damas.display import Display
from damas.game import Game
from damas.player import MinimaxPlayer, HumanPlayer


class WebsocketDisplay(Display):

    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket

    async def render_board(self, board: Board):
        msg = {
            "event": "render_board",
            "board": board.values.tolist()
        }

        await self.websocket.send(json.dumps(msg))
        await self.websocket.recv()

    async def new_turn(self, player):
        msg = {
            "event": "new_turn",
            "player": player
        }

        await self.websocket.send(json.dumps(msg))

    async def end_turn(self, player):
        msg = {
            "event": "end_turn",
            "player": player
        }

        await self.websocket.send(json.dumps(msg))

    async def end_game(self, winner):
        msg = {
            "event": "new_turn",
            "player": winner
        }

        await self.websocket.send(json.dumps(msg))

    async def select_move(self, moves):
        msg = {
            "event": "select_move",
            "moves": moves,
        }

        await self.websocket.send(json.dumps(msg))
        move = json.loads(await self.websocket.recv())
        move = ((move[0][0], move[0][1]), (move[1][0], move[1][1]))

        return move


async def echo(websocket: WebSocketServerProtocol, path: str):
    print("New connection")

    board = Board()
    board.start()

    display = WebsocketDisplay(websocket)

    player1 = HumanPlayer(board, +1, display)
    # player1 = MinimaxPlayer(board, +1, depth=2, seed=1)
    # player1 = RandomPlayer(board, +1, seed=1)
    player2 = MinimaxPlayer(board, -1, depth=6, seed=1)

    game = Game(board, display, player1, player2)

    await game.async_loop()


def main():
    bundle_dir = getattr(sys, "_MEIPASS", path.abspath(path.dirname(__file__)))
    index_path = path.join(bundle_dir, "index.html")

    start_server = websockets.serve(echo, "localhost", 4444)
    asyncio.get_event_loop().run_until_complete(start_server)
    threading.Thread(target=lambda: webbrowser.open(index_path, new=2)).start()
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
