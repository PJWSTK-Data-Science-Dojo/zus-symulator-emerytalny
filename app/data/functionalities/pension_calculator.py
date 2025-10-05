from dataclasses import dataclass
from typing import Optional


@dataclass
class PensionInputs:
    life_expectancy_months: int
    total_capital: Optional[float] = 0


class PensionCalculator:
    MIN_LIFE_EXPECTANCY_MONTHS = 60

    @staticmethod
    def calculate_pension(inputs: PensionInputs) -> float:
        inputs.life_expectancy_months = max(PensionCalculator.MIN_LIFE_EXPECTANCY_MONTHS, inputs.life_expectancy_months)
        return round(inputs.total_capital / inputs.life_expectancy_months, 2)
