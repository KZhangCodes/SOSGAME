from dataclasses import dataclass, field

MIN_N = 3
MAX_N = 8
Cell = str | None #cell s/o or empty

class InvalidBoardSizeError(ValueError):
    """raise if board size invalid"""
    #pass

def validate_board_size(n: int) -> None:
    if not isinstance(n, int): #int checking
        raise InvalidBoardSizeError("Board size invalid")
    if n < MIN_N:
        raise InvalidBoardSizeError("Board must be at least 3")
    if n > MAX_N:
        raise InvalidBoardSizeError("Board must less than or 8")

@dataclass #__init__
class Board:
    n: int
    grid: list[list[Cell]] = field(init=False)
    #validate board, each none = empty cell for gui
    def __post_init__(self) -> None:
        validate_board_size(self.n)
        self.grid = [[None for _ in range(self.n)] for _ in range(self.n)] #list of lists grid with value none
