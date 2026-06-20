import unittest
import os
import sys

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scoring_engine import ScoringEngine

class TestScoringEngine(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.engine = ScoringEngine()

    def test_calculate_yoe_fit(self):
        # YOE = 7.0 is exactly the mean, so fit should be 1.0
        self.assertAlmostEqual(self.engine.calculate_yoe_fit(7.0), 1.0, places=4)
        # YOE = 1.0 is far from mean, so fit should be low
        self.assertTrue(self.engine.calculate_yoe_fit(1.0) < 0.2)
        # YOE = 15.0 is also far from mean, so fit should be low
        self.assertTrue(self.engine.calculate_yoe_fit(15.0) < 0.2)

    def test_calculate_stability_score(self):
        # 36 months average tenure -> 1.0 stability
        history_stable = [{"duration_months": 36}, {"duration_months": 40}]
        self.assertEqual(self.engine.calculate_stability_score(history_stable), 1.0)
        
        # 12 months average tenure -> 0.3 stability
        history_hopper = [{"duration_months": 12}, {"duration_months": 12}]
        self.assertEqual(self.engine.calculate_stability_score(history_hopper), 0.3)

    def test_get_services_penalty(self):
        # Entire career at TCS/Wipro -> Penalty (0.75)
        history_services = [
            {"company": "TCS"},
            {"company": "Wipro Limited"}
        ]
        self.assertEqual(self.engine.get_services_penalty(history_services, "TCS"), 0.75)
        
        # Part career at TCS, part at Swiggy (product company) -> No penalty (1.0)
        history_mixed = [
            {"company": "TCS"},
            {"company": "Swiggy"}
        ]
        self.assertEqual(self.engine.get_services_penalty(history_mixed, "Swiggy"), 1.0)

    def test_get_notice_score(self):
        self.assertEqual(self.engine.get_notice_score(15), 1.0)
        self.assertEqual(self.engine.get_notice_score(90), 0.3)
        self.assertEqual(self.engine.get_notice_score(None), 0.2)

    def test_score_candidate(self):
        mock_cand = {
            "candidate_id": "CAND_1234567",
            "profile": {
                "years_of_experience": 7.0,
                "current_company": "Google"
            },
            "career_history": [
                {"company": "Google", "duration_months": 36, "title": "Senior AI Engineer", "start_date": "2023-01-01"}
            ],
            "skills": [],
            "redrob_signals": {
                "expected_salary_range_inr_lpa": {"min": 10, "max": 15},
                "notice_period_days": 15,
                "recruiter_response_rate": 0.8,
                "avg_response_time_hours": 10,
                "last_active_date": "2026-06-10",
                "open_to_work_flag": True,
                "profile_completeness_score": 90
            }
        }
        
        # Test scoring
        res = self.engine.score_candidate(mock_cand, matched_ids=[35], semantic_sim=0.75)
        
        # Verify required keys in returned feature breakdown
        self.assertEqual(res["candidate_id"], "CAND_1234567")
        self.assertTrue("final_score" in res)
        self.assertTrue("template_score" in res)
        self.assertTrue("semantic_score" in res)
        self.assertTrue("behavioral_score" in res)
        self.assertTrue("progression_score" in res)
        self.assertTrue("stability_score" in res)
        
        # Final score should be reasonably high since candidate has clean record, perfect YOE, and good signals
        self.assertTrue(res["final_score"] > 0.5)

if __name__ == "__main__":
    unittest.main()
