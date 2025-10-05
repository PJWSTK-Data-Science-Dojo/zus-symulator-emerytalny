from typing import Optional


class PensionCalculator:
    MIN_LIFE_EXPECTANCY_MONTHS = 60

    @staticmethod
    def calculate_pension(life_expectancy_months: int, total_capital: Optional[float] = 0) -> float:
        life_expectancy_months = max(PensionCalculator.MIN_LIFE_EXPECTANCY_MONTHS, life_expectancy_months)
        return round(total_capital / life_expectancy_months, 2)
