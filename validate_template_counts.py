import json
import os
import sys

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.template_classifier import TemplateClassifier
from src.filters import is_clean_candidate

candidates_file = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

print("Initializing Template Classifier...")
classifier = TemplateClassifier()

limit = 10000
total_processed = 0
total_jobs_checked = 0
exact_matches = 0
fallback_matches = 0
no_matches = 0

tier_1_count = 0
tier_2_count = 0

tier_1_ids = set(range(28, 45))
tier_2_ids = set(range(22, 28))

# Let's override find_template_id to track exact vs. fallback matches
original_find_template_id = classifier.find_template_id

def tracked_find_template_id(desc_text):
    global exact_matches, fallback_matches, no_matches
    if not desc_text:
        return None
    
    clean_desc = classifier._clean_text(desc_text)
    
    # Check exact match
    for idx, clean_temp in enumerate(classifier.clean_templates):
        if clean_desc == clean_temp or clean_temp in clean_desc or clean_desc in clean_temp:
            exact_matches += 1
            return idx + 1
            
    # Fallback match
    classifier._load_model()
    desc_embedding = classifier.model.encode(desc_text, show_progress_bar=False)
    similarities = []
    for temp_emb in classifier.template_embeddings:
        import numpy as np
        norm_a = np.linalg.norm(desc_embedding)
        norm_b = np.linalg.norm(temp_emb)
        if norm_a == 0 or norm_b == 0:
            sim = 0.0
        else:
            sim = np.dot(desc_embedding, temp_emb) / (norm_a * norm_b)
        similarities.append(sim)
        
    max_idx = int(np.argmax(similarities))
    max_sim = float(similarities[max_idx])
    
    if max_sim >= 0.60:
        fallback_matches += 1
        return max_idx + 1
        
    no_matches += 1
    return None

classifier.find_template_id = tracked_find_template_id

print(f"Scanning first {limit} candidates from candidates.jsonl...")

with open(candidates_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        total_processed += 1
        
        # Check if candidate has Tier 1/2 experience
        matched_ids = classifier.classify_candidate(c)
        total_jobs_checked += len(c.get("career_history", []))
        
        has_t1 = any(tid in tier_1_ids for tid in matched_ids)
        has_t2 = any(tid in tier_2_ids for tid in matched_ids)
        
        # We only count clean candidates in Tiers to match our ranking logic
        if is_clean_candidate(c):
            if has_t1:
                tier_1_count += 1
            elif has_t2:
                tier_2_count += 1
                
        if total_processed >= limit:
            break

total_matches = exact_matches + fallback_matches
exact_pct = (exact_matches / total_matches * 100) if total_matches else 0
fallback_pct = (fallback_matches / total_matches * 100) if total_matches else 0

print(f"\n--- Template Classifier Validation ---")
print(f"Total Candidates Processed: {total_processed}")
print(f"Total Jobs Checked: {total_jobs_checked}")
print(f"Successful Matches: {total_matches} (unmatched: {no_matches})")
print(f"  - Exact-match coverage: {exact_matches} ({exact_pct:.2f}%)")
print(f"  - Semantic-fallback coverage: {fallback_matches} ({fallback_pct:.2f}%)")
print(f"\nClean Candidates in Sample:")
print(f"  - Tier 1 count: {tier_1_count} (Estimated in 100K: {tier_1_count * (100000/limit):.0f})")
print(f"  - Tier 2 count: {tier_2_count} (Estimated in 100K: {tier_2_count * (100000/limit):.0f})")
