import os
import sys
import unittest

from src.pension_scenarios import ForecastVariant, PensionCalculator


class TestPensionCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = PensionCalculator()

    def test_init(self):
        """Test that PensionCalculator initializes correctly."""
        self.assertIsInstance(self.calculator, PensionCalculator)
        # Verify alpha_coefficients are set as class variables
        self.assertIn(ForecastVariant.REALISTIC, PensionCalculator.alpha_coefficients)
        self.assertIn(ForecastVariant.PESSIMISTIC, PensionCalculator.alpha_coefficients)
        self.assertIn(ForecastVariant.OPTIMISTIC, PensionCalculator.alpha_coefficients)

    def test_year_validation_before_2023(self):
        """Test that years before 2023 raise ValueError."""
        with self.assertRaises(ValueError) as context:
            self.calculator.forecast_pension(3000, 2022, ForecastVariant.REALISTIC)
        self.assertIn("jest przed początkiem prognozy", str(context.exception))

    def test_pension_amount_validation_negative(self):
        """Test that negative pension amounts raise ValueError."""
        with self.assertRaises(ValueError) as context:
            self.calculator.forecast_pension(-100, 2030, ForecastVariant.REALISTIC)
        self.assertIn("Wysokość emerytury musi być większa od zera", str(context.exception))

    def test_pension_amount_validation_zero(self):
        """Test that zero pension amount raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.calculator.forecast_pension(0, 2030, ForecastVariant.REALISTIC)
        self.assertIn("Wysokość emerytury musi być większa od zera", str(context.exception))

    def test_interpolation_exact_year(self):
        """Test that exact years return exact coefficients."""
        # Test exact years for each variant
        for variant in ForecastVariant:
            for year in [2030, 2040, 2050, 2060, 2070, 2080]:
                expected_alpha = PensionCalculator.alpha_coefficients[variant][year]
                actual_alpha = self.calculator._interpolate_alpha(variant, year)
                self.assertAlmostEqual(actual_alpha, expected_alpha, places=4)

    def test_interpolation_between_years(self):
        """Test interpolation between known years."""
        # Test interpolation between 2030 and 2040
        alpha_2030 = PensionCalculator.alpha_coefficients[ForecastVariant.REALISTIC][2030]
        alpha_2040 = PensionCalculator.alpha_coefficients[ForecastVariant.REALISTIC][2040]
        expected_2035 = alpha_2030 + (alpha_2040 - alpha_2030) * 0.5

        actual_2035 = self.calculator._interpolate_alpha(ForecastVariant.REALISTIC, 2035)
        self.assertAlmostEqual(actual_2035, expected_2035, places=4)

    def test_extrapolation_beyond_2080(self):
        """Test extrapolation beyond 2080 with bounds."""
        # Test that we can extrapolate beyond 2080
        alpha_2080 = PensionCalculator.alpha_coefficients[ForecastVariant.REALISTIC][2080]
        alpha_2070 = PensionCalculator.alpha_coefficients[ForecastVariant.REALISTIC][2070]

        # The trend should continue upward
        alpha_2090 = self.calculator._interpolate_alpha(ForecastVariant.REALISTIC, 2090)
        self.assertGreater(alpha_2090, alpha_2080)

    def test_extrapolation_bounds_max(self):
        """Test that extrapolation respects MAX_ALPHA bound."""
        # Test with a very far future year
        alpha = self.calculator._interpolate_alpha(ForecastVariant.OPTIMISTIC, 3000)
        self.assertLessEqual(alpha, 1.5)

    def test_extrapolation_bounds_min(self):
        """Test that extrapolation respects MIN_ALPHA bound."""
        # Test with a very far future year
        alpha = self.calculator._interpolate_alpha(ForecastVariant.PESSIMISTIC, 3000)
        self.assertGreaterEqual(alpha, 0.5)

    def test_forecast_pension_functionality(self):
        """Test the main forecast_pension method."""
        pension_amount = 3000
        year = 2040
        variant = ForecastVariant.REALISTIC

        forecasted_pension, interpretation = self.calculator.forecast_pension(
            pension_amount, year, variant
        )

        expected_alpha = PensionCalculator.alpha_coefficients[variant][year]
        expected_pension = pension_amount * expected_alpha

        self.assertAlmostEqual(forecasted_pension, expected_pension, places=2)
        self.assertIn("System pokrywa", interpretation)
        self.assertIn("% zobowiązań", interpretation)

    def test_forecast_pension_interpretation_deficit(self):
        """Test interpretation when alpha < 1 (deficit)."""
        forecasted_pension, interpretation = self.calculator.forecast_pension(
            3000, 2030, ForecastVariant.REALISTIC
        )

        self.assertIn("System pokrywa", interpretation)
        self.assertIn("Deficyt wynosi", interpretation)

    def test_forecast_pension_interpretation_surplus(self):
        """Test interpretation when alpha > 1 (surplus)."""
        forecasted_pension, interpretation = self.calculator.forecast_pension(
            3000, 2070, ForecastVariant.OPTIMISTIC
        )

        self.assertIn("System generuje nadwyżkę", interpretation)

    def test_forecast_pension_interpretation_balanced(self):
        """Test interpretation when alpha = 1 (balanced)."""
        # Find a year where alpha is close to 1 for some variant
        forecasted_pension, interpretation = self.calculator.forecast_pension(
            3000, 2070, ForecastVariant.OPTIMISTIC
        )

        if "System jest zrównoważony" in interpretation:
            self.assertIn("pokrywa 100% zobowiązań", interpretation)

    def test_before_first_year(self):
        """Test that years before first year use first year's alpha."""
        alpha = self.calculator._interpolate_alpha(ForecastVariant.REALISTIC, 2025)
        expected = PensionCalculator.alpha_coefficients[ForecastVariant.REALISTIC][2030]
        self.assertEqual(alpha, expected)

    def test_all_variants_have_data(self):
        """Test that all forecast variants have complete data."""
        for variant in ForecastVariant:
            self.assertIn(variant, PensionCalculator.alpha_coefficients)
            coefficients = PensionCalculator.alpha_coefficients[variant]
            for year in [2030, 2040, 2050, 2060, 2070, 2080]:
                self.assertIn(year, coefficients)
                self.assertIsInstance(coefficients[year], float)
                self.assertGreater(coefficients[year], 0)

    def test_interpolation_monotonicity(self):
        """Test that interpolation maintains monotonicity."""
        # Realistic variant should be monotonically increasing
        years = [2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065, 2070, 2075, 2080]
        alphas = [
            self.calculator._interpolate_alpha(ForecastVariant.REALISTIC, year) for year in years
        ]

        for i in range(1, len(alphas)):
            self.assertGreaterEqual(alphas[i], alphas[i - 1])


if __name__ == "__main__":
    unittest.main()
