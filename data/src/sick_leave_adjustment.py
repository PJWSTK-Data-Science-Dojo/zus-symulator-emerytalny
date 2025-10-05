from dataclasses import dataclass

@dataclass
class SickLeaveResult:
    """Stores comparison between normal and sick-leave-adjusted pension."""
    base_pension: float
    adjusted_pension: float
    difference: float


class SickLeaveAdjustment:
    """
    Simple model for comparing pension with and without sick leave.
    'With sick leave' reduces the pension by 10%.
    """

    def __init__(self, reduction_factor: float = 0.9):
        """
        :param reduction_factor: coefficient for pension reduction (default 0.9)
        """
        if not (0 < reduction_factor <= 1):
            raise ValueError("Reduction factor must be between 0 and 1.")
        self.reduction_factor = reduction_factor

    def calculate(self, pension_amount: float) -> SickLeaveResult:
        """
        Calculates pension with and without sick leave.
        :param pension_amount: base pension (without sick leave adjustment)
        :return: SickLeaveResult
        """
        if pension_amount < 0:
            raise ValueError("Pension amount cannot be negative.")

        adjusted = round(pension_amount * self.reduction_factor, 2)
        diff = round(pension_amount - adjusted, 2)

        return SickLeaveResult(
            base_pension=round(pension_amount, 2),
            adjusted_pension=adjusted,
            difference=diff
        )


if __name__ == "__main__":
    calc = SickLeaveAdjustment()

    base = 5000
    result = calc.calculate(base)

    print(f"Emerytura bez chorobowych: {result.base_pension} zł")
    print(f"Emerytura z chorobowymi:  {result.adjusted_pension} zł")
    print(f"Różnica:                  {result.difference} zł")
