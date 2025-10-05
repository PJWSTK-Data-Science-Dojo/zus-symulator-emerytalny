import unittest
from data.src.sick_leave_adjustment import SickLeaveAdjustment, SickLeaveResult


class TestSickLeaveAdjustment(unittest.TestCase):

    def setUp(self):
        self.calc = SickLeaveAdjustment()  # domyślny współczynnik 0.9

    def test_basic_calculation(self):
        result = self.calc.calculate(5000)
        self.assertIsInstance(result, SickLeaveResult)
        self.assertAlmostEqual(result.base_pension, 5000.0)
        self.assertAlmostEqual(result.adjusted_pension, 4500.0)
        self.assertAlmostEqual(result.difference, 500.0)

    def test_custom_reduction_factor(self):
        calc = SickLeaveAdjustment(reduction_factor=0.85)
        result = calc.calculate(4000)
        self.assertAlmostEqual(result.adjusted_pension, 3400.0)
        self.assertAlmostEqual(result.difference, 600.0)

    def test_invalid_reduction_factor_raises_error(self):
        with self.assertRaises(ValueError):
            SickLeaveAdjustment(reduction_factor=1.5)
        with self.assertRaises(ValueError):
            SickLeaveAdjustment(reduction_factor=0)

    def test_negative_pension_raises_error(self):
        with self.assertRaises(ValueError):
            self.calc.calculate(-2000)

    def test_reduction_precision(self):
        """Standardowe zaokrąglenie do 2 miejsc (ROUND_HALF_UP) -> 3000.00."""
        result = self.calc.calculate(3333.33)
        self.assertEqual(result.adjusted_pension, 3000.00)
        self.assertEqual(result.difference, 333.33)


if __name__ == "__main__":
    unittest.main()
