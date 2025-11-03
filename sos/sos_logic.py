from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class InvalidBoardSizeError(ValueError):
    pass
class InvalidMoveError(ValueError):
    pass
class InvalidGameModeError(ValueError):
    pass
class InvalidLetterError(ValueError):
    pass
class OutOfBoundsError(InvalidMoveError):
    pass

MIN_N = 3
MAX_N = 8
Cell = str | None #cell s/o or empty

#radio button default player1
RED_PLAYER = 1
BLUE_PLAYER = 2
PLAYERS = (RED_PLAYER, BLUE_PLAYER)
DEFAULT_STARTING_PLAYER = 1

#radio button simple and general, default simple mode for gui
SIMPLE = "simple"
GENERAL = "general"
MODES = (SIMPLE, GENERAL)

#validations for separation of concerns (most constraint checks done by GUI)
def validate_board_size(board_size: int) -> None:
    if not isinstance(board_size, int): #int checking
        raise InvalidBoardSizeError("Board size invalid")
    if board_size < MIN_N:
        raise InvalidBoardSizeError("Board must be at least 3")
    if board_size > MAX_N:
        raise InvalidBoardSizeError("Board must less than or 8")

def validate_mode(mode: str) -> str:
    if not isinstance(mode, str):
        raise InvalidGameModeError("Game mode must be string")
    m = mode.strip().lower() #normalization
    if m not in MODES:
        raise InvalidGameModeError("Game mode must be Simple or General")
    return m

def validate_letter(letter:str) -> str:
    if not isinstance(letter, str):
        raise InvalidLetterError("Letter must be string")
    letter = letter.strip().upper()
    if letter not in ("S", "O"):
        raise InvalidLetterError("Letter must be S or O")
    return letter

def validate_position(board_size: int, row: int, col: int) -> None:
    if not (0 <= row < board_size and 0 <= col < board_size):
        raise OutOfBoundsError("Row/Column out of bounds")

@dataclass #__init__
class Board:
    board_size: int
    grid: list[list[Cell]] = field(init=False)
    #validate board, each none = empty cell for gui
    def __post_init__(self) -> None:
        validate_board_size(self.board_size)
        self.grid = [[None for _ in range(self.board_size)] for _ in range(self.board_size)] #list of lists grid with value none

    def is_empty(self, row: int, col: int) -> bool:
        return self.grid[row][col] is None

@dataclass
class BaseGame(ABC):
    board_size: int
    board: Board = field(init=False)
    current_player: int

    #checks independent of gui radio button constraints
    def __init__(self, *, board_size: int, starting_player: int = DEFAULT_STARTING_PLAYER) -> None:
        if starting_player not in PLAYERS:
            raise ValueError("Invalid player")
        self.board = Board(board_size)
        self.board_size = board_size
        self.current_player = starting_player

    '''def cell_is_empty(self, row: int, col: int) -> bool:
        return self.board.grid[row][col] is None'''

    def _switch_turns(self) -> None:
        self.current_player = BLUE_PLAYER if self.current_player == RED_PLAYER else RED_PLAYER

    def place_letter(self, row: int, col: int, letter:str) -> None:
        validate_position(self.board_size , row, col)
        letter = validate_letter(letter)
        if not self.board.is_empty(row, col):
            raise InvalidMoveError("Cell is already occupied")
        self.board.grid[row][col] = letter #place letter
        self._after_move(row, col, letter)
        self._switch_turns()

    @abstractmethod
    def _after_move(self, row: int,col: int, letter:str) -> None:
        ...

class SimpleGame(BaseGame):
    def _after_move(self, row: int, col: int, letter:str) -> None:
        #win con
        pass

class GeneralGame(BaseGame):
    def _after_move(self, row: int, col: int, letter:str) -> None:
        #win con
        pass

def start_game(*, board_size: int, mode: str, starting_player: int = DEFAULT_STARTING_PLAYER) -> BaseGame:
    m = validate_mode(mode)
    if m == SIMPLE:
        return SimpleGame(board_size=board_size, starting_player=starting_player)
    else:
        return GeneralGame(board_size=board_size, starting_player=starting_player)








