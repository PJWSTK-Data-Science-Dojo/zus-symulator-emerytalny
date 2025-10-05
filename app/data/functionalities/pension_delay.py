from dataclasses import dataclass
from typing import Dict

from pydantic import BaseModel, ConfigDict

class Delay(BaseModel):
    years: int
    pension: float

class PensionDelayResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pensions: list[Delay]


class PensionDelayCalculator:
    @staticmethod
    def calculate_pension_delay(
        base_capital: float, #initial accumulated capital (PLN)
        monthly_contribution: float, #current monthly contribution added to account (PLN)
        life_expectancy_months: int, #remaining life expectancy at normal retirement age (months)
        annual_valorization: float=0.03, #yearly valorization rate, e.g. 0.03 = 3%
        delays: list = [0, 1, 2, 5] #list of delays in years to evaluate (default: [0,1,2,5])
    ) -> PensionDelayResult:
        """
        Calculate pension amounts depending on delay in retirement.
        """

        results = []
        for d in delays:
            # Start with base capital
            capital = base_capital
            months = life_expectancy_months - (12 * d)

            # Simulate additional years of work
            for year in range(d):
                # Add contributions for 12 months
                capital += monthly_contribution * 12
                # Apply valorization
                capital *= (1 + annual_valorization)

            # Calculate pension
            pension = capital / months if months > 0 else 0
            results.append(Delay(years=d, pension=round(pension, 2)))

        return PensionDelayResult(pensions=results)
