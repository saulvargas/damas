import asyncio
import threading
import webbrowser
import websockets

from websockets import WebSocketServerProtocol

from damas.board import Board
from damas.display import Display
from damas.game import Game
from damas.player import MinimaxPlayer


class WebsocketDisplay(Display):

    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket

    async def render_board(self, board: Board):
        await self.websocket.send("render board")

    async def new_turn(self, player):
        await self.websocket.send("new turn")

    async def end_turn(self, player):
        await self.websocket.send("end turn")

    async def end_game(self, winner):
        await self.websocket.send("end game")

        return True

    async def select_move(self, moves):
        raise NotImplemented


async def echo(websocket: WebSocketServerProtocol, path: str):
    print("New connection")

    board = Board()
    board.start()
    display = WebsocketDisplay(websocket)
    player1 = MinimaxPlayer(board, +1, depth=4, seed=1)
    player2 = MinimaxPlayer(board, -1, depth=4, seed=1)
    game = Game(board, display, player1, player2)

    await websocket.send("dale")

    # await game.loop()


def main():
    start_server = websockets.serve(echo, "localhost", 4444)
    asyncio.get_event_loop().run_until_complete(start_server)
    threading.Thread(target=lambda: webbrowser.open("../index.html", new=2)).start()
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
