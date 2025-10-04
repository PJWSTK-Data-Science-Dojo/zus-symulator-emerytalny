from enum import Enum
from typing import Dict, Tuple


class ForecastVariant(Enum):
    PESSIMISTIC = "pesymistyczny"
    REALISTIC = "realistyczny"
    OPTIMISTIC = "optymistyczny"


class PensionCalculator:
    # Alpha coefficients for key years - static for all instances
    alpha_coefficients: Dict[ForecastVariant, Dict[int, float]] = {
        ForecastVariant.REALISTIC: {
            2030: 0.66,
            2040: 0.72,
            2050: 0.73,
            2060: 0.78,
            2070: 0.87,
            2080: 0.88,
        },
        ForecastVariant.PESSIMISTIC: {
            2030: 0.60,
            2040: 0.64,
            2050: 0.63,
            2060: 0.66,
            2070: 0.72,
            2080: 0.72,
        },
        ForecastVariant.OPTIMISTIC: {
            2030: 0.71,
            2040: 0.81,
            2050: 0.84,
            2060: 0.90,
            2070: 1.03,
            2080: 1.06,
        },
    }

    # Constants for extrapolation bounds
    MIN_ALPHA = 0.5  # System covers minimum 50% of obligations
    MAX_ALPHA = 1.5  # System generates maximum 50% surplus

    def _interpolate_alpha(self, variant: ForecastVariant, year: int) -> float:
        """Linear interpolation or extrapolation of alpha coefficient for any year."""

        coefficients = self.alpha_coefficients[variant]
        years = sorted(coefficients.keys())

        # If year is before first year in data
        if year <= years[0]:
            return coefficients[years[0]]

        # If year is within the data range, interpolate normally
        if year <= years[-1]:
            # Find year interval for interpolation
            for i in range(len(years) - 1):
                if years[i] <= year <= years[i + 1]:
                    t1, t2 = years[i], years[i + 1]
                    alpha1 = coefficients[t1]
                    alpha2 = coefficients[t2]

                    # Linear interpolation
                    alpha = alpha1 + (alpha2 - alpha1) * (year - t1) / (t2 - t1)
                    return round(alpha, 4)

        # Extrapolation beyond the last data point (2080)
        # Use the trend from the last two data points (2070-2080)
        t1, t2 = years[-2], years[-1]  # 2070, 2080
        alpha1, alpha2 = coefficients[t1], coefficients[t2]

        # Calculate slope from last two points
        slope = (alpha2 - alpha1) / (t2 - t1)

        # Extrapolate linearly
        extrapolated_alpha = alpha2 + slope * (year - t2)

        # Apply bounds to prevent nonsensical values
        if extrapolated_alpha < self.MIN_ALPHA:
            return self.MIN_ALPHA
        elif extrapolated_alpha > self.MAX_ALPHA:
            return self.MAX_ALPHA
        else:
            return round(extrapolated_alpha, 4)

    def forecast_pension(
        self, pension_amount: float, year: int, variant: ForecastVariant
    ) -> Tuple[float, str]:
        """
        Forecasts pension amount for given year and variant.

        Args:
            pension_amount: Base pension amount (in PLN)
            year: Forecast year (2023 or later)
            variant: Selected forecast variant (enum)

        Returns:
            Tuple containing:
            - forecasted pension amount
            - interpretation of the result
        """
        # Year validation - allow extrapolation beyond 2080
        if year < 2023:
            raise ValueError(f"Rok {year} jest przed początkiem prognozy (2023)")

        # Pension amount validation
        if pension_amount <= 0:
            raise ValueError("Wysokość emerytury musi być większa od zera")

        # Calculate alpha coefficient for given year and variant
        alpha = self._interpolate_alpha(variant, year)

        # Calculate forecasted pension
        forecasted_pension = round(pension_amount * alpha, 2)

        # Prepare interpretation
        if alpha < 1:
            coverage_percent = round(alpha * 100, 1)
            interpretation = (
                f"System pokrywa {coverage_percent}% zobowiązań. "
                f"Deficyt wynosi {100 - coverage_percent}%."
            )
        elif alpha == 1:
            interpretation = "System jest zrównoważony - pokrywa 100% zobowiązań."
        else:
            surplus = round((alpha - 1) * 100, 1)
            interpretation = f"System generuje nadwyżkę {surplus}% ponad zobowiązania."

        return forecasted_pension, interpretation


# Example usage:
if __name__ == "__main__":
    calculator = PensionCalculator()

    # Example calculation
    base_pension = 3000  # PLN
    retirement_year = 2045  # Test extrapolation beyond 2080

    print(f"Prognoza emerytury dla roku {retirement_year}")
    print(f"Emerytura bazowa: {base_pension} zł\n")

    for variant in ForecastVariant:
        forecast, interpretation = calculator.forecast_pension(
            pension_amount=base_pension, year=retirement_year, variant=variant
        )
        print(f"Wariant {variant.value}:")
        print(f"  Prognozowana emerytura: {forecast} zł")
        print(f"  {interpretation}\n")
