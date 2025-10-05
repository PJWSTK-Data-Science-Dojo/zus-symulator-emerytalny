import unittest
import pandas as pd
from unittest.mock import patch
from data.src.inflation_projection import InflationProjection

class TestInflationProjection(unittest.TestCase):

    def setUp(self):
        self.macro_paths = {
            1: "data/dane_emerytalne/parametry_makroekonomiczne_wariant_1.csv",
            2: "data/dane_emerytalne/parametry_makroekonomiczne_wariant_2.csv",
            3: "data/dane_emerytalne/parametry_makroekonomiczne_wariant_3.csv"
        }
        self.projection = InflationProjection(self.macro_paths)

    @patch.object(InflationProjection, "load_data")
    def test_cumulative_inflation_correct(self, mock_load):
        # Dane testowe: inflacja 105%, 103%, 104%
        mock_load.return_value = pd.DataFrame({
            "rok": [2024, 2025, 2026],
            "inflacja_ogolna": [105, 103, 104],
            "inflation_factor": [1.05, 1.03, 1.04]
        })

        result = self.projection.cumulative_inflation(1, 2024, 2026)
        expected = 1.05 * 1.03 * 1.04
        self.assertAlmostEqual(result, expected, places=5)

    @patch.object(InflationProjection, "load_data")
    def test_project_price_returns_correct_value(self, mock_load):
        mock_load.return_value = pd.DataFrame({
            "rok": [2024, 2025],
            "inflacja_ogolna": [105, 103],
            "inflation_factor": [1.05, 1.03]
        })

        result = self.projection.project_price(1, 2024, 2025, 1000)
        expected = round(1000 * 1.05 * 1.03, 2)
        self.assertEqual(result, expected)

    @patch.object(InflationProjection, "load_data")
    def test_raises_error_for_missing_years(self, mock_load):
        mock_load.return_value = pd.DataFrame({
            "rok": [2020, 2021],
            "inflacja_ogolna": [102, 101],
            "inflation_factor": [1.02, 1.01]
        })
        with self.assertRaises(ValueError):
            self.projection.cumulative_inflation(1, 2024, 2026)

    def test_load_data_reads_and_transforms_properly(self):
        # Symulacja danych z CSV
        df_mock = pd.DataFrame({
            "rok": [2024, 2025],
            "inflacja_ogolna": [105, 103]
        })
        with patch("pandas.read_csv", return_value=df_mock):
            df_loaded = self.projection.load_data(1)
            self.assertIn("inflation_factor", df_loaded.columns)
            self.assertAlmostEqual(df_loaded.loc[0, "inflation_factor"], 1.05)

    @patch.object(InflationProjection, "load_data")
    def test_multiple_variants_handled(self, mock_load):
        mock_load.return_value = pd.DataFrame({
            "rok": [2024, 2025, 2026],
            "inflacja_ogolna": [102, 103, 104],
            "inflation_factor": [1.02, 1.03, 1.04]
        })
        for variant in [1, 2, 3]:
            result = self.projection.cumulative_inflation(variant, 2024, 2026)
            self.assertGreater(result, 1.0)


if __name__ == "__main__":
    unittest.main()
