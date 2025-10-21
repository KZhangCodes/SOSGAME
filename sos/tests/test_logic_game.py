import unittest
from unittest import TestCase

from sos_logic import (SIMPLE, GENERAL, MODES, Game, Board, InvalidBoardSizeError,
    InvalidMoveError, MIN_N, MAX_N, PLAYERS, DEFAULT_STARTING_PLAYER,)

class TestGameMode(unittest.TestCase):

    def test_valid_modes(self):
        self.assertEqual(set(MODES), {SIMPLE, GENERAL})
        self.assertEqual(len(MODES), 2)

class TestGameInit(unittest.TestCase):
    def test_game_init(self):
        g = Game(board_size=MIN_N, mode=SIMPLE, starting_player=2)
        self.assertEqual(g.board.board_size, MIN_N)
        self.assertIsInstance(g.board, Board)
        self.assertEqual(g.current_player, 2)

class TestGameCellAndMoves(unittest.TestCase):
    def setUp(self):
        self.g = Game(board_size=3, mode=SIMPLE, starting_player=DEFAULT_STARTING_PLAYER)

    def test_cell_empty_init(self):
        self.assertTrue(self.g.cell_is_empty(0,0))
        self.assertTrue(self.g.cell_is_empty(2,2))

    def test_place_letter_and_switch_turn(self):
        #player 1 S
        self.g.place_letter(0, 0, "S")
        self.assertEqual(self.g.board.grid[0][0], "S")
        self.assertEqual(self.g.current_player, 2)  # switch
        #player 2 o
        self.g.place_letter(1, 1, "O")
        self.assertEqual(self.g.board.grid[1][1], "O")
        self.assertEqual(self.g.current_player, 1) #switch

    def test_cannot_place_on_occupied_cell(self):
        self.g.place_letter(0, 0, "S")
        with self.assertRaises(InvalidMoveError):
            self.g.place_letter(0, 0, "O")

if __name__ == '__main__':
    unittest.main()
