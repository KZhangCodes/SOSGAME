from dataclasses import dataclass, field

MIN_N = 3
MAX_N = 8
Cell = str | None #cell s/o or empty

class InvalidBoardSizeError(ValueError):
    """raise if board size invalid"""
    #pass

class InvalidMoveError(ValueError):
    """raise if move invalid"""

#radio button default player1
PLAYERS = (1,2)
default_starting_player = 1

#radio button simple and general, default simple mode for gui
SIMPLE = "simple"
GENERAL = "general"
MODES = ("simple", "general")
DEFAULT_MODE = SIMPLE

def validate_board_size(n: int) -> None:
    if not isinstance(n, int): #int checking
        raise InvalidBoardSizeError("Board size invalid")
    if n < MIN_N:
        raise InvalidBoardSizeError("Board must be at least 3")
    if n > MAX_N:
        raise InvalidBoardSizeError("Board must less than or 8")

def start_default_mode() -> str:
    return DEFAULT_MODE

@dataclass #__init__
class Board:
    n: int
    grid: list[list[Cell]] = field(init=False)
    #validate board, each none = empty cell for gui
    def __post_init__(self) -> None:
        validate_board_size(self.n)
        self.grid = [[None for _ in range(self.n)] for _ in range(self.n)] #list of lists grid with value none

@dataclass
class Game:
    n: int
    mode: str
    starting_player: int = default_starting_player
    board: Board = field(init=False)
    current_player: int = field(init=False)

    #checks independent of gui radio button constraints
    def __post_init__(self) -> None:
        validate_board_size(self.n)
        if self.mode not in MODES:
            raise ValueError("Invalid mode")
        if self.starting_player not in PLAYERS:
            raise ValueError("Invalid player")
        self.board = Board(self.n)
        self.current_player = self.starting_player

    def cell_is_empty(self, row: int, col: int) -> bool:
        return self.board.grid[row][col] is None

    def place_letter(self, row: int, col: int, letter:str) -> None:
        if letter not in ("S", "O"):
            raise ValueError("Invalid letter")
        if not self.cell_is_empty(row, col):
            raise InvalidMoveError("Cell is already occupied")
        self.board.grid[row][col] = letter
        self._switch_turns()

    def _switch_turns(self) -> None:
        self.current_player = 2 if self.current_player == 1 else 1





