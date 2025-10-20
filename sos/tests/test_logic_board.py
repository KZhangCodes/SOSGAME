import unittest
from sos_logic import Board, InvalidBoardSizeError, MIN_N, MAX_N

class TestBoardSize(unittest.TestCase):
    def test_valid_selection(self):
        for n in range(MIN_N, MAX_N+1):
            b = Board(n)
            self.assertEqual(len(b.grid), n)
            self.assertEqual(len(b.grid[0]), n)

    def test_too_small(self):
        with self.assertRaises(InvalidBoardSizeError):
            Board(2)

    def test_too_large(self):
        with self.assertRaises(InvalidBoardSizeError):
            Board(MAX_N + 1)

    def test_non_integer(self):
        with self.assertRaises(InvalidBoardSizeError):
            Board("5")

class TestBoardInit(unittest.TestCase):
    def test_cells_start_empty(self):
        n = 5
        b = Board(n)
        for r in range(n):
            for c in range(n):
                self.assertIsNone(b.grid[r][c]), f"Expected None at ({r}, {c})"

if __name__ == '__main__':
    unittest.main()
