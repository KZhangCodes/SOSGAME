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

        scoring_moves: list[tuple[int, int, str]] = [] #store scoring moves
        empty_cells: list[tuple[int, int]] = []

        #loop through cells
        for row in range(size):
            for col in range(size):
                if board.is_empty(row, col):
                    empty_cells.append((row, col)) #track empty cells
                    #line segment completion check
                    s_line = len(game.new_lines_from_move(row, col, "S", self.side))
                    if s_line > 0:
                        scoring_moves.append((row, col, "S"))
                    o_line = len(game.new_lines_from_move(row, col, "O", self.side))
                    if o_line > 0:
                        scoring_moves.append((row, col, "O"))

        #choose random scoring move
        if scoring_moves:
            return random.choice(scoring_moves)
        if not empty_cells:
            raise RuntimeError("Not empty")
        #choose random cell and letter
        row, col = random.choice(empty_cells)
        letter = random.choice(["S", "O"])
        return row, col, letter


        '''empty_cells = [
            (row, col)
            for row in range(size)
            for col in range(size)
            if board.is_empty(row, col)
        ]

        if not empty_cells:
            raise RuntimeError("Not empty")

        row, col = random.choice(empty_cells)
        letter = random.choice(["S", "O"])

        return row, col, letter'''
