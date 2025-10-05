import unittest
import pandas as pd
from unittest.mock import MagicMock
from data.src.macro_scenarios import MacroScenarioAnalyzer

class TestMacroScenarioAnalyzer(unittest.TestCase):

    def setUp(self):
        df_base = pd.DataFrame({
            "rok": [2024, 2025, 2026],
            "cpi_factor": [1.05, 1.03, 1.02],
            "real_gdp_factor": [1.02, 1.01, 1.00],
            "nominal_gdp_factor": [1.07, 1.04, 1.02]
        })

        self.mock_forecast = MagicMock()
        self.mock_forecast.load_macro.side_effect = lambda v: df_base.copy()

        self.analyzer = MacroScenarioAnalyzer(self.mock_forecast)

    def test_compare_inflation_scenarios_returns_three_variants(self):
        df = self.analyzer.compare_inflation_scenarios()
        variants = df["variant"].unique()
        self.assertEqual(set(variants), {1, 2, 3})
        self.assertIn("cpi_factor", df.columns)
        self.assertIn("real_gdp_factor", df.columns)

    def test_summarize_by_year_returns_expected_columns(self):
        summary = self.analyzer.summarize_by_year()
        expected_cols = {
            "rok",
            "cpi_factor_min",
            "cpi_factor_max",
            "cpi_factor_mean",
            "real_gdp_factor_min",
            "real_gdp_factor_max",
            "real_gdp_factor_mean"
        }
        self.assertEqual(set(summary.columns), expected_cols)

    def test_summarize_values_are_correct(self):
        summary = self.analyzer.summarize_by_year()
        self.assertTrue((summary["cpi_factor_min"] == summary["cpi_factor_max"]).all())
        self.assertTrue(summary["real_gdp_factor_mean"].isin([1.00, 1.01, 1.02]).all())

    def test_handles_multiple_years(self):
        summary = self.analyzer.summarize_by_year()
        self.assertGreaterEqual(len(summary), 3)
        self.assertTrue((summary["rok"] == [2024, 2025, 2026]).any())

if __name__ == "__main__":
    unittest.main()
