from dataclasses import dataclass

@dataclass
class PensionComparisonResult:
    expected: float
    forecasted: float
    difference: float
    percentage: float
    message: str

class PensionComparison:
    @staticmethod
    def compare(expected: float, forecasted: float) -> PensionComparisonResult:
        """
        Compare expected vs forecasted pension values.
        Returns structured result with difference, percentage and message.
        """
        difference = round(expected - forecasted, 2)
        percentage = round((forecasted / expected) * 100, 2) if expected > 0 else 0.0

        if forecasted > expected:
            message = (
                f"Świetna wiadomość! Twoja prognozowana emerytura ({forecasted} zł) "
                f"jest wyższa niż oczekiwana ({expected} zł)."
            )
        elif forecasted < expected:
            message = (
                f"Twoja prognozowana emerytura ({forecasted} zł) jest niższa niż oczekiwana ({expected} zł). "
                f"Brakuje {difference} zł ({100 - percentage}% mniej). "
                f"Rozważ dłuższą aktywność zawodową lub wyższe składki."
            )
        else:  # forecasted == expected
            message = (
                f"Twoja prognozowana emerytura ({forecasted} zł) "
                f"jest równa oczekiwanej emeryturze ({expected} zł)."
            )

        return PensionComparisonResult(
            expected=expected,
            forecasted=forecasted,
            difference=difference,
            percentage=percentage,
            message=message
        )