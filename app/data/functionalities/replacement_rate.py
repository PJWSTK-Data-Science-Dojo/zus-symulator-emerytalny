from dataclasses import dataclass

@dataclass
class ReplacementRateResult:
    pension: float #forecasted pension (PLN)
    last_wage: float #last wage before retirement (PLN)
    rate_percent: float #last wage before retirement (PLN)
    message: str


class ReplacementRateCalculator:
    @staticmethod
    def calculate(pension: float, last_wage: float) -> ReplacementRateResult:
        """
        Calculate replacement rate = pension ÷ last_wage.
        """
        if last_wage <= 0:
            rate_percent = 0.0
        else:
            rate_percent = round((pension / last_wage) * 100, 2)

        if rate_percent >= 70:
            message = f"Twoja stopa zastąpienia wynosi {rate_percent}%. To bardzo wysoki poziom – Twoja emerytura zapewni podobny standard życia jak pensja."
        elif 40 <= rate_percent < 70:
            message = f"Twoja stopa zastąpienia wynosi {rate_percent}%. To umiarkowany poziom – emerytura będzie zauważalnie niższa niż pensja."
        else:
            message = f"Twoja stopa zastąpienia wynosi tylko {rate_percent}%. To niski poziom – standard życia po przejściu na emeryturę może się istotnie obniżyć."

        return ReplacementRateResult(
            pension=round(pension, 2),
            last_wage=round(last_wage, 2),
            rate_percent=rate_percent,
            message=message
        )
