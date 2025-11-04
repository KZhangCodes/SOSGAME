from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import IntEnum, StrEnum

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

#enum for player and mode
class Player(IntEnum):
    RED = 1
    BLUE = 2

class Mode(StrEnum):
    SIMPLE = "simple"
    GENERAL = "general"

MIN_N = 3
MAX_N = 8
Cell = str | None #cell s/o or empty

DEFAULT_STARTING_PLAYER = Player.RED
PLAYERS = (Player.RED, Player.BLUE)
MODES = (Mode.SIMPLE, Mode.GENERAL)

#validations for separation of concerns (most constraint checks done by GUI)
def validate_board_size(board_size: int) -> None:
    if not isinstance(board_size, int): #int checking
        raise InvalidBoardSizeError("Board size invalid")
    if board_size < MIN_N:
        raise InvalidBoardSizeError("Board must be at least 3")
    if board_size > MAX_N:
        raise InvalidBoardSizeError("Board must less than or 8")

def validate_mode(mode: str | Mode) -> Mode:
    if isinstance(mode, Mode):
        return mode
    if not isinstance(mode, str):
        raise InvalidGameModeError("Game mode must be string")
    m = mode.strip().lower() #normalization
    if m == Mode.SIMPLE.value:
        return Mode.SIMPLE
    if m == Mode.GENERAL.value:
        return Mode.GENERAL
    raise InvalidGameModeError("Game mode must be Simple or General")

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

#completed sos segment
@dataclass(frozen=True)
class CompletedSOS:
    start: tuple[int, int] #endpoints
    end: tuple[int, int]
    player: Player #sos owner

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

    def is_full(self)-> bool:
        return all(cell is not None for row in self.grid for cell in row)

#abstract base class for both simple and general - turn order, placing validation, sos line and completion tracking
@dataclass
class BaseGame(ABC):
    board_size: int
    starting_player: Player = DEFAULT_STARTING_PLAYER

    board: Board = field(init=False)
    current_player: Player = field(init=False)
    is_over: bool = field(default=False, init=False)
    winner: Player | None = field(default=None, init=False)
    lines: list[CompletedSOS] = field(default_factory=list, init=False)
    red_score: int = field(default=0, init=False)
    blue_score: int = field(default=0, init=False)

    #checks independent of gui radio button constraints
    def __post_init__(self) -> None:
        if self.starting_player not in PLAYERS:
            raise ValueError("Invalid player")
        self.board = Board(self.board_size)
        self.current_player = self.starting_player

    '''def cell_is_empty(self, row: int, col: int) -> bool:
        return self.board.grid[row][col] is None'''

    def _switch_turns(self) -> None:
        self.current_player = Player.BLUE if self.current_player == Player.RED else Player.RED

    def place_letter(self, row: int, col: int, letter:str) -> None:
        if self.is_over:
            raise InvalidMoveError("Game over")
        validate_position(self.board_size , row, col)
        letter = validate_letter(letter)
        if not self.board.is_empty(row, col):
            raise InvalidMoveError("Cell is already occupied")
        self.board.grid[row][col] = letter #place letter
        self._after_move(row, col, letter)
        if not self.is_over: #check if game is over
            self._switch_turns()

    @abstractmethod
    def _after_move(self, row: int,col: int, letter:str) -> None:
        ...

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.board_size and 0 <= c < self.board_size

    def cell(self, r: int, c: int) -> Cell:
        return self.board.grid[r][c]
    #append new sos lines and increment score
    def sos_line(self, new_lines: list[CompletedSOS]) -> None:
        if not new_lines:
            return
        self.lines.extend(new_lines)
        scored = len(new_lines)
        if self.current_player == Player.RED:
            self.red_score += scored
        else:
            self.blue_score += scored
    #returns list of CompletedSOS segments with owner as current player
    def new_lines_from_move(self, row: int, col: int, letter: str) -> list[CompletedSOS]:
        player = self.current_player
        lines: list[CompletedSOS] = []

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)] #horizontal, vert, diagonal, diagonal

        def add_line(start: tuple[int, int], end: tuple[int, int]) -> None:
            lines.append(CompletedSOS(start, end, player))

        #placed O, must be in middle of SOS
        if letter == "O":
            for d_row, d_col in directions:
                start_r, start_c = row - d_row, col - d_col
                end_r, end_c = row + d_row, col + d_col
                if self.in_bounds(start_r, start_c) and self.in_bounds(end_r, end_c):
                    if self.cell(start_r, start_c) == "S" and self.cell(end_r, end_c) == "S":
                            add_line((start_r, start_c), (end_r, end_c))
        #placed S, must be at either end of SOS
        elif letter == "S":
            for d_row, d_col in directions:
                #S at start of SOS
                mid_r, mid_c = row + d_row, col + d_col
                end_r, end_c = row + 2 * d_row, col + 2 * d_col
                if self.in_bounds(mid_r, mid_c) and self.in_bounds(end_r, end_c):
                    if self.cell(mid_r, mid_c) == "O" and self.cell(end_r, end_c) == "S":
                        add_line((row, col), (end_r, end_c))
                #S at end SOS
                start_r, start_c = row - 2 * d_row, col - 2 * d_col
                mid_r2, mid_c2   = row - d_row,     col - d_col
                if self.in_bounds(start_r, start_c) and self.in_bounds(mid_r2, mid_c2):
                    if self.cell(mid_r2, mid_c2) == "O" and self.cell(start_r, start_c) == "S":
                        add_line((start_r, start_c), (row, col))
            return lines
        return lines

class SimpleGame(BaseGame):
    def _after_move(self, row: int, col: int, letter:str) -> None:
        new_lines = self.new_lines_from_move(row, col, letter)
        self.sos_line(new_lines)
        #scoring simple
        if new_lines:
            self.is_over = True
            self.winner = self.current_player
            return
        if self.board.is_full():
            self.is_over = True
            self.winner = None

class GeneralGame(BaseGame):
    def _after_move(self, row: int, col: int, letter:str) -> None:
        new_lines = self.new_lines_from_move(row, col, letter)
        self.sos_line(new_lines)
        #scoring general
        if self.board.is_full():
            self.is_over = True
            if self.red_score > self.blue_score:
                self.winner = Player.RED
            elif self.blue_score > self.red_score:
                self.winner = Player.BLUE
            else:
                self.winner = None

def start_game(*, board_size: int, mode: str | Mode, starting_player: Player = DEFAULT_STARTING_PLAYER) -> BaseGame:
    m = validate_mode(mode)
    if m == Mode.SIMPLE:
        return SimpleGame(board_size=board_size, starting_player=starting_player)
    else:
        return GeneralGame(board_size=board_size, starting_player=starting_player)








