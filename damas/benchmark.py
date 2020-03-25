from time import time

from damas.ai import RandomPlayer, MinimaxPlayer
from damas.game import Game, Board
from damas.main import NoDisplay


def main():
    display = NoDisplay()

    for i in range(10):
        board = Board()
        board.start()
        player_w = MinimaxPlayer(board, player=+1, depth=2, seed=i)
        player_b = MinimaxPlayer(board, player=-1, depth=2, seed=i)

        game = Game(board, display, player_w, player_b)

        t0 = time()
        wins, turns = game.loop()
        dt = time() - t0

        print(f"{i}\t{wins}\t{turns}\t{dt}")


if __name__ == '__main__':
    main()
