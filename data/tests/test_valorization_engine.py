import unittest
import tempfile
import os
import math
import pandas as pd

from data.src.valorization_engine import (
    DataPaths,
    ForecastData,
    ValorizationIndexBuilder,
    ValorizationEngine,
    ValorizationInputs,
)


class TestValorizationEngine(unittest.TestCase):
    def setUp(self):
        # Temporary directory with mini-CSV
        self.tmpdir = tempfile.TemporaryDirectory()
        td = self.tmpdir.name

        # revenues (contributions)
        # Years: 2024:100, 2025:120 (+20%), 2026:108 (-10% -> lower bound 1.0)
        revenues_df = pd.DataFrame({
            "rok": [2024, 2025, 2026],
            "wariant_1": [100.0, 120.0, 108.0],
            "wariant_2": [100.0, 120.0, 108.0],
            "wariant_3": [100.0, 120.0, 108.0],
        })
        self.revenues_path = os.path.join(td, "wplywy_skladkowe_mln_zl.csv")
        revenues_df.to_csv(self.revenues_path, index=False)

        # macro (variant 1/2/3)
        # Constant factors CPI=1.05 (105.0) i real GDP=1.02 (102.0)
        # for years 2020..2026, so that the sub-account has 5 previous years for 2025 and 2026
        macro_years = list(range(2020, 2027))
        macro_df = pd.DataFrame({
            "rok": macro_years,
            "stopa_bezrobocia": [5.0] * len(macro_years),
            "inflacja_ogolna": [105.0] * len(macro_years),          # -> cpi_factor = 1.05
            "inflacja_emeryci": [105.0] * len(macro_years),
            "realny_wzrost_wynagrodzen": [102.0] * len(macro_years),
            "realny_wzrost_PKB": [102.0] * len(macro_years),        # -> real_gdp_factor = 1.02
            "sciagalnosc_skladek": [99.0] * len(macro_years),
        })
        # Save the same grid for 3 variants (we are not testing the differences between variants here)
        self.macro1_path = os.path.join(td, "parametry_makroekonomiczne_wariant_1.csv")
        self.macro2_path = os.path.join(td, "parametry_makroekonomiczne_wariant_2.csv")
        self.macro3_path = os.path.join(td, "parametry_makroekonomiczne_wariant_3.csv")
        macro_df.to_csv(self.macro1_path, index=False)
        macro_df.to_csv(self.macro2_path, index=False)
        macro_df.to_csv(self.macro3_path, index=False)

        # Build objects from your module
        self.paths = DataPaths(
            macro_variant_1=self.macro1_path,
            macro_variant_2=self.macro2_path,
            macro_variant_3=self.macro3_path,
            revenues=self.revenues_path,
        )
        self.data = ForecastData(self.paths)
        self.builder = ValorizationIndexBuilder(self.data)
        self.engine = ValorizationEngine(self.builder)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_account_index_formula(self):
        """account_index should be revenues[t] / revenues[t-1] with floor 1.0"""
        idx = self.builder.build_account_and_initial_capital_indices(variant=1)
        # 2025: 120/100 = 1.2
        i_2025 = float(idx.loc[idx["rok"] == 2025, "account_index"].iloc[0])
        self.assertAlmostEqual(i_2025, 1.2, places=6)

        # 2026: 108/120 = 0.9 -> floor 1.0
        i_2026 = float(idx.loc[idx["rok"] == 2026, "account_index"].iloc[0])
        self.assertAlmostEqual(i_2026, 1.0, places=6)

        # initial_capital_index == account_index
        cap_2025 = float(idx.loc[idx["rok"] == 2025, "initial_capital_index"].iloc[0])
        self.assertAlmostEqual(cap_2025, i_2025, places=6)

    # 5-year geometric mean of nominal GDP
    def test_subaccount_index_formula(self):
        """
        nominal_gdp_factor = cpi_factor * real_gdp_factor
        1.05 * 1.02 = 1.071
        For 2026 we take the years 2021..2025 (5 previous ones), so the geom. average = 1.071
        """
        sub = self.builder.build_subaccount_indices(variant=1)
        i_2026 = float(sub.loc[sub["rok"] == 2026, "subaccount_index"].iloc[0])
        self.assertAlmostEqual(i_2026, 1.05 * 1.02, places=6)

    def test_subaccount_flooring(self):
        """When the previous 5 years have nominal_gdp_factor < 1.0, the index should be 1.0 (floor)."""
        # We overwrite the variant_1 macro with a file with values ​​< 100 (i.e. < 1.0 after conversion)
        td = self.tmpdir.name
        bad_macro_df = pd.DataFrame({
            "rok": [2019, 2020, 2021, 2022, 2023, 2024, 2025],
            "stopa_bezrobocia": [5.0] * 7,
            "inflacja_ogolna": [99.0] * 7,                # 0.99
            "inflacja_emeryci": [99.0] * 7,
            "realny_wzrost_wynagrodzen": [99.0] * 7,
            "realny_wzrost_PKB": [99.0] * 7,              # 0.99
            "sciagalnosc_skladek": [99.0] * 7,
        })
        bad_macro_path = os.path.join(td, "parametry_makroekonomiczne_wariant_1_bad.csv")
        bad_macro_df.to_csv(bad_macro_path, index=False)

        # Replace the path only for variant 1 and recalculate
        paths2 = DataPaths(
            macro_variant_1=bad_macro_path,
            macro_variant_2=self.macro2_path,
            macro_variant_3=self.macro3_path,
            revenues=self.revenues_path,
        )
        data2 = ForecastData(paths2)
        builder2 = ValorizationIndexBuilder(data2)
        sub2 = builder2.build_subaccount_indices(variant=1)

        # Year 2025 will use window 2020..2024 -> all < 1.0, so floor = 1.0
        i_2025 = float(sub2.loc[sub2["rok"] == 2025, "subaccount_index"].iloc[0])
        self.assertEqual(i_2025, 1.0)

    def test_apply_valorization_balances(self):
        """
        We check the multiplication of balances by annual indices.
        Account: 2025 (1.2), 2026 (1.0)  => account_final = 1000 * 1.2 * 1.0 = 1200
        Initial capital: same as account
        Subaccount: for 2025 i 2026 index = 1.071 (from permanent data), so:
                  sub_final = 200 * 1.071 * 1.071
        """
        inputs = ValorizationInputs(
            start_year=2025,
            end_year=2026,
            variant=1,
            opening_account=1000.0,
            opening_initial_capital=500.0,
            opening_subaccount=200.0,
        )
        result = self.engine.apply_valorization(inputs)

        # Account and initial capital
        self.assertAlmostEqual(result.final_account, 1200.0, places=2)
        self.assertAlmostEqual(result.final_initial_capital, 600.0, places=2)  # 500 * 1.2 * 1.0

        # Subaccount: 200 * 1.071 * 1.071 (rounding to 2 places for each year in engine)
        # Engine rounds the states to 2 places after each year, so let's count the same way
        sub_2025 = round(200.0 * (1.05 * 1.02), 2)
        sub_2026 = round(sub_2025 * (1.05 * 1.02), 2)
        self.assertAlmostEqual(result.final_subaccount, sub_2026, places=2)

        # Check that the year rows have the correct years and columns
        years = result.yearly_balances["rok"].tolist()
        self.assertEqual(years, [2025, 2026])
        for col in ["account", "initial_capital", "subaccount"]:
            self.assertIn(col, result.yearly_balances.columns)

    def test_indices_table_contains_all_series(self):
        """Verifying that build_indices_table(variant) returns 3 indexes for each year."""
        idx = self.engine.build_indices_table(variant=1)
        for col in ["account_index", "initial_capital_index", "subaccount_index"]:
            self.assertIn(col, idx.columns)
        self.assertGreaterEqual(idx["rok"].min(), 2020)
        self.assertGreaterEqual(idx["rok"].max(), 2026)


if __name__ == "__main__":
    unittest.main()
