import unittest
import os
import sys

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reasoning_generator import ReasoningGenerator

class TestReasoningGenerator(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.generator = ReasoningGenerator()

    def test_generate_reasoning_tier_1(self):
        candidate = {
            "candidate_id": "CAND_0000042",
            "profile": {
                "anonymized_name": "Aarav Sharma",
                "years_of_experience": 6.5,
                "current_title": "Applied ML Engineer",
                "current_company": "Swiggy",
                "location": "Bangalore"
            },
            "skills": [
                {"name": "Pinecone"},
                {"name": "PyTorch"},
                {"name": "sentence-transformers"}
            ],
            "redrob_signals": {
                "notice_period_days": 30,
                "willing_to_relocate": True
            }
        }
        
        reasoning = self.generator.generate_reasoning(candidate, matched_ids=[37], score_breakdown={})
        
        print(f"\nGenerated Reasoning Tier 1:")
        print(f"  {reasoning}")
        
        # Verify it contains crucial facts
        self.assertTrue("Aarav Sharma" in reasoning)
        self.assertTrue("6.5" in reasoning)
        self.assertTrue("BGE" in reasoning or "Pinecone" in reasoning) # achievement details
        self.assertTrue("30" in reasoning) # notice period
        self.assertTrue("Bangalore" in reasoning) # location

    def test_generate_reasoning_tier_2(self):
        candidate = {
            "candidate_id": "CAND_0000099",
            "profile": {
                "anonymized_name": "Kabir Mehta",
                "years_of_experience": 4.0,
                "current_title": "Data Scientist",
                "current_company": "Initech",
                "location": "Pune"
            },
            "skills": [
                {"name": "Python"},
                {"name": "scikit-learn"}
            ],
            "redrob_signals": {
                "notice_period_days": 60,
                "willing_to_relocate": False
            }
        }
        
        reasoning = self.generator.generate_reasoning(candidate, matched_ids=[25], score_breakdown={})
        
        print(f"\nGenerated Reasoning Tier 2:")
        print(f"  {reasoning}")
        
        # Verify it contains crucial facts
        self.assertTrue("Kabir Mehta" in reasoning)
        self.assertTrue("4.0" in reasoning)
        self.assertTrue("pune" in reasoning.lower())

    def test_determinism_and_diversity(self):
        candidate_1 = {
            "candidate_id": "CAND_0000001",
            "profile": {"anonymized_name": "User 1", "years_of_experience": 5.0}
        }
        candidate_2 = {
            "candidate_id": "CAND_0000002",
            "profile": {"anonymized_name": "User 2", "years_of_experience": 5.0}
        }
        
        # 1. Determinism
        res_a1 = self.generator.generate_reasoning(candidate_1, [37], {})
        res_a2 = self.generator.generate_reasoning(candidate_1, [37], {})
        self.assertEqual(res_a1, res_a2)
        
        # 2. Diversity (different IDs choose different templates)
        res_b = self.generator.generate_reasoning(candidate_2, [37], {})
        # Note: since they have different IDs and are hashed, their template structures should be different
        self.assertNotEqual(res_a1.replace("User 1", "User 2").replace("CAND_0000001", "CAND_0000002"), res_b)

if __name__ == "__main__":
    unittest.main()
