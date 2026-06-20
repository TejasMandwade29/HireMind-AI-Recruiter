import unittest
import os
import sys

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.career_progression import CareerProgressionScorer

class TestCareerProgression(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.scorer = CareerProgressionScorer()
        
    def test_title_level(self):
        self.assertEqual(self.scorer._get_title_level("Junior ML Engineer"), 1)
        self.assertEqual(self.scorer._get_title_level("Software Engineer II"), 2)
        self.assertEqual(self.scorer._get_title_level("Senior AI Engineer"), 3)
        self.assertEqual(self.scorer._get_title_level("Lead Data Scientist"), 3)
        self.assertEqual(self.scorer._get_title_level(None), 2)
        
    def test_calculate_progression_score(self):
        # 1. Upward progression: Junior (1) -> Mid (2) -> Senior (3)
        history_up = [
            {"title": "Junior Developer", "start_date": "2020-01-01"},
            {"title": "Software Engineer", "start_date": "2022-01-01"},
            {"title": "Senior Engineer", "start_date": "2024-01-01"}
        ]
        score_up = self.scorer.calculate_progression_score(history_up)
        self.assertTrue(score_up > 0.6)
        
        # 2. Stable progression: Mid (2) -> Mid (2)
        history_stable = [
            {"title": "Software Engineer", "start_date": "2020-01-01"},
            {"title": "Developer", "start_date": "2023-01-01"}
        ]
        score_stable = self.scorer.calculate_progression_score(history_stable)
        self.assertEqual(score_stable, 0.5)
        
        # 3. Demoted progression: Senior (3) -> Junior (1)
        history_down = [
            {"title": "Lead Architect", "start_date": "2020-01-01"},
            {"title": "Junior Assistant", "start_date": "2023-01-01"}
        ]
        score_down = self.scorer.calculate_progression_score(history_down)
        self.assertTrue(score_down < 0.4)

    def test_calculate_growth_velocity(self):
        # Moving from a small company (1-10) to a large one (10001+)
        # Reached senior level in 24 months (2.0 years)
        history = [
            {"title": "Junior Developer", "company_size": "1-10", "start_date": "2020-01-01", "duration_months": 24},
            {"title": "Senior AI Engineer", "company_size": "10001+", "start_date": "2022-01-01", "duration_months": 24}
        ]
        vel = self.scorer.calculate_growth_velocity(history, 4.0)
        # Should be a high velocity score because of company scale growth and fast senior promotion
        self.assertTrue(vel > 0.6)

if __name__ == "__main__":
    unittest.main()
