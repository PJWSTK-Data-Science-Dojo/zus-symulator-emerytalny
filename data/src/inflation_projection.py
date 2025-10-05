import pandas as pd
from typing import Literal

Variant = Literal[1, 2, 3]

class InflationProjection:
    def __init__(self, macro_paths: dict[Variant, str]):
        self.macro_paths = macro_paths # dict np. {1: 'data/parametry_makroekonomiczne_wariant_1.csv', ...}
        self._data = {}

    def load_data(self, variant: Variant) -> pd.DataFrame:
        """Wczytuje dane o inflacji dla wybranego wariantu (1, 2, 3)."""
        if variant in self._data:
            return self._data[variant]

        df = pd.read_csv(self.macro_paths[variant])
        df = df[["rok", "inflacja_ogolna"]].copy()
        df["inflation_factor"] = df["inflacja_ogolna"] / 100.0  # np. 105.2 -> 1.052
        self._data[variant] = df
        return df

    def cumulative_inflation(self, variant: Variant, start_year: int, end_year: int) -> float:
        """
        Zwraca łączną inflację między start_year a end_year (jako mnożnik).
        Np. 1.127 oznacza wzrost o 12,7%.
        """
        df = self.load_data(variant)
        df = df[(df["rok"] >= start_year) & (df["rok"] <= end_year)].copy()

        if df.empty:
            raise ValueError(f"No inflation data for range {start_year}-{end_year} (variant {variant})")

        cumulative = df["inflation_factor"].prod()
        return cumulative

    def project_price(self, variant: Variant, start_year: int, end_year: int, amount: float) -> float:
        """Oblicza wartość nominalną kwoty po uwzględnieniu inflacji."""
        factor = self.cumulative_inflation(variant, start_year, end_year)
        return round(amount * factor, 2)


# === przykład użycia ===
if __name__ == "__main__":
    macro_paths = {
        1: "data/dane_emerytalne/parametry_makroekonomiczne_wariant_1.csv",
        2: "data/dane_emerytalne/parametry_makroekonomiczne_wariant_2.csv",
        3: "data/dane_emerytalne/parametry_makroekonomiczne_wariant_3.csv"
    }

    infl = InflationProjection(macro_paths)

    start = 2024
    end = 2030
    base_amount = 1000.0

    cumulative_factor = infl.cumulative_inflation(2, start, end)
    projected_value = infl.project_price(2, start, end, base_amount)

    print(f"Skumulowana inflacja {start}-{end}: {(cumulative_factor - 1)*100:.2f}%")
    print(f"Wartość {base_amount} zł w {start} roku to {projected_value} zł w {end} roku.")
