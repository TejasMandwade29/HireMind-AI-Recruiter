import unittest
import os
import sys

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.semantic_matching import SemanticMatcher

class TestSemanticMatcher(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.matcher = SemanticMatcher()
        cls.jd_text = (
            "We are looking for a Senior AI Engineer to join our founding team. "
            "Experience with embeddings-based retrieval systems (sentence-transformers), "
            "vector databases (Pinecone, FAISS, Milvus), learning-to-rank, and evaluation frameworks (NDCG, MAP) is required. "
            "Strong Python background."
        )

    def test_identical_similarity(self):
        # Identical texts should have similarity near 1.0
        text = "Senior AI Engineer building search and retrieval pipelines."
        sim = self.matcher.get_similarity(text, text)
        self.assertAlmostEqual(sim, 1.0, places=4)

    def test_different_similarity(self):
        # Different texts should have lower similarity
        text1 = "Senior AI Engineer building search and retrieval pipelines."
        text2 = "Looking for accountant to manage financial close and tax filings."
        sim = self.matcher.get_similarity(text1, text2)
        self.assertTrue(sim < 0.5)

    def test_score_candidate_semantic(self):
        # Candidate A: Strong match
        candidate_ml = {
            "profile": {
                "current_title": "Applied ML Engineer",
                "headline": "Search & Recommendation Systems | Pinecone, PyTorch, Embeddings",
                "summary": "Building end-to-end vector search pipelines and ranking layers for e-commerce search. Experience with sentence-transformers."
            }
        }
        
        # Candidate B: Poor match
        candidate_sales = {
            "profile": {
                "current_title": "Sales Executive",
                "headline": "Enterprise account executive carried $2M quota",
                "summary": " consultative sales of cloud software solutions into commercial accounts. Prospecting, commercial negotiation and closing."
            }
        }
        
        score_ml = self.matcher.score_candidate_semantic(candidate_ml, self.jd_text)
        score_sales = self.matcher.score_candidate_semantic(candidate_sales, self.jd_text)
        
        print(f"\nSemantic match validation:")
        print(f"  ML Candidate Score: {score_ml:.4f}")
        print(f"  Sales Candidate Score: {score_sales:.4f}")
        
        self.assertTrue(score_ml > score_sales)
        self.assertTrue(score_ml > 0.5)
        self.assertTrue(score_sales < 0.4)

if __name__ == "__main__":
    unittest.main()
