import pandas as pd
from data.src.valorization_engine import ForecastData, DataPaths, _interpolate_yearly_factors

class MacroScenarioAnalyzer:
    def __init__(self, forecast_data: ForecastData):
        self.data = forecast_data

    def compare_inflation_scenarios(self) -> pd.DataFrame:
        dfs = []
        for variant in [1, 2, 3]:
            df = self.data.load_macro(variant)[["rok", "cpi_factor", "real_gdp_factor"]].copy()
            df["variant"] = variant
            dfs.append(df)
        merged = pd.concat(dfs).sort_values(["rok", "variant"]).reset_index(drop=True)
        return merged

    def summarize_by_year(self) -> pd.DataFrame:
        df = self.compare_inflation_scenarios()
        summary = (
            df.groupby("rok")[["cpi_factor", "real_gdp_factor"]]
            .agg(["min", "max", "mean"])
            .round(3)
        )
        summary.columns = ["_".join(c) for c in summary.columns]
        return summary.reset_index()

if __name__ == "__main__":
    paths = DataPaths(
        macro_variant_1="data/dane_emerytalne/parametry_makroekonomiczne_wariant_1.csv",
        macro_variant_2="data/dane_emerytalne/parametry_makroekonomiczne_wariant_2.csv",
        macro_variant_3="data/dane_emerytalne/parametry_makroekonomiczne_wariant_3.csv",
        revenues="data/dane_emerytalne/wplywy_skladkowe_mln_zl.csv",
    )

    data = ForecastData(paths)
    analyzer = MacroScenarioAnalyzer(data)

    summary = analyzer.summarize_by_year()
    print(summary.head(10))
