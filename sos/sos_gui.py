from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QMainWindow, QLabel, QGroupBox, QRadioButton,
                             QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,)

from sos_logic import start_game, Mode, InvalidMoveError, InvalidGameModeError, InvalidBoardSizeError, \
    InvalidLetterError, Player


class GameBoard(QWidget):

    cell_clicked = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game = None
        self._cell_size = 35
        self._margin = 5
        self.setMinimumSize(8 * self._cell_size + 2 * self._margin, 8 * self._cell_size + 2 * self._margin)
        #widget large enough for max size
        #

    def set_game(self, game):
        self._game = game #current game instance
        side = game.board_size * self._cell_size + 2 * self._margin #widget based on board size
        self.setMinimumSize(side, side)
        self.update() #repaint event, calls paintEvent()

    def paintEvent(self, event):
        if not self._game:
            return
        painter = QPainter(self)

        board_size = self._game.board_size
        cell = self._cell_size
        margin = self._margin
        size = board_size * cell

        #border and grid lines
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(margin, margin, size, size) #square border enclosing cells
        for i in range(1, board_size):
            x = margin + i * cell #vertical line pos
            painter.drawLine(x, margin, x, margin + size)
            y = margin + i * cell #hortizontal
            painter.drawLine(margin, y, margin + size, y)

        #draw letter for S and O
        font = QFont()
        font.setPointSize(18)
        painter.setFont(font)
        for r in range(board_size): #value in position
            for c in range(board_size):
                value = self._game.board.grid[r][c]
                if value:
                    rect = QRect(margin + c * cell, margin + r * cell, cell, cell) #cell rectangle coord
                    painter.drawText(rect, Qt.AlignCenter, value)

        #draw line for completed SOS
        if getattr(self._game, "lines", None):
            line_pen = QPen()
            line_pen.setWidth(3)
            #color by owner
            for segment in self._game.lines:
                if segment.player == Player.RED:
                    line_pen.setColor(Qt.red)
                elif segment.player == Player.BLUE:
                    line_pen.setColor(Qt.blue)
                painter.setPen(line_pen)

                #grid coords to pixel center
                start_row, start_col = segment.start
                end_row, end_col = segment.end
                x1 = margin + start_col * cell + cell // 2
                y1 = margin + start_row * cell + cell // 2
                x2 = margin + end_col * cell + cell // 2
                y2 = margin + end_row * cell + cell // 2

                painter.drawLine(x1, y1, x2, y2)

    #mouse1 placement
    def mousePressEvent(self, event):
        if not self._game or event.button() != Qt.LeftButton:
            return
        cell = self._cell_size
        margin = self._margin
        x = event.x() - margin
        y = event.y() - margin
        if x < 0 or y < 0:
            return
        col = x // cell
        row = y // cell
        if 0 <= row < self._game.board_size and 0 <= col < self._game.board_size:
            self.cell_clicked.emit(row,col)

#main app window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOS Game")
        self.game = None #hold current game instance

        #game mode radios
        mode_box = QGroupBox("Game Mode")
        self.mode_simple = QRadioButton("Simple Mode")
        self.mode_general = QRadioButton("General Mode")
        self.mode_simple.setChecked(True) #default simple
        layout_mode = QVBoxLayout()
        layout_mode.addWidget(self.mode_simple)
        layout_mode.addWidget(self.mode_general)
        mode_box.setLayout(layout_mode)

        #QSpinBox only allows values between 3-8 regardless of input, arrows wont go outside this range
        size_box = QGroupBox("Board Size")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(3, 8)
        self.size_spin.setValue(3)
        layout_size = QVBoxLayout()
        layout_size.addWidget(self.size_spin)
        size_box.setLayout(layout_size)

        self.new_button = QPushButton("Start New Game") #game start
        top_row = QHBoxLayout()
        top_row.addWidget(mode_box)
        top_row.addStretch(1)
        top_row.addWidget(size_box)
        top_row.addWidget(self.new_button)

        self.board_widget = GameBoard() #board placement
        board_wrap = QHBoxLayout()
        board_wrap.addStretch(1)
        board_wrap.addWidget(self.board_widget)
        board_wrap.addStretch(1)

        #s/o picker
        self.red_box, self.red_s, self.red_o = self._create_player_box("Red")
        self.blue_box, self.blue_s, self.blue_o = self._create_player_box("Blue")
        self.red_s.setChecked(True)
        self.blue_s.setChecked(True)
        side_row = QHBoxLayout()
        side_row.addWidget(self.red_box)
        side_row.addLayout(board_wrap)
        side_row.addWidget(self.blue_box)

        self.turn_label = QLabel("Current turn: —") #current turn label
        self.turn_label.setAlignment(Qt.AlignCenter)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.addLayout(top_row)
        root_layout.addLayout(side_row)
        root_layout.addWidget(self.turn_label)
        self.setCentralWidget(root)

        self.new_button.clicked.connect(self._start_new_game) #add start_new_game method
        self.board_widget.cell_clicked.connect(self._on_cell_clicked)

        self._start_new_game()

    #s/o selection
    def _create_player_box(self, title):
        box = QGroupBox(title)
        s_radio = QRadioButton("S")
        o_radio = QRadioButton("O")
        v = QVBoxLayout()
        v.addWidget(s_radio)
        v.addWidget(o_radio)
        box.setLayout(v)
        return box, s_radio, o_radio

    def _get_current_mode(self):
        return Mode.SIMPLE if self.mode_simple.isChecked() else Mode.GENERAL

    #return player s/o selection
    def _get_current_player_letter(self):
        if not self.game: #default s
            return "S"
        if self.game.current_player == Player.RED:
            return "S" if self.red_s.isChecked() else "O"
        else:
            return "S" if self.blue_s.isChecked() else "O"

    def _update_turn_label(self):
        if not self.game:
            self.turn_label.setText("Current turn: —")
        elif self.game.current_player == Player.RED:
            self.turn_label.setText("Current turn: Red ")
        else:
            self.turn_label.setText("Current turn: Blue")

    #resets everything on start a new game, pass Game to Gameboard to draw empty grid
    def _start_new_game(self):
        board_size = self.size_spin.value()
        mode = self._get_current_mode()
        try:
            self.game = start_game(board_size=board_size, mode=mode)
        except (InvalidBoardSizeError, InvalidGameModeError) as e:
            QMessageBox.warning(self, "Invalid settings", str(e))
            return
        self.board_widget.set_game(self.game)
        self._update_turn_label()

    #place s/o on clicked cell
    def _on_cell_clicked(self, row, col):
        if not self.game:
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
        #game over and score popup
        if self.game.is_over:
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
        else:
            self._update_turn_label()








