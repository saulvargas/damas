from time import time

from damas.board import Board
from damas.display import NoDisplay
from damas.loop import loop
from damas.player import MinimaxPlayer


def main():
    display = NoDisplay()

    for i in range(10):
        board = Board()

        player_w = MinimaxPlayer(board, player=+1, depth=4, seed=i)
        player_b = MinimaxPlayer(board, player=-1, depth=4, seed=i)

        t0 = time()
        wins, turns = loop(board, display, player_w, player_b)
        dt = time() - t0

        print(f"{i}\t{wins}\t{turns}\t{dt}")


if __name__ == '__main__':
    main()
