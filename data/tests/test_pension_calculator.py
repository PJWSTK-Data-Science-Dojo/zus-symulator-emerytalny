import unittest
from data.src.pension_calculator import PensionInputs, PensionCalculator

class TestPensionCalculator(unittest.TestCase):
    def test_basic_case(self):
        inputs = PensionInputs(300000, 100000, 50000, 240)
        result = PensionCalculator.calculate_pension(inputs)
        self.assertEqual(result, 1875.0)  # 450000 / 240 = 1875

    def test_zero_life_expectancy(self):
        inputs = PensionInputs(300000, 100000, 50000, 0)
        with self.assertRaises(ValueError):
            PensionCalculator.calculate_pension(inputs)

if __name__ == "__main__":
    unittest.main()

