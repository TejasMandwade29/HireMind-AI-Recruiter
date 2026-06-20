import unittest
from src.filters import (
    has_salary_anomaly,
    has_duration_anomaly,
    has_skill_anomaly,
    is_clean_candidate
)

class TestFilters(unittest.TestCase):
    
    def test_has_salary_anomaly(self):
        # Normal expected salary
        self.assertFalse(has_salary_anomaly({"min": 10, "max": 20}))
        # Boundary equal expected salary
        self.assertFalse(has_salary_anomaly({"min": 15, "max": 15}))
        # Salary anomaly (min > max)
        self.assertTrue(has_salary_anomaly({"min": 25, "max": 20}))
        # Missing values
        self.assertFalse(has_salary_anomaly({}))
        self.assertFalse(has_salary_anomaly(None))
        self.assertFalse(has_salary_anomaly({"min": 10}))
        
    def test_has_duration_anomaly(self):
        history = [
            {"company": "Google", "duration_months": 24},
            {"company": "Swiggy", "duration_months": 36}
        ]
        # Normal duration (Total YOE 6.0 years = 72 months)
        self.assertFalse(has_duration_anomaly(history, 6.0))
        # Anomaly: Single job duration (36 months) exceeds YOE (2.0 years = 24 months)
        self.assertTrue(has_duration_anomaly(history, 2.0))
        # Missing career history / YOE
        self.assertFalse(has_duration_anomaly(None, 5.0))
        self.assertFalse(has_duration_anomaly(history, None))
        
    def test_has_skill_anomaly(self):
        skills_clean = [
            {"name": "Python", "proficiency": "expert", "duration_months": 36},
            {"name": "ML", "proficiency": "beginner", "duration_months": 0}
        ]
        skills_anomaly = [
            {"name": "Python", "proficiency": "expert", "duration_months": 0},
            {"name": "ML", "proficiency": "beginner", "duration_months": 12}
        ]
        # Clean skills list
        self.assertFalse(has_skill_anomaly(skills_clean))
        # Anomaly (expert with 0 months)
        self.assertTrue(has_skill_anomaly(skills_anomaly))
        # Missing skills list
        self.assertFalse(has_skill_anomaly(None))
        
    def test_is_clean_candidate(self):
        # Clean candidate record
        clean_cand = {
            "profile": {"years_of_experience": 5.0},
            "career_history": [{"company": "Swiggy", "duration_months": 24}],
            "skills": [{"name": "Python", "proficiency": "expert", "duration_months": 12}],
            "redrob_signals": {"expected_salary_range_inr_lpa": {"min": 10.0, "max": 15.0}}
        }
        self.assertTrue(is_clean_candidate(clean_cand))
        
        # Anomalous candidate record (salary anomaly)
        anom_cand = {
            "profile": {"years_of_experience": 5.0},
            "career_history": [{"company": "Swiggy", "duration_months": 24}],
            "skills": [{"name": "Python", "proficiency": "expert", "duration_months": 12}],
            "redrob_signals": {"expected_salary_range_inr_lpa": {"min": 20.0, "max": 15.0}}
        }
        self.assertFalse(is_clean_candidate(anom_cand))

if __name__ == "__main__":
    unittest.main()
