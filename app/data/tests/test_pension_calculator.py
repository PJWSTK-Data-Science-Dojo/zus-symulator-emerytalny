import unittest

from functionalities.pension_calculator import PensionCalculator, PensionInputs


class TestPensionCalculator(unittest.TestCase):
    def test_basic_case(self):
        inputs = PensionInputs(300000, 100000, 50000, 240)
        result = PensionCalculator.calculate_pension(inputs)
        self.assertEqual(result, 1875.0)  # 450000 / 240 = 1875

    def test_zero_life_expectancy(self):
        inputs = PensionInputs(300000, 100000, 50000, 0)
        result = PensionCalculator.calculate_pension(inputs)
        self.assertEqual(result, 7500)  # 450000 / 60 = 7500

    def test_old_people(self):
        inputs = PensionInputs(300000, 100000, 50000, 30)
        result = PensionCalculator.calculate_pension(inputs)
        self.assertEqual(result, 7500)  # 450000 / 60 = 7500


if __name__ == "__main__":
    unittest.main()
