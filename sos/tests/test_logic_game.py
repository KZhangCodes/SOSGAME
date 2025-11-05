import unittest

from sos_logic import (Mode, start_game, Board,
    InvalidMoveError, MIN_N, DEFAULT_STARTING_PLAYER, InvalidLetterError, InvalidGameModeError,
                       OutOfBoundsError, validate_mode, Player)

class TestGameMode(unittest.TestCase):
    def test_valid_modes(self):
        self.assertEqual({m for m in Mode}, {Mode.SIMPLE, Mode.GENERAL})

class TestGameInit(unittest.TestCase):
    def test_game_init(self):
        g = start_game(board_size=MIN_N, mode=Mode.SIMPLE, starting_player=Player.BLUE)
        self.assertEqual(g.board.board_size, MIN_N)
        self.assertIsInstance(g.board, Board)
        self.assertEqual(g.current_player, Player.BLUE)

class TestGameCellAndMoves(unittest.TestCase):
    def setUp(self):
        self.g = start_game(board_size=3, mode=Mode.SIMPLE, starting_player=DEFAULT_STARTING_PLAYER)

    def test_cell_empty_init(self):
        self.assertTrue(self.g.board.is_empty(0,0))
        self.assertTrue(self.g.board.is_empty(2,2))

    def test_place_letter_and_switch_turn(self):
        #red player S
        self.g.place_letter(0, 0, "S")
        self.assertEqual(self.g.board.grid[0][0], "S")
        self.assertEqual(self.g.current_player, Player.BLUE)  # switch
        #blue player o
        self.g.place_letter(1, 1, "O")
        self.assertEqual(self.g.board.grid[1][1], "O")
        self.assertEqual(self.g.current_player, Player.RED) #switch

    def test_cannot_place_on_occupied_cell(self):
        self.g.place_letter(0, 0, "S")
        with self.assertRaises(InvalidMoveError):
            self.g.place_letter(0, 0, "O")

#LLM generated unit test 1
class TestModeNormalization(unittest.TestCase):
    def test_mode_normalization(self):
        cases = {
            "SIMPLE": Mode.SIMPLE,
            " simple ": Mode.SIMPLE,
            "Simple": Mode.SIMPLE,
            "\nGENERAL\t": Mode.GENERAL,
            "GeNeRaL": Mode.GENERAL,
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
                    start_game(board_size=3, mode=Mode.SIMPLE, starting_player=bad_player)

class TestInvalidMovesAndLetters(unittest.TestCase):
    def setUp(self):
        self.g = start_game(board_size=3, mode=Mode.SIMPLE, starting_player=DEFAULT_STARTING_PLAYER)

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
            start_game(board_size=3, mode="SUDDEN_DEATH")

#user story 5: simple game is over
class TestSimpleGameEnds(unittest.TestCase):
    def setUp(self):
        self.g = start_game(board_size=3, mode=Mode.SIMPLE, starting_player=Player.RED)
    #AC 5.1
    def test_simple_winner_on_sos(self):
        #red: s(0,0), blue: o(0,1), red: s(0,2)
        self.g.place_letter(0, 0, "S")
        self.g.place_letter(0, 1, "O")
        self.g.place_letter(0, 2, "S")

        self.assertTrue(self.g.is_over)
        self.assertEqual(self.g.winner, Player.RED)
        #no turn swift after game over
        self.assertEqual(self.g.current_player, Player.RED)
        self.assertEqual(len(self.g.lines), 1)
        segment = self.g.lines[0]
        self.assertEqual(segment.start, (0, 0))
        self.assertEqual(segment.end, (0, 2))
        self.assertEqual(segment.player, Player.RED)
    #AC 5.2
    def test_simple_draw(self):
        #3x3 all o no sos
        moves = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2),
        ]
        for row, col in moves:
            self.g.place_letter(row, col, "O")

        self.assertTrue(self.g.is_over)
        self.assertIsNone(self.g.winner)
        self.assertEqual(len(self.g.lines), 0)
    #AC 5.3
    def test_simple_reset(self):
        #end simple with red sos
        self.g.place_letter(0, 0, "S")
        self.g.place_letter(0, 1, "O")
        self.g.place_letter(0, 2, "S")
        self.assertTrue(self.g.is_over)
        #start new simple game with different size
        game2 = start_game(board_size=4, mode=Mode.SIMPLE, starting_player=Player.RED)
        self.assertFalse(game2.is_over)
        self.assertIsNone(game2.winner)
        self.assertEqual(game2.red_score, 0)
        self.assertEqual(game2.blue_score, 0)
        self.assertEqual(len(game2.lines), 0)
        self.assertEqual(game2.board.board_size, 4)
        self.assertEqual(game2.current_player, Player.RED)

#user story 7: general game is over
class TestGeneralGameEnds(unittest.TestCase):
    def setUp(self):
        self.g = start_game(board_size=3, mode=Mode.GENERAL, starting_player=Player.RED)
    #AC 7.1
    def test_general_winner_filled_board(self):
        #red: s(0,0), blue: o(0,1), red: s(0,2), rest o
        self.g.place_letter(0, 0, "S")
        self.g.place_letter(0, 1, "O")
        self.g.place_letter(0, 2, "S")

        moves = [
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2),
        ]
        #alternate with o
        letters = ["O"] * len(moves)
        for (row, col), letter in zip(moves, letters):
            self.g.place_letter(row, col, letter)

        self.assertTrue(self.g.is_over)
        self.assertEqual(self.g.red_score, 1)
        self.assertEqual(self.g.blue_score, 0)
        self.assertEqual(self.g.winner, Player.RED)
    #AC 7.2
    def test_general_draw_event(self):
        #fill with all o
        moves = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2),
        ]
        for row, col in moves:
            self.g.place_letter(row, col, "O")

        self.assertTrue(self.g.is_over)
        self.assertEqual(self.g.red_score, 0)
        self.assertEqual(self.g.blue_score, 0)
        self.assertIsNone(self.g.winner)
    #AC 7.3
    def test_general_reset(self):
        #full board with no SOS
        for row, col in [(row, col) for row in range(3) for col in range(3)]:
            self.g.place_letter(row, col, "O")
        self.assertTrue(self.g.is_over)
        #start new general game with different size
        game2 = start_game(board_size=5, mode=Mode.GENERAL, starting_player=Player.RED)
        self.assertFalse(game2.is_over)
        self.assertIsNone(game2.winner)
        self.assertEqual(game2.red_score, 0)
        self.assertEqual(game2.blue_score, 0)
        self.assertEqual(len(game2.lines), 0)
        self.assertEqual(game2.board.board_size, 5)
        self.assertEqual(game2.current_player, Player.RED)

#line segment test
class TestCompletedSOSSegment(unittest.TestCase):
    def setUp(self):
        self.g = start_game(board_size=3, mode=Mode.SIMPLE, starting_player=Player.RED)
    #horizontal sos, segment owner and endpoints
    def test_horizontal_and_endpoints(self):
        self.g.place_letter(0, 0, "S")
        self.g.place_letter(0, 1, "O")
        self.g.place_letter(0, 2, "S")

        self.assertTrue(self.g.is_over)
        self.assertEqual(len(self.g.lines), 1)

        segment = self.g.lines[0]
        self.assertEqual(segment.start, (0, 0))
        self.assertEqual(segment.end, (0, 2))
        self.assertEqual(segment.player, Player.RED)

if __name__ == '__main__':
    unittest.main()
