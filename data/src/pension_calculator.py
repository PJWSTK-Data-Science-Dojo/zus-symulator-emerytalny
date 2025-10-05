from dataclasses import dataclass
from typing import Optional


@dataclass
class PensionInputs:
    account: float  # total amount of contributions (with valorization)
    initial_capital: float  # valorized initial capital
    subaccount: float  # valorized subaccount
    life_expectancy_months: int


class PensionCalculator:
    MIN_LIFE_EXPECTANCY_MONTHS = 60

    @staticmethod
    def calculate_pension(inputs: PensionInputs) -> float:
        total_capital = inputs.account + inputs.initial_capital + inputs.subaccount
        inputs.life_expectancy_months = max(PensionCalculator.MIN_LIFE_EXPECTANCY_MONTHS, inputs.life_expectancy_months)
        return round(total_capital / inputs.life_expectancy_months, 2)
