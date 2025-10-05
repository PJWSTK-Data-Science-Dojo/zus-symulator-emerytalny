"""
Zawiera definicje typowych profili emerytalnych wykorzystywanych
w symulacjach ZUS — od osób poniżej minimum po najwyższe świadczenia.

Każdy profil określa:
- szacunkowy czas pracy (years_of_work)
- względny poziom wynagrodzenia (wage_factor)
- stabilność zatrudnienia (stability)
- opis tekstowy (description)

Plik ten stanowi punkt wyjścia dla symulacji emerytalnych
w module `pension_profile_forecast.py`.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class PensionProfile:
    """Opis pojedynczego profilu emerytalnego."""
    name: str
    years_of_work: int
    wage_factor: float  # w stosunku do średniego wynagrodzenia (1.0 = średnia krajowa)
    stability: float    # stabilność zatrudnienia w [0–1]
    description: str


class PensionProfileSimulator:
    """
    Udostępnia zestaw predefiniowanych profili emerytalnych,
    które mogą być wykorzystane do prognoz świadczeń.
    """

    def __init__(self):
        self.profiles: Dict[str, PensionProfile] = {
            "below_minimum": PensionProfile(
                name="Poniżej minimalnej",
                years_of_work=15,
                wage_factor=0.5,
                stability=0.4,
                description=(
                    "Osoby, które nie przepracowały wymaganego stażu (25 lat mężczyźni, 20 lat kobiety). "
                    "Często nieregularne zatrudnienie lub przerwy zawodowe. Emerytura poniżej minimum ustawowego."
                ),
            ),
            "minimum": PensionProfile(
                name="Minimalna",
                years_of_work=25,
                wage_factor=0.7,
                stability=0.6,
                description=(
                    "Spełnione warunki stażowe, ale niskie zarobki. "
                    "Świadczenie równe minimalnej emeryturze gwarantowanej przez ZUS."
                ),
            ),
            "below_average": PensionProfile(
                name="Poniżej średniej",
                years_of_work=30,
                wage_factor=0.85,
                stability=0.7,
                description=(
                    "Emerytury wyższe niż minimalne, ale niższe od średniej. "
                    "Typowe dla osób o średnich karierach zawodowych z przerwami."
                ),
            ),
            "average": PensionProfile(
                name="Średnia",
                years_of_work=35,
                wage_factor=1.0,
                stability=0.85,
                description=(
                    "Świadczenia zbliżone do średniej krajowej. "
                    "Stabilne zatrudnienie przez większość kariery."
                ),
            ),
            "above_average": PensionProfile(
                name="Powyżej średniej",
                years_of_work=40,
                wage_factor=1.3,
                stability=0.9,
                description=(
                    "Długi staż pracy i stabilne zatrudnienie. "
                    "Emerytury wyższe od średniej, typowe dla specjalistów i sektora publicznego."
                ),
            ),
            "top_earners": PensionProfile(
                name="Najwyższe emerytury (top 5%)",
                years_of_work=42,
                wage_factor=2.0,
                stability=0.95,
                description=(
                    "Emerytury kilkukrotnie wyższe od średniej. "
                    "Dotyczy osób o bardzo wysokich zarobkach i długim stażu pracy."
                ),
            ),
        }

    def list_profiles(self):
        """Zwraca listę nazw dostępnych profili."""
        return list(self.profiles.keys())

    def get_profile(self, profile_name: str) -> PensionProfile:
        """Zwraca obiekt `PensionProfile` dla wybranego profilu."""
        if profile_name not in self.profiles:
            raise ValueError(f"Nieznany profil: {profile_name}")
        return self.profiles[profile_name]

    def simulate_profile(self, profile_name: str) -> PensionProfile:
        """
        Zwraca profil gotowy do użycia w prognozie.
        (Metoda alias — zgodna z konwencją reszty projektu.)
        """
        return self.get_profile(profile_name)

@dataclass
class PensionProfile:
    key: str
    description: str
    years_worked: int
    wage_factor: float

class PensionProfiles:
    """
    Zbiór predefiniowanych profili emerytalnych
    (np. poniżej minimalnej, średnia, top 5%, itd.)
    """

    def __init__(self):
        self.profiles = {
            "below_minimum": PensionProfile(
                key="below_minimum",
                description="Poniżej minimalnej",
                years_worked=15,
                wage_factor=0.6
            ),
            "minimum": PensionProfile(
                key="minimum",
                description="Minimalna",
                years_worked=25,
                wage_factor=0.8
            ),
            "below_average": PensionProfile(
                key="below_average",
                description="Poniżej średniej",
                years_worked=30,
                wage_factor=0.9
            ),
            "average": PensionProfile(
                key="average",
                description="Średnia (przeciętna)",
                years_worked=35,
                wage_factor=1.0
            ),
            "above_average": PensionProfile(
                key="above_average",
                description="Powyżej średniej",
                years_worked=40,
                wage_factor=1.3
            ),
            "top": PensionProfile(
                key="top",
                description="Najwyższe emerytury (top 5–10%)",
                years_worked=42,
                wage_factor=2.5
            ),
        }

    def get_by_key(self, key: str) -> PensionProfile | None:
        """Zwraca profil po kluczu lub None, jeśli nie istnieje."""
        return self.profiles.get(key)


# === Przykład użycia ===
if __name__ == "__main__":
    sim = PensionProfileSimulator()

    print("Dostępne profile:")
    for name in sim.list_profiles():
        p = sim.get_profile(name)
        print(f"- {name}: {p.name} ({p.years_of_work} lat, {p.wage_factor}x średniej)")
