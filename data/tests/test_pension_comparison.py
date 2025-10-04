import unittest

from src.pension_comparison import PensionComparison


class TestPensionComparison(unittest.TestCase):
    def test_forecasted_higher_than_expected(self):
        result = PensionComparison.compare(expected=3000, forecasted=4000)
        self.assertEqual(result.expected, 3000)
        self.assertEqual(result.forecasted, 4000)
        self.assertGreaterEqual(result.forecasted, result.expected)
        self.assertIn("wyższa", result.message)

    def test_forecasted_lower_than_expected(self):
        result = PensionComparison.compare(expected=5000, forecasted=3500)
        self.assertEqual(result.expected, 5000)
        self.assertEqual(result.forecasted, 3500)
        self.assertLess(result.forecasted, result.expected)
        self.assertIn("niższa", result.message)
        self.assertGreater(result.difference, 0)

    def test_forecasted_equal_to_expected(self):
        result = PensionComparison.compare(expected=4000, forecasted=4000)
        self.assertEqual(result.expected, 4000)
        self.assertEqual(result.forecasted, 4000)
        self.assertEqual(result.difference, 0)
        self.assertAlmostEqual(result.percentage, 100.0)
        self.assertIn("równa", result.message)


if __name__ == "__main__":
    unittest.main()
