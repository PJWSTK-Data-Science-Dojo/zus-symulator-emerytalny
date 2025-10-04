import unittest
import pandas as pd
import sys
import os
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.src.life_expectancy_calculator import LifeExpectancyCalculator

class TestLifeExpectancyCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = LifeExpectancyCalculator("data/dane_emerytalne/tablice_trwania_zycia_w_latach_1990-2022.xlsx")

    @patch.object(LifeExpectancyCalculator, "_load_year_data")
    def test_get_life_expectancy_returns_correct_value(self, mock_load):
        df = pd.DataFrame({
            "age": [60, 61, 62],
            "male": [19.1, 18.5, 17.9],
            "female": [23.5, 22.8, 22.2]
        })
        mock_load.return_value = df

        result_m = self.calc.get_life_expectancy(2022, 61, "m")
        result_k = self.calc.get_life_expectancy(2022, 62, "k")

        self.assertAlmostEqual(result_m, 18.5)
        self.assertAlmostEqual(result_k, 22.2)

    @patch.object(LifeExpectancyCalculator, "get_life_expectancy")
    def test_calculate_required_extra_years_increases_with_lower_pension(self, mock_life_exp):
        mock_life_exp.return_value = 20.0  # simulated life expectancy

        expected = 5000
        forecasted = 4000
        result = self.calc.calculate_required_extra_years(expected, forecasted, 65, "k", 2022)

        # 5000/4000 = 1.25 → (1.25 - 1.0) / 0.05 = 5.0
        self.assertAlmostEqual(result, 5.0, places=1)

    @patch.object(LifeExpectancyCalculator, "get_life_expectancy")
    def test_no_extra_years_when_expected_lower_than_forecasted(self, mock_life_exp):
        mock_life_exp.return_value = 20.0

        expected = 3500
        forecasted = 4000
        result = self.calc.calculate_required_extra_years(expected, forecasted, 65, "m", 2022)

        self.assertEqual(result, 0)

    @patch.object(LifeExpectancyCalculator, "get_life_expectancy")
    def test_returns_latest_year_if_not_specified(self, mock_life_exp):
        mock_life_exp.return_value = 18.0
        self.calc.latest_year = 2022

        result = self.calc.calculate_required_extra_years(5000, 4000, 65, "m")

        self.assertGreater(result, 0)
        mock_life_exp.assert_called_once_with(2022, 65, "m")

    def test_latest_year_detected_correctly(self):
        calc = LifeExpectancyCalculator("data/dane_emerytalne/tablice_trwania_zycia_w_latach_1990-2022.xlsx")
        self.assertEqual(calc.latest_year, 2022)


if __name__ == "__main__":
    unittest.main()
