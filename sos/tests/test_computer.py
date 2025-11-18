import unittest

from sos_logic import (start_game, Mode, Player, InvalidMoveError, InvalidLetterError)
from sos_computer import EasyComputerOpponent

#user story 8: move against computer opponent in simple game
class TestSimplePlayerComputer(unittest.TestCase):
    def setUp(self):
        self.game = start_game(board_size=3, mode=Mode.SIMPLE, starting_player=Player.RED) #red human blue computer
        self.computer = EasyComputerOpponent(Player.BLUE)
    #ac 8.1
    def test_valid_player_move_simple(self):
        self.assertTrue(self.game.board.is_empty(0, 0))
        self.game.place_letter(0, 0, "S")
        self.assertEqual(self.game.board.get_cell(0, 0), "S")
        self.assertEqual(self.game.current_player, Player.BLUE)
    #ac 8.2
    def test_invalid_player_move_simple(self):
        self.game.place_letter(0, 0, "S")
        with self.assertRaises(InvalidMoveError):
            self.game.place_letter(0, 0, "O")  #same cell should fail

        #cell unchanged
        self.assertEqual(self.game.board.get_cell(0, 0), "S")
        self.assertEqual(self.game.current_player, Player.BLUE)
    #ac 8.3
    def test_computer_score_simple(self):
        #blue has winning move ready
        self.game.place_letter(0, 0, "S")
        self.game.place_letter(0, 1, "O")
        self.game.place_letter(2, 2, "S")
        self.assertFalse(self.game.is_over)
        self.assertEqual(self.game.current_player, Player.BLUE)
        #computer move
        row, col, letter = self.computer.choose_move(self.game)
        new_lines = self.game.new_lines_from_move(row, col, letter, Player.BLUE)
        self.assertGreaterEqual(len(new_lines), 1)
        #apply move and blue wins
        self.game.place_letter(row, col, letter)
        self.assertTrue(self.game.is_over)
        self.assertEqual(self.game.winner, Player.BLUE)

#user story 9: move against computer opponent in general game
class TestGeneralPlayerComputer(unittest.TestCase):
    def setUp(self):
        self.game = start_game(board_size=3, mode=Mode.GENERAL, starting_player=Player.RED)
        self.computer = EasyComputerOpponent(Player.BLUE)
    #ac 9.1
    def test_valid_player_move_general(self):
        self.assertTrue(self.game.board.is_empty(1, 1))
        self.game.place_letter(1, 1, "O")
        self.assertEqual(self.game.board.get_cell(1, 1), "O")
        self.assertEqual(self.game.current_player, Player.BLUE)
    #ac 9.2
    def test_invalid_player_move_general(self):
        self.game.place_letter(0, 0, "S")
        with self.assertRaises(InvalidMoveError):
            self.game.place_letter(0, 0, "O")

        self.assertEqual(self.game.board.get_cell(0, 0), "S")
        self.assertEqual(self.game.current_player, Player.BLUE)
    #ac 9.3
    def test_computer_score_general(self):
        self.game.place_letter(0, 0, "S")   # RED
        self.game.place_letter(0, 1, "O")   # BLUE
        self.game.place_letter(2, 2, "S")   # RED
        self.assertFalse(self.game.is_over)
        self.assertEqual(self.game.current_player, Player.BLUE)

        row, col, letter = self.computer.choose_move(self.game)
        new_lines = self.game.new_lines_from_move(row, col, letter, Player.BLUE)
        self.assertGreaterEqual(len(new_lines), 1, "Computer should choose a scoring move")
        #apply move blue +1 points
        self.game.place_letter(row, col, letter)
        self.assertFalse(self.game.is_over)
        self.assertGreaterEqual(self.game.blue_score, 1)
        self.assertEqual(
            self.game.blue_score,
            sum(1 for seg in self.game.lines if seg.player == Player.BLUE),
        )
