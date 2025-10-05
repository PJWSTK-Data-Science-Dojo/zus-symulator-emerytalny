import pandas as pd
import unicodedata

def normalize_text(s):
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join([c for c in s if not unicodedata.combining(c)])
    return s.lower().strip().replace(" ", "")

class LifeExpectancyCalculator:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.xl = pd.ExcelFile(excel_path)
        self.latest_year = max(int(s) for s in self.xl.sheet_names if s.isdigit())

    def _load_year_data(self, year: int) -> pd.DataFrame:
        df = pd.read_excel(self.xl, sheet_name=str(year), header=None)
        header_row = None
        for i, row in df.iterrows():
            normalized = [normalize_text(str(x)) for x in row]
            if any("wiek" in x for x in normalized) and any("m" in x for x in normalized) and any("k" in x for x in normalized):
                header_row = i
                break

        if header_row is not None:
            df.columns = df.iloc[header_row]
            df = df.iloc[header_row + 1:]
        df.columns = [normalize_text(str(c)) for c in df.columns]

        col_map = {}
        for c in df.columns:
            if "wiek" in c:
                col_map["wiek"] = c
            elif "mezczyzn" in c or "m" == c:
                col_map["mezczyzni"] = c
            elif "kobiet" in c or "k" == c:
                col_map["kobiety"] = c

        df = df[[col_map["wiek"], col_map["mezczyzni"], col_map["kobiety"]]]
        df.columns = ["age", "male", "female"]

        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df["male"] = df["male"].astype(str).str.replace(",", ".").astype(float)
        df["female"] = df["female"].astype(str).str.replace(",", ".").astype(float)
        return df.dropna(subset=["age"])

    def get_life_expectancy(self, year: int, age: int, sex: str) -> float:
        df = self._load_year_data(year)
        if sex.lower() == "m":
            col = "male"
        else:
            col = "female"

        row = df.loc[df["age"] == age]
        if row.empty:
            raise ValueError(f"Brak danych dla wieku {age} w roku {year}")
        return float(row[col].iloc[0])

    def calculate_required_extra_years(
        self,
        expected_pension: float,
        forecasted_pension: float,
        current_age: int,
        sex: str,
        year: int = None,
    ) -> float:
        """
        Estimating how many more years you need to work to reach your expected retirement age. This assumes a proportional increase in benefits and a reduction in life expectancy.
        """
        if year is None:
            year = self.latest_year

        current_life_expectancy = self.get_life_expectancy(year, current_age, sex)
        ratio = expected_pension / forecasted_pension

        # Assumption: Each additional 0.05 (5%) of benefit increase requires +1 year of service
        # (can be adjusted empirically)
        extra_years = max(0, (ratio - 1.0) / 0.05)
        return round(extra_years, 1)


if __name__ == "__main__":
    calc = LifeExpectancyCalculator("data/dane_emerytalne/tablice_trwania_zycia_w_latach_1990-2022.xlsx")

    expected = 5000   # expected retirement
    forecasted = 4200 # projected retirement
    age = 65
    sex = "k"

    extra = calc.calculate_required_extra_years(expected, forecasted, age, sex)
    print(f"Aby osiągnąć oczekiwaną emeryturę ({expected} PLN), należy pracować ok. {extra} lat dłużej.")
