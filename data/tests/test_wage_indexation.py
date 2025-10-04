import os
import tempfile
import unittest

import pandas as pd
from src.wage_indexation import WageIndexationEngine


class TestWageIndexationEngine(unittest.TestCase):
    def setUp(self):
        # Twemporary CSV with historical data
        self.tmpdir = tempfile.TemporaryDirectory()
        self.csv_path = os.path.join(self.tmpdir.name, "test_wages.csv")

        df = pd.DataFrame(
            {"year": [2020, 2021, 2022, 2023], "wage": [5000.00, 5500.00, 5000.00, 6000.00]}
        )
        df.to_csv(self.csv_path, index=False)

        self.engine = WageIndexationEngine(self.csv_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_build_indices(self):
        df_indices = self.engine.build_indices()

        # Check number of rows
        self.assertEqual(len(df_indices), 4)

        # 2021: 5500/5000 = 1.1
        idx_2021 = df_indices.loc[df_indices["year"] == 2021, "wage_index"].iloc[0]
        self.assertAlmostEqual(idx_2021, 1.1, places=4)

        # 2022: 5000/5500 = 0.909 → ale floor = 1.0
        idx_2022 = df_indices.loc[df_indices["year"] == 2022, "wage_index"].iloc[0]
        self.assertEqual(idx_2022, 1.0)

    def test_project_user_wages(self):
        projection = self.engine.project_user_wages(start_year=2020, base_wage=4000, end_year=2023)

        # 2020 should be the first year = base salary
        self.assertIn(2020, projection)

        # 2021: 4000 * 1.1 = 4400
        self.assertAlmostEqual(projection[2021], 4400.0, places=2)

        # 2022: decline, but floor = 1.0 → still 4400
        self.assertAlmostEqual(projection[2022], 4400.0, places=2)

        # 2023: increase 6000/5000 = 1.2 → 4400 * 1.2 = 5280
        self.assertAlmostEqual(projection[2023], 5280.0, places=2)


if __name__ == "__main__":
    unittest.main()
