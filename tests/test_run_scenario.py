import unittest
import run_scenario

class TestRouter(unittest.TestCase):
    def test_test(self):
        expected    = 1
        actual      = 1
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()