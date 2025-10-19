import unittest
from sos_logic import SIMPLE, GENERAL, MODES, DEFAULT_MODE, start_default_mode

class TestGameMode(unittest.TestCase):
    def test_default_simple(self):
        self.assertEqual(DEFAULT_MODE, SIMPLE)
        self.assertEqual(start_default_mode(), SIMPLE)

    def test_valid_modes(self):
        self.assertEqual(set(MODES), {SIMPLE, GENERAL})
        self.assertEqual(len(MODES), 2)

if __name__ == '__main__':
    unittest.main()
