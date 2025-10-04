from dataclasses import dataclass
from typing import Optional

@dataclass
class PensionInputs:
    account: float  # total amount of contributions (with valorization)
    initial_capital: float  # valorized initial capital
    subaccount: float  # valorized subaccount
    life_expectancy_months: int

class PensionCalculator:
    @staticmethod
    def calculate_pension(inputs: PensionInputs) -> float:
        total_capital = inputs.account + inputs.initial_capital + inputs.subaccount
        if inputs.life_expectancy_months <= 0:
            raise ValueError("Life expectancy must be greater than zero.")
        return round(total_capital / inputs.life_expectancy_months, 2)

