import unittest

from sos_logic import (SIMPLE, GENERAL, MODES, Game, Board,
    InvalidMoveError, MIN_N, DEFAULT_STARTING_PLAYER, InvalidLetterError, InvalidGameModeError,
                       OutOfBoundsError, validate_mode, RED_PLAYER, BLUE_PLAYER)

class TestGameMode(unittest.TestCase):
    def test_valid_modes(self):
        self.assertEqual(set(MODES), {SIMPLE, GENERAL})

class TestGameInit(unittest.TestCase):
    def test_game_init(self):
        g = Game(board_size=MIN_N, mode=SIMPLE, starting_player=BLUE_PLAYER)
        self.assertEqual(g.board.board_size, MIN_N)
        self.assertIsInstance(g.board, Board)
        self.assertEqual(g.current_player, BLUE_PLAYER)

class TestGameCellAndMoves(unittest.TestCase):
    def setUp(self):
        self.g = Game(board_size=3, mode=SIMPLE, starting_player=DEFAULT_STARTING_PLAYER)

    def test_cell_empty_init(self):
        self.assertTrue(self.g.cell_is_empty(0,0))
        self.assertTrue(self.g.cell_is_empty(2,2))

    def test_place_letter_and_switch_turn(self):
        #red player S
        self.g.place_letter(0, 0, "S")
        self.assertEqual(self.g.board.grid[0][0], "S")
        self.assertEqual(self.g.current_player, BLUE_PLAYER)  # switch
        #blue player o
        self.g.place_letter(1, 1, "O")
        self.assertEqual(self.g.board.grid[1][1], "O")
        self.assertEqual(self.g.current_player, RED_PLAYER) #switch

    def test_cannot_place_on_occupied_cell(self):
        self.g.place_letter(0, 0, "S")
        with self.assertRaises(InvalidMoveError):
            self.g.place_letter(0, 0, "O")

#LLM generated unit test 1
class TestModeNormalization(unittest.TestCase):
    def test_mode_normalization(self):
        cases = {
            "SIMPLE": SIMPLE,
            " simple ": SIMPLE,
            "Simple": SIMPLE,
            "\nGENERAL\t": GENERAL,
            "GeNeRaL": GENERAL,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(validate_mode(raw), expected)

#LLM generated unit test 2
class TestInvalidStartingPlayer(unittest.TestCase):
    def test_invalid_starting_player(self):
        # Any value not in (1, 2) should raise ValueError
        for bad_player in [0, 3, -1, None, "A"]:
            with self.subTest(bad_player=bad_player):
                with self.assertRaises(ValueError):
                    Game(board_size=3, mode=SIMPLE, starting_player=bad_player)

class TestInvalidMovesAndLetters(unittest.TestCase):
    def setUp(self):
        self.g = Game(board_size=3, mode=SIMPLE, starting_player=DEFAULT_STARTING_PLAYER)

    def test_out_of_bounds(self):
        with self.assertRaises(OutOfBoundsError):
            self.g.place_letter(-1, 0, "O")
        with self.assertRaises(OutOfBoundsError):
            self.g.place_letter(0, 3, "O")

    def test_invalid_letter(self):
        with self.assertRaises(InvalidLetterError):
            self.g.place_letter(0, 0, "X")

#logic/gui doesnt allow, for ac 3.2/2.1
class TestInvalidMode(unittest.TestCase):
    def test_invalid_mode(self):
        with self.assertRaises(InvalidGameModeError):
            Game(board_size=3, mode="SUDDEN_DEATH")

if __name__ == '__main__':
    unittest.main()
