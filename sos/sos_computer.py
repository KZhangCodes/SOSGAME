from abc import ABC, abstractmethod
import random

from sos_logic import BaseGame, Player

class ComputerOpponent(ABC):
    def __init__(self, side: Player):
        self.side = side

    @abstractmethod
    def choose_move(self, game: BaseGame) -> tuple[int, int, str]:
        ...

class EasyComputerOpponent(ComputerOpponent):
    def choose_move(self, game: BaseGame) -> tuple[int, int, str]:
        board = game.board
        size = board.board_size

        scoring_moves: list[tuple[int, int, str]] = []
        empty_cells: list[tuple[int, int]] = []

        #loop through cells
        for row in range(size):
            for col in range(size):
                if not board.is_empty(row, col):
                    continue
                empty_cells.append((row, col))
                for letter in ("S", "O"):
                    if game.new_lines_from_move(row, col, letter, self.side):
                        scoring_moves.append((row, col, letter))

        #choose random scoring move
        if scoring_moves:
            return random.choice(scoring_moves)
        if not empty_cells:
            raise RuntimeError("Not empty")
        #choose random cell and letter
        row, col = random.choice(empty_cells)
        letter = random.choice(["S", "O"])
        return row, col, letter


