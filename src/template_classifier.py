import os
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import (
    MODEL_PATH, 
    TEMPLATE_SEMANTIC_SIM_THRESHOLD,
    BASE_DIR
)

class TemplateClassifier:
    def __init__(self):
        # Paths to template texts and precomputed embeddings
        models_dir = os.path.join(BASE_DIR, "models")
        self.texts_path = os.path.join(models_dir, "template_texts.json")
        self.embeddings_path = os.path.join(models_dir, "template_embeddings.pkl")
        
        # Load template texts
        if not os.path.exists(self.texts_path):
            raise FileNotFoundError(f"Template texts JSON file not found at: {self.texts_path}")
        with open(self.texts_path, "r", encoding="utf-8") as f:
            self.templates = json.load(f)
            
        # Load template embeddings
        if not os.path.exists(self.embeddings_path):
            raise FileNotFoundError(f"Template embeddings pickle file not found at: {self.embeddings_path}")
        with open(self.embeddings_path, "rb") as f:
            self.template_embeddings = pickle.load(f)
            
        # Cleaned template texts for exact matching
        self.clean_templates = [self._clean_text(t) for t in self.templates]
        
        # Lazy-loaded sentence-transformers model
        self.model = None

    def _load_model(self):
        if self.model is None:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Local sentence-transformer model not found at: {MODEL_PATH}")
            self.model = SentenceTransformer(MODEL_PATH, device="cpu")

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Remove whitespace and normalize quotes / symbols
        return text.strip().lower().replace("—", "-").replace("", "-").replace("'", "").replace('"', "")

    def find_template_id(self, desc_text: str) -> int:
        """
        Classifies a job description using Exact Match -> MiniLM Semantic Fallback.
        Returns the 1-based template index (1 to 44) if matched, otherwise None.
        """
        if not desc_text:
            return None
            
        clean_desc = self._clean_text(desc_text)
        
        # --- Stage 1: Exact / Substring Matching ---
        for idx, clean_temp in enumerate(self.clean_templates):
            # Check for exact matches or high-quality subset containment
            if clean_desc == clean_temp or clean_temp in clean_desc or clean_desc in clean_temp:
                return idx + 1 # 1-based index
                
        # --- Stage 2: MiniLM Semantic Fallback ---
        self._load_model()
        desc_embedding = self.model.encode(desc_text, show_progress_bar=False)
        
        # Calculate cosine similarity manually using dot product (since sentence-transformers output normalized vectors)
        # Cosine similarity = dot(A, B) / (||A|| * ||B||)
        # BGE / MiniLM vectors from sentence-transformers are L2-normalized, so dot product is cosine similarity.
        similarities = []
        for temp_emb in self.template_embeddings:
            # normalize vectors in case they are not already
            norm_a = np.linalg.norm(desc_embedding)
            norm_b = np.linalg.norm(temp_emb)
            if norm_a == 0 or norm_b == 0:
                sim = 0.0
            else:
                sim = np.dot(desc_embedding, temp_emb) / (norm_a * norm_b)
            similarities.append(sim)
            
        max_idx = int(np.argmax(similarities))
        max_sim = float(similarities[max_idx])
        
        if max_sim >= TEMPLATE_SEMANTIC_SIM_THRESHOLD:
            return max_idx + 1
            
        return None

    def classify_candidate(self, candidate_record: dict) -> list[int]:
        """
        Parses career history of a candidate and classifies each job into template IDs.
        Returns list of matched template IDs.
        """
        if not candidate_record:
            return []
            
        history = candidate_record.get("career_history", [])
        matched_ids = []
        for job in history:
            desc = job.get("description", "")
            tid = self.find_template_id(desc)
            if tid:
                matched_ids.append(tid)
                
        return matched_ids
