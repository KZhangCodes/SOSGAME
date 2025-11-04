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

@dataclass(frozen=True)
class CompletedSOS:
    start: tuple[int, int] #endpoints
    end: tuple[int, int]
    SOS_player: int #sos owner

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


@dataclass
class BaseGame(ABC):
    board_size: int
    starting_player: int = DEFAULT_STARTING_PLAYER

    board: Board = field(init=False)
    current_player: int = field(init=False)
    is_over: bool = field(default=False, init=False)
    winner: int | None = field(default=None, init=False)
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
        self.current_player = BLUE_PLAYER if self.current_player == RED_PLAYER else RED_PLAYER

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

    def SOS_line(self, new_lines: list[CompletedSOS]) -> None:
        if not new_lines:
            return
        self.lines.extend(new_lines)
        scored = len(new_lines)
        if self.current_player == RED_PLAYER:
            self.red_score += scored
        else:
            self.blue_score += scored

    def new_lines_from_move(self, r: int, c: int, letter: str) -> list[CompletedSOS]:
        SOS_player = self.current_player
        lines: list[CompletedSOS] = []

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)] #horizontal, vert, diagonal, diagonal
        #placed O, must be in middle of SOS
        if letter == "O":
            for dr, dc in directions:
                r1, c1 = r - dr, c - dc
                r3, c3 = r + dr, c + dc
                if self.in_bounds(r1, c1) and self.in_bounds(r3, c3):
                    if self.cell(r1, c1) == "S" and self.cell(r3, c3) == "S":
                        lines.append(CompletedSOS((r1, c1), (r3, c3), SOS_player))
            return lines
        #placed S, must be at either end of SOS
        if letter == "S":
            for dr, dc in directions:
                #S at start of SOS
                r0, c0 = r +dr, c + dc
                rS2, cS2 = r + 2*dr, c + 2*dc
                if self.in_bounds(r0, c0) and self.in_bounds(rS2, cS2):
                    if self.cell(r0, c0) == "O" and self.cell(rS2, cS2) == "S":
                        lines.append(CompletedSOS((r, c), (rS2, cS2), SOS_player))
                #S at end SOS
                rS1, cS1 = r - 2*dr, c - 2*dc
                rO2, cO2 = r - dr, c - dc
                if self.in_bounds(rS1, cS1) and self.in_bounds(rO2, cO2):
                    if self.cell(rO2, cO2) == "O" and self.cell(rS1, cS1) == "S":
                        lines.append(CompletedSOS((rS1, cS1), (r, c), SOS_player))
            return lines
        return lines

class SimpleGame(BaseGame):
    def _after_move(self, row: int, col: int, letter:str) -> None:
        new_lines = self.new_lines_from_move(row, col, letter)
        self.SOS_line(new_lines)
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
        self.SOS_line(new_lines)
        #scoring general
        if self.board.is_full():
            self.is_over = True
            if self.red_score > self.blue_score:
                self.winner = RED_PLAYER
            elif self.blue_score > self.red_score:
                self.winner = BLUE_PLAYER
            else:
                self.winner = None

def start_game(*, board_size: int, mode: str, starting_player: int = DEFAULT_STARTING_PLAYER) -> BaseGame:
    m = validate_mode(mode)
    if m == SIMPLE:
        return SimpleGame(board_size=board_size, starting_player=starting_player)
    else:
        return GeneralGame(board_size=board_size, starting_player=starting_player)








