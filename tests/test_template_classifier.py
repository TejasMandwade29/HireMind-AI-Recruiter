import unittest
import os
import sys

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.template_classifier import TemplateClassifier

class TestTemplateClassifier(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.classifier = TemplateClassifier()
        
    def test_exact_match(self):
        # Retrieve the exact text of Template #2 (Customer support)
        target_text = self.classifier.templates[1]
        
        # Test exact match
        tid = self.classifier.find_template_id(target_text)
        self.assertEqual(tid, 2)
        
        # Test case/spacing variation (should still match exactly via clean_text)
        variant_text = "   " + target_text.upper() + "   "
        tid_var = self.classifier.find_template_id(variant_text)
        self.assertEqual(tid_var, 2)
        
    def test_semantic_fallback(self):
        # Paraphrase Swiggy's recommendation system template (Template #29 in 1-based indexing)
        # Template #29 text is: "Trained and shipped multiple ranking models for our product's discovery feed using XGBoost and LightGBM..."
        paraphrase = "I trained and shipped multiple ranking models for our search discovery feed using XGBoost and LightGBM. I designed user engagement features and worked with PMs to optimize online metrics."
        
        tid = self.classifier.find_template_id(paraphrase)
        self.assertEqual(tid, 29)
        
    def test_unrelated_desc(self):
        # A completely random description
        garbage_desc = "Responsible for printing office memos, greeting guests, and coordinating cleaning staff."
        tid = self.classifier.find_template_id(garbage_desc)
        self.assertIsNone(tid)

if __name__ == "__main__":
    unittest.main()
