import unittest
from data.functionalities.pension_profiles import PensionProfile, PensionProfiles

class TestPensionProfiles(unittest.TestCase):

    def setUp(self):
        self.profiles = PensionProfiles()

    def test_profiles_are_loaded(self):
        """Sprawdza, czy wczytano 6 predefiniowanych profili."""
        self.assertEqual(len(self.profiles.profiles), 6)

    def test_get_by_key_returns_correct_profile(self):
        """Sprawdza, czy można pobrać profil po kluczu."""
        profile = self.profiles.get_by_key("average")
        self.assertIsNotNone(profile)
        self.assertIsInstance(profile, PensionProfile)
        self.assertEqual(profile.key, "average")
        self.assertAlmostEqual(profile.wage_factor, 1.0)
        self.assertEqual(profile.description, "Średnia (przeciętna)")

    def test_invalid_key_returns_none(self):
        """Sprawdza, że nieistniejący klucz zwraca None."""
        profile = self.profiles.get_by_key("nonexistent")
        self.assertIsNone(profile)

    def test_profiles_contain_expected_keys(self):
        """Sprawdza, czy wszystkie klucze są zgodne z oczekiwaniem."""
        expected_keys = {
            "below_minimum", "minimum", "below_average",
            "average", "above_average", "top"
        }
        actual_keys = set(self.profiles.profiles.keys())
        self.assertSetEqual(expected_keys, actual_keys)

    def test_profile_values_are_reasonable(self):
        """Sprawdza, że wartości lat pracy i współczynników są logiczne."""
        for profile in self.profiles.profiles.values():
            self.assertGreater(profile.years_worked, 0)
            self.assertLessEqual(profile.wage_factor, 3.0)
            self.assertGreater(profile.wage_factor, 0.1)


if __name__ == "__main__":
    unittest.main()
