import unittest
from data.src.replacement_rate import ReplacementRateCalculator


class TestReplacementRateCalculator(unittest.TestCase):

    def test_low_replacement_rate(self):
        result = ReplacementRateCalculator.calculate(pension=2000, last_wage=8000)
        self.assertLess(result.rate_percent, 40)
        self.assertIn("niski", result.message.lower())

    def test_medium_replacement_rate(self):
        result = ReplacementRateCalculator.calculate(pension=4000, last_wage=8000)
        self.assertGreaterEqual(result.rate_percent, 40)
        self.assertLess(result.rate_percent, 70)
        self.assertIn("umiarkowany", result.message.lower())

    def test_high_replacement_rate(self):
        result = ReplacementRateCalculator.calculate(pension=6000, last_wage=8000)
        self.assertGreaterEqual(result.rate_percent, 70)
        self.assertIn("wysoki", result.message.lower())

    def test_zero_last_wage(self):
        result = ReplacementRateCalculator.calculate(pension=3000, last_wage=0)
        self.assertEqual(result.rate_percent, 0.0)
        self.assertIsInstance(result.message, str)


if __name__ == "__main__":
    unittest.main()
