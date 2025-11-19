from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QMainWindow, QLabel, QGroupBox, QRadioButton,
                             QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QButtonGroup)

from sos_logic import start_game, Mode, InvalidMoveError, InvalidGameModeError, InvalidBoardSizeError, \
    InvalidLetterError, Player
from sos_computer import EasyComputerOpponent


class GameBoard(QWidget):

    cell_clicked = pyqtSignal(int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._game = None
        self._cell_size = 35
        self._margin = 5
        self._init_minimum_size()

    def _init_minimum_size(self) -> None:
        max_board_size = 8
        side = max_board_size * self._cell_size + 2 * self._margin
        self.setMinimumSize(side, side)

    def _update_board_size(self) -> None:
        if not self._game:
            return
        side = self._game.board_size * self._cell_size + 2 * self._margin
        self.setMinimumSize(side, side)

    def set_game(self, game) -> None:
        self._game = game
        self._update_board_size()
        self.update() #repaint event, calls paintEvent()

    def _board_geometry(self) -> tuple[int, int, int, int]:
        board_size = self._game.board_size
        cell_size = self._cell_size
        margin = self._margin
        size = board_size * cell_size
        return board_size, cell_size, margin, size

    def paintEvent(self, event) -> None:
        if not self._game:
            return
        painter = QPainter(self)
        board_size, cell, margin, size = self._board_geometry()

        self._draw_grid(painter, board_size, cell, margin, size)
        self._draw_letters(painter, board_size, cell, margin)
        self._draw_sos_lines(painter, cell, margin)

    def _draw_grid(self, painter: QPainter, board_size: int, cell: int, margin: int, size: int) ->None:
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(margin, margin, size, size) #square border enclosing cells

        for i in range(1, board_size):
            x = margin + i * cell #vertical line pos
            painter.drawLine(x, margin, x, margin + size)
            y = margin + i * cell #hortizontal
            painter.drawLine(margin, y, margin + size, y)

    def _draw_letters(self, painter: QPainter, board_size: int, cell: int, margin: int) ->None:
        #draw letter for S and O
        font = QFont()
        font.setPointSize(18)
        painter.setFont(font)
        for row in range(board_size): #value in position
            for col in range(board_size):
                value = self._game.board.get_cell(row, col)
                if value:
                    rect = QRect(margin + col * cell, margin + row * cell, cell, cell) #cell rectangle coord
                    painter.drawText(rect, Qt.AlignCenter, value)

    def _draw_sos_lines(self, painter: QPainter, cell: int, margin: int) ->None:
        if not self._game:
            return

        segments = self._game.get_lines()
        if not segments:
            return

        line_pen = QPen()
        line_pen.setWidth(3)
        #color by owner
        for segment in segments:
            if segment.player == Player.RED:
                line_pen.setColor(Qt.red)
            elif segment.player == Player.BLUE:
                line_pen.setColor(Qt.blue)
            else:
                continue
            painter.setPen(line_pen)

            #grid coords to pixel center
            start_row, start_col = segment.start
            end_row, end_col = segment.end
            x1 = margin + start_col * cell + cell // 2
            y1 = margin + start_row * cell + cell // 2
            x2 = margin + end_col * cell + cell // 2
            y2 = margin + end_row * cell + cell // 2

            painter.drawLine(x1, y1, x2, y2)

    def mousePressEvent(self, event) -> None:
        if not self._game:
            return
        if event.button() != Qt.LeftButton:
            return

        x = event.x() - self._margin
        y = event.y() - self._margin

        if x < 0 or y < 0:
            return
        col = x // self._cell_size
        row = y // self._cell_size

        board_size = self._game.board.board_size
        if not (0 <= row < board_size and 0 <= col < board_size):
            return

        self.cell_clicked.emit(row,col)

#main app window
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.game = None #hold current game instance

        self.computers: dict[Player, EasyComputerOpponent] = {}

        self._setup_window()
        self._create_widget()
        self._create_layout()
        self._signals()
        self._start_new_game()

    def _setup_window(self) -> None:
        self.setWindowTitle("SOS Game")

    def _create_widget(self) -> None:
        self.mode_box = self._create_mode_box()
        self.size_box = self._create_size_box()
        self.new_button = QPushButton("Start new game")
        self.board_widget = GameBoard() #board placement
        # s/o picker
        self.red_box, self.red_human, self.red_computer, self.red_s, self.red_o = self._create_player_box("Red")
        self.blue_box, self.blue_human, self.blue_computer, self.blue_s, self.blue_o = self._create_player_box("Blue")
        self.red_s.setChecked(True)
        self.blue_s.setChecked(True)
        self.red_human.setChecked(True)
        self.blue_human.setChecked(True)
        self.turn_label = QLabel("Current turn: —")
        self.turn_label.setAlignment(Qt.AlignCenter)

    def _create_layout(self) -> None:
        top_row = self._build_top_row()
        side_row = self._build_side_row()

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.addLayout(top_row)
        root_layout.addLayout(side_row)
        root_layout.addWidget(self.turn_label)
        self.setCentralWidget(root)

    def _signals(self) -> None:
        self.new_button.clicked.connect(self._start_new_game) #add start_new_game method
        self.board_widget.cell_clicked.connect(self._on_cell_clicked)

    def _create_mode_box(self) -> QGroupBox:
        mode_box = QGroupBox("Game mode")
        self.mode_simple = QRadioButton("Simple Mode")
        self.mode_general = QRadioButton("General Mode")
        self.mode_simple.setChecked(True) #default simple
        layout_mode = QVBoxLayout()
        layout_mode.addWidget(self.mode_simple)
        layout_mode.addWidget(self.mode_general)
        mode_box.setLayout(layout_mode)
        return mode_box

    def _create_size_box(self) -> QGroupBox:
        #QSpinBox only allows values between 3-8 regardless of input, arrows wont go outside this range
        size_box = QGroupBox("Board Size")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(3, 8)
        self.size_spin.setValue(3)
        layout_size = QVBoxLayout()
        layout_size.addWidget(self.size_spin)
        size_box.setLayout(layout_size)
        return size_box

    def _build_top_row(self) -> QHBoxLayout:
        top_row = QHBoxLayout()
        top_row.addWidget(self.mode_box)
        top_row.addStretch(1)
        top_row.addWidget(self.size_box)
        top_row.addWidget(self.new_button)
        return top_row

    def _build_side_row(self) -> QHBoxLayout:
        board_wrap = QHBoxLayout()
        board_wrap.addStretch(1)
        board_wrap.addWidget(self.board_widget)
        board_wrap.addStretch(1)

        side_row = QHBoxLayout()
        side_row.addWidget(self.red_box)
        side_row.addLayout(board_wrap)
        side_row.addWidget(self.blue_box)
        return side_row

    #s/o selection
    def _create_player_box(self, title) -> tuple[QGroupBox, QRadioButton, QRadioButton, QRadioButton, QRadioButton]:
        box = QGroupBox(title)

        human_radio = QRadioButton("Human")
        computer_radio = QRadioButton("Computer")
        s_radio = QRadioButton("S")
        o_radio = QRadioButton("O")

        human_group = QButtonGroup(box)
        human_group.setExclusive(True)
        human_group.addButton(human_radio)
        human_group.addButton(computer_radio)

        letter_group = QButtonGroup(box)
        letter_group.setExclusive(True)
        letter_group.addButton(s_radio)
        letter_group.addButton(o_radio)

        layout = QVBoxLayout()
        layout.addWidget(human_radio)
        layout.addWidget(computer_radio)
        layout.addSpacing(8)
        layout.addWidget(s_radio)
        layout.addWidget(o_radio)

        box.setLayout(layout)

        return box, human_radio, computer_radio, s_radio, o_radio

    def _current_player_computer(self) -> bool:
        if not self.game:
            return False
        return self.game.current_player in self.computers

    def _get_current_mode(self):
        return Mode.SIMPLE if self.mode_simple.isChecked() else Mode.GENERAL

    #return player s/o selection
    def _get_current_player_letter(self):
        if not self.game: #default s
            return "S"
        if self.game.current_player == Player.RED:
            return "S" if self.red_s.isChecked() else "O"
        return "S" if self.blue_s.isChecked() else "O"

    def _update_turn_label(self):
        if not self.game:
            self.turn_label.setText("Current turn: —")
            return

        if self.game.current_player == Player.RED:
            self.turn_label.setText("Current turn: Red ")
        else:
            self.turn_label.setText("Current turn: Blue")

    def _game_over_dialog(self):
        if not self.game or not self.game.is_over:
            return

        if self.mode_simple.isChecked():
            if self.game.winner == Player.RED:
                QMessageBox.information(self, "Game Over", "Red wins")
            elif self.game.winner == Player.BLUE:
                QMessageBox.information(self, "Game Over", "Blue wins")
            else:
                QMessageBox.information(self, "Game Over", "Draw")
        else:
            red_score, blue_score = self.game.red_score, self.game.blue_score
            if self.game.winner == Player.RED:
                QMessageBox.information(self, "Game Over", f"Red wins {red_score}-{blue_score}")
            elif self.game.winner == Player.BLUE:
                QMessageBox.information(self, "Game Over", f"Blue wins {blue_score}-{red_score}")
            else:
                QMessageBox.information(self, "Game Over", f"Draw {red_score}-{blue_score}")

    def _handle_computer_move(self):
        if not self.game:
            return
        #stop counter
        moves_left = self.game.board_size * self.game.board_size

        while not self.game.is_over and moves_left > 0:
            computer = self.computers.get(self.game.current_player) #check if current player is computer
            if computer is None:
                break
            row, col, letter = computer.choose_move(self.game)
            self.game.place_letter(row, col, letter)
            moves_left -= 1

        self.board_widget.update()

        if self.game.is_over:
            self._game_over_dialog()
        else:
            self._update_turn_label()

    #resets everything on start a new game, pass Game to Gameboard to draw empty grid
    def _start_new_game(self):
        board_size = self.size_spin.value()
        mode = self._get_current_mode()
        #set computer
        self.computers = {}
        if self.red_computer.isChecked():
            self.computers[Player.RED] = EasyComputerOpponent(Player.RED)
        if self.blue_computer.isChecked():
            self.computers[Player.BLUE] = EasyComputerOpponent(Player.BLUE)

        try:
            self.game = start_game(board_size=board_size, mode=mode)
        except (InvalidBoardSizeError, InvalidGameModeError) as e:
            QMessageBox.warning(self, "Invalid settings", str(e))
            return

        self.board_widget.set_game(self.game)
        self._update_turn_label()
        self._handle_computer_move()

    def _on_cell_clicked(self, row, col):
        if not self.game:
            return

        if self._current_player_computer():
            return

        letter = self._get_current_player_letter()
        try:
            self.game.place_letter(row, col, letter)
        except InvalidMoveError as e:
            QMessageBox.information(self, "Invalid move", str(e))
            return
        except InvalidLetterError as e:
            QMessageBox.warning(self, "Invalid letter", str(e))
            return

        self.board_widget.update() #redraw board

        if self.game.is_over:
            self._game_over_dialog()
            return

        self._update_turn_label()
        self._handle_computer_move()








