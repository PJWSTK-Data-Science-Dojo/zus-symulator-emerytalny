import pandas as pd
from dataclasses import dataclass
from typing import Dict

@dataclass
class WageIndexation:
    year: int
    wage: float
    wage_index: float


class WageIndexationEngine:
    def __init__(self, history_path: str):
        """
        Engine for wage indexation using historical data.
        """
        self.history_path = history_path # path to historical wages CSV (columns: year, wage)
        self.df_history = pd.read_csv(history_path)

        # ensure proper ordering
        self.df_history = self.df_history.sort_values("year").reset_index(drop=True)

    def build_indices(self) -> pd.DataFrame:
        """
        Compute wage growth indices year to year.
        """
        df = self.df_history.copy()
        df["prev_wage"] = df["wage"].shift(1)
        df["wage_index"] = (df["wage"] / df["prev_wage"]).fillna(1.0)

        # floor at 1.0 (no negative or <1 growth in simulation)
        df["wage_index"] = df["wage_index"].apply(lambda x: max(x, 1.0))

        return df[["year", "wage", "wage_index"]]

    def project_user_wages(self, start_year: int, base_wage: float, end_year: int) -> Dict[int, float]:
        """
        Project user wages using historical indices.
        If end_year > max(year in history), the projection stops at last historical year.
        :param start_year: year when user starts
        :param base_wage: current wage (user input)
        :param end_year: last year for projection
        :return: dict {year: projected_wage}
        """
        df_idx = self.build_indices()
        df_idx = df_idx[df_idx["year"] >= start_year]

        wages = {}
        wage = base_wage

        for _, row in df_idx.iterrows():
            if row["year"] > end_year:
                break
            factor = row["wage_index"]
            wage = round(wage * factor, 2)
            wages[int(row["year"])] = wage

        return wages
