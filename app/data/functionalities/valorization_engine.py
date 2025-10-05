from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple
import math
import pandas as pd
import numpy as np


Variant = Literal[1, 2, 3]


# Assumptions (transparent & tweakable)
#
# 1) Account & initial capital valorization:
#    Approximate yearly index = max(1.0, contributions_t / contributions_{t-1})
#    where contributions come from `wplywy_skladkowe_mln_zl.csv` (by variant).
#
# 2) Subaccount valorization:
#    Yearly index = 5-year geometric mean of NOMINAL GDP growth factors.
#    We approximate nominal GDP growth using:
#       nominal_gdp_growth_factor = (real_GDP_growth_index / 100) * (CPI_index / 100)
#    (CPI as a proxy for GDP deflator; transparent simplification for hackathon).
#    If fewer than 5 prior years exist, use geometric mean of available years.
#
# 3) Interpolation:
#    Macro & revenue tables have "milestone years" (e.g., 2035, 2040…).
#    We expand to a continuous yearly grid using linear interpolation
#    on the *indices in factor space* (not percent points).
#
# 4) Floors:
#    All valorization indices are floored at 1.0 (no de-valorization),
#    mirroring legal “not-below-100%” logic.

def _geom_mean(values: np.ndarray) -> float:
    """Geometric mean of positive factors."""
    vals = np.array(values, dtype=float)
    vals = vals[vals > 0]
    if len(vals) == 0:
        return 1.0
    return float(np.exp(np.log(vals).mean()))


def _interpolate_yearly_factors(df: pd.DataFrame, year_col: str, factor_cols: Tuple[str, ...]) -> pd.DataFrame:
    """
    Given a dataframe with sparse years and factor columns (e.g. 1.025 = +2.5%),
    return a continuous yearly index with linear interpolation in factor space.
    """
    df2 = df.copy().set_index(year_col).sort_index()
    full_index = pd.RangeIndex(df2.index.min(), df2.index.max() + 1, step=1)
    df2 = df2.reindex(full_index)
    # linear interpolation for each factor column
    for c in factor_cols:
        df2[c] = df2[c].interpolate(method="linear", limit_direction="both")
    df2.index.name = year_col
    return df2.reset_index()


# Data loaders
@dataclass
class DataPaths:
    macro_variant_1: str  # parametry_makroekonomiczne_wariant_1.csv
    macro_variant_2: str  # parametry_makroekonomiczne_wariant_2.csv
    macro_variant_3: str  # parametry_makroekonomiczne_wariant_3.csv
    revenues: str         # wplywy_skladkowe_mln_zl.csv


class ForecastData:
    def __init__(self, paths: DataPaths):
        self.paths = paths
        self._macro: Dict[Variant, pd.DataFrame] = {}
        self._revenues: Optional[pd.DataFrame] = None

    def load_macro(self, variant: Variant) -> pd.DataFrame:
        if variant in self._macro:
            return self._macro[variant]

        path = {
            1: self.paths.macro_variant_1,
            2: self.paths.macro_variant_2,
            3: self.paths.macro_variant_3,
        }[variant]

        df = pd.read_csv(path)
        # Expected columns:
        # rok, stopa_bezrobocia, inflacja_ogolna, inflacja_emeryci,
        # realny_wzrost_wynagrodzen, realny_wzrost_PKB, sciagalnosc_skladek
        # Convert index-like percents 102.5 => factor 1.025
        df["cpi_factor"] = df["inflacja_ogolna"] / 100.0
        df["real_gdp_factor"] = df["realny_wzrost_PKB"] / 100.0
        # Nominal GDP factor proxy
        df["nominal_gdp_factor"] = df["cpi_factor"] * df["real_gdp_factor"]

        # Keep only needed columns
        df = df[["rok", "cpi_factor", "real_gdp_factor", "nominal_gdp_factor"]].copy()
        self._macro[variant] = df
        return df

    def load_revenues(self) -> pd.DataFrame:
        if self._revenues is not None:
            return self._revenues
        df = pd.read_csv(self.paths.revenues)
        # columns: rok, wariant_1, wariant_2, wariant_3 (values in mln PLN)
        self._revenues = df
        return df


# Valorization index builders
class ValorizationIndexBuilder:
    """
    Builds yearly valorization indices for:
      - account
      - initial capital
      - subaccount
    based on forecast variant.
    """

    def __init__(self, data: ForecastData):
        self.data = data

    def build_account_and_initial_capital_indices(self, variant: Variant) -> pd.DataFrame:
        """
        Account & initial capital: index_t = max(1.0, revenues_t / revenues_{t-1})
        """
        rev = self.data.load_revenues().copy()
        col = {1: "wariant_1", 2: "wariant_2", 3: "wariant_3"}[variant]
        rev = rev[["rok", col]].rename(columns={col: "revenues"})
        rev = rev.sort_values("rok").reset_index(drop=True)

        rev["prev_revenues"] = rev["revenues"].shift(1)
        rev["account_index"] = (rev["revenues"] / rev["prev_revenues"]).fillna(1.0)
        rev["account_index"] = rev["account_index"].apply(lambda x: max(1.0, float(x)))

        # initial capital uses same index
        rev["initial_capital_index"] = rev["account_index"]

        # Interpolate to continuous years if needed (already yearly, but future-proof)
        out = _interpolate_yearly_factors(
            rev[["rok", "account_index", "initial_capital_index"]],
            "rok",
            ("account_index", "initial_capital_index"),
        )
        return out

    def build_subaccount_indices(self, variant: Variant) -> pd.DataFrame:
        """
        Subaccount: index_t = geometric mean of last up to 5 nominal GDP factors
        (using CPI * real GDP as a proxy for nominal GDP growth).
        Floor at 1.0.
        """
        macro = self.data.load_macro(variant).copy()
        macro = macro.sort_values("rok").reset_index(drop=True)

        # Interpolate nominal_gdp_factor to annual grid
        macro = _interpolate_yearly_factors(
            macro[["rok", "nominal_gdp_factor"]],
            "rok",
            ("nominal_gdp_factor",),
        )

        years = macro["rok"].tolist()
        ng = dict(zip(macro["rok"], macro["nominal_gdp_factor"]))

        rows = []
        for y in years:
            # window: previous 5 years available (y-5..y-1). If not available, use what we have.
            window_years = [t for t in range(y - 5, y) if t in ng]
            if len(window_years) == 0:
                # fallback: if early years, use current year's factor
                gm = ng.get(y, 1.0)
            else:
                gm = _geom_mean(np.array([ng[t] for t in window_years], dtype=float))

            idx = max(1.0, float(gm))
            rows.append({"rok": y, "subaccount_index": idx})

        return pd.DataFrame(rows)


# Valorization engine (apply indices to balances)
@dataclass
class ValorizationInputs:
    start_year: int
    end_year: int           # inclusive
    variant: Variant
    opening_account: float          # account balance for start_year at the end of the year (after indexation for start_year-1)
    opening_initial_capital: float  # indexed initial capital for start_year
    opening_subaccount: float       # subaccount balance at start_year


@dataclass
class ValorizationResult:
    final_account: float
    final_initial_capital: float
    final_subaccount: float
    yearly_indices: pd.DataFrame  # columns: rok, account_index, initial_capital_index, subaccount_index
    yearly_balances: pd.DataFrame # columns: rok, account, initial_capital, subaccount


class ValorizationEngine:
    def __init__(self, index_builder: ValorizationIndexBuilder):
        self.idx_builder = index_builder

    def build_indices_table(self, variant: Variant) -> pd.DataFrame:
        acc_df = self.idx_builder.build_account_and_initial_capital_indices(variant)
        sub_df = self.idx_builder.build_subaccount_indices(variant)
        idx = pd.merge(acc_df, sub_df, on="rok", how="outer").sort_values("rok").reset_index(drop=True)

        # Fill missing with 1.0 (safe default)
        for col in ["account_index", "initial_capital_index", "subaccount_index"]:
            if col not in idx:
                idx[col] = 1.0
            idx[col] = idx[col].fillna(1.0)
        return idx

    def apply_valorization(self, inputs: ValorizationInputs) -> ValorizationResult:
        idx = self.build_indices_table(inputs.variant)

        # Filter the index table to relevant years
        idx = idx[(idx["rok"] >= inputs.start_year) & (idx["rok"] <= inputs.end_year)].copy()

        account = inputs.opening_account
        initcap = inputs.opening_initial_capital
        subacc = inputs.opening_subaccount

        balances_rows = []
        for _, row in idx.iterrows():
            y = int(row["rok"])
            account *= float(row["account_index"])
            initcap *= float(row["initial_capital_index"])
            subacc *= float(row["subaccount_index"])
            balances_rows.append({
                "rok": y,
                "account": round(account, 2),
                "initial_capital": round(initcap, 2),
                "subaccount": round(subacc, 2),
            })

        balances_df = pd.DataFrame(balances_rows)
        return ValorizationResult(
            final_account=float(balances_df["account"].iloc[-1]) if not balances_df.empty else inputs.opening_account,
            final_initial_capital=float(balances_df["initial_capital"].iloc[-1]) if not balances_df.empty else inputs.opening_initial_capital,
            final_subaccount=float(balances_df["subaccount"].iloc[-1]) if not balances_df.empty else inputs.opening_subaccount,
            yearly_indices=idx.reset_index(drop=True),
            yearly_balances=balances_df.reset_index(drop=True),
        )


# Example usage (remove or guard under __main__ in production)
if __name__ == "__main__":
    # Paths to your CSVs (adjust to your repo structure)
    paths = DataPaths(
        macro_variant_1="parametry_makroekonomiczne_wariant_1.csv",
        macro_variant_2="parametry_makroekonomiczne_wariant_2.csv",
        macro_variant_3="parametry_makroekonomiczne_wariant_3.csv",
        revenues="wplywy_skladkowe_mln_zl.csv",
    )

    data = ForecastData(paths)
    builder = ValorizationIndexBuilder(data)
    engine = ValorizationEngine(builder)

    # Sample inputs (variant 1, valorize 2024..2030)
    inputs = ValorizationInputs(
        start_year=2024,
        end_year=2030,
        variant=1,
        opening_account=300_000.0,
        opening_initial_capital=120_000.0,
        opening_subaccount=60_000.0,
    )

    result = engine.apply_valorization(inputs)

    print("Final balances:")
    print("  Account:         ", result.final_account)
    print("  Initial capital: ", result.final_initial_capital)
    print("  Subaccount:      ", result.final_subaccount)

    # If you want to inspect indices and per-year balances:
    # print(result.yearly_indices.head(12))
    # print(result.yearly_balances.head(12))
