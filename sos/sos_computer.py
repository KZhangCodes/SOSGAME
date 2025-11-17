from abc import ABC, abstractmethod
import random
from typing import Tuple

from sos_logic import BaseGame, Player

class ComputerOpponent(ABC):
    def __init__(self, side: Player):
        self.side = side

    @abstractmethod
    def choose_move(self, board: BaseGame) -> Tuple[int, int, str]:
        ...

class EasyComputerOpponent(ComputerOpponent):
    def choose_move(self, game: BaseGame) -> Tuple[int, int, str]:
        board = game.board
        size = board.board_size

        empty_cells = [
            (row, col)
            for row in range(size)
            for col in range(size)
            if board.is_empty(row, col)
        ]

        if not empty_cells:
            raise RuntimeError("Not empty")

        row, col = random.choice(empty_cells)
        letter = random.choice(["S", "O"])

        return row, col, letter
