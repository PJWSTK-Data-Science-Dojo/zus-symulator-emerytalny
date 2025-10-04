import unittest
from data.src.pension_delay import PensionDelayCalculator


class TestPensionDelayCalculator(unittest.TestCase):

    def setUp(self):
        self.base_capital = 500_000
        self.monthly_contribution = 2500
        self.annual_valorization = 0.03
        self.life_expectancy_months = 240

    def test_returns_all_delays(self):
        result = PensionDelayCalculator.calculate_pension_delay(
            base_capital=self.base_capital,
            monthly_contribution=self.monthly_contribution,
            annual_valorization=self.annual_valorization,
            life_expectancy_months=self.life_expectancy_months
        )
        for d in [0, 1, 2, 5]:
            self.assertIn(d, result.pensions)

    def test_pension_increases_with_delay(self):
        result = PensionDelayCalculator.calculate_pension_delay(
            base_capital=self.base_capital,
            monthly_contribution=self.monthly_contribution,
            annual_valorization=self.annual_valorization,
            life_expectancy_months=self.life_expectancy_months
        )
        self.assertGreater(result.pensions[1], result.pensions[0])
        self.assertGreater(result.pensions[2], result.pensions[1])
        self.assertGreater(result.pensions[5], result.pensions[2])

    def test_pensions_are_positive(self):
        result = PensionDelayCalculator.calculate_pension_delay(
            base_capital=self.base_capital,
            monthly_contribution=self.monthly_contribution,
            annual_valorization=self.annual_valorization,
            life_expectancy_months=self.life_expectancy_months
        )
        for pension in result.pensions.values():
            self.assertGreater(pension, 0)

    def test_zero_life_expectancy(self):
        result = PensionDelayCalculator.calculate_pension_delay(
            base_capital=self.base_capital,
            monthly_contribution=self.monthly_contribution,
            annual_valorization=self.annual_valorization,
            life_expectancy_months=0
        )
        # wszystkie wyniki powinny być 0, bo dzielnik = 0
        for pension in result.pensions.values():
            self.assertEqual(pension, 0)


if __name__ == "__main__":
    unittest.main()
