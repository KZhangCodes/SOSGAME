from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import (QWidget, QMainWindow, QLabel, QGroupBox, QRadioButton,
                             QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,)

from sos_logic import Game, SIMPLE, GENERAL, validate_board_size

class GameBoard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._game = None
        self._cell = 35
        self._margin = 5
        self.setMinimumSize(8 * self._cell + 2 * self._margin, 8 * self._cell + 2 * self._margin)
        #widget large enough for max size
        #

    def set_game(self, game):
        self._game = game #current game instance
        side = game.n * self._cell + 2 * self._margin #widget based on board size
        self.setMinimumSize(side, side)
        self.update() #repaint event, calls paintEvent()

    def paintEvent(self, event):
        if not self._game:
            return
        painter = QPainter(self)

        n = self._game.n
        cell = self._cell
        m = self._margin
        size = n * cell

        #border and grid lines
        pen = QPen(Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(m, m, size, size) #square border enclosing cells
        for i in range(1, n):
            x = m + i * cell #vertical line pos
            painter.drawLine(x, m, x, m + size)
            y = m + i * cell #hortizontal
            painter.drawLine(m, y, m + size, y)

        #draw letter for S and O
        font = QFont()
        font.setPointSize(18)
        painter.setFont(font)
        for r in range(n): #value in position
            for c in range(n):
                value = self._game.board.grid[r][c]
                if value:
                    rect = QRect(m + c * cell, m + r * cell, cell, cell) #cell rectangle coord
                    painter.drawText(rect, Qt.AlignCenter, value)

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

        #board size range 3-8 default 3
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

        self.turn_label = QLabel("Current turn: —") #current turn label
        self.turn_label.setAlignment(Qt.AlignCenter)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.addLayout(top_row)
        root_layout.addLayout(board_wrap)
        root_layout.addWidget(self.turn_label)
        self.setCentralWidget(root)

        self.new_button.clicked.connect(self._start_new_game) #add start_new_game method

        self._start_new_game()





