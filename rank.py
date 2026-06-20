import argparse
import os
import sys
import logging
from src.config import (
    CANDIDATES_PATH,
    UNIQUE_DESCS_PATH,
    MODEL_PATH
)
from src.utils import (
    load_candidates_generator,
    load_job_description,
    save_submission_csv,
    StageProfiler,
    logger
)
from src.filters import is_clean_candidate
from src.template_classifier import TemplateClassifier
from src.semantic_matching import SemanticMatcher
from src.scoring_engine import ScoringEngine
from src.reasoning_generator import ReasoningGenerator

def main():
    parser = argparse.ArgumentParser(description="Redrob Intelligent Candidate Discovery & Ranking CLI")
    parser.add_argument("--candidates", type=str, default=CANDIDATES_PATH, help="Path to candidates.jsonl")
    parser.add_argument("--jd", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "job_description.txt"), help="Path to job_description.txt")
    parser.add_argument("--out", type=str, default="submission.csv", help="Path to write output CSV")
    args = parser.parse_args()

    logger.info("Starting Redrob AI Ranker pipeline...")
    
    # 1. Load Job Description
    if not os.path.exists(args.jd):
        # Fallback to check relative path in workspace
        alt_jd = os.path.join(os.path.dirname(args.candidates), "job_description.txt")
        if os.path.exists(alt_jd):
            args.jd = alt_jd
        else:
            logger.error(f"Job Description file not found at: {args.jd}")
            sys.exit(1)
            
    jd_text = load_job_description(args.jd)
    logger.info(f"Loaded Job Description: '{args.jd}' ({len(jd_text)} chars)")

    # 2. Stage 1: Anomaly Filtering & Classifier Segmentation
    clean_candidates_t1_t2 = []
    raw_count = 0
    clean_count = 0
    tier1_count = 0
    tier2_count = 0
    
    with StageProfiler("Filtering & Classifier Segmentation") as prof:
        # Load classifier
        classifier = TemplateClassifier()
        
        # Scan candidates generator
        for c in load_candidates_generator(args.candidates):
            raw_count += 1
            # Check honeypots / anomalies first
            if not is_clean_candidate(c):
                continue
            clean_count += 1
                
            # Classify candidate template IDs
            matched_ids = classifier.classify_candidate(c)
            
            # Segment: only keep Tier 1 (28-44) and Tier 2 (22-27)
            has_t1 = any(tid in range(28, 45) for tid in matched_ids)
            has_t2 = any(tid in range(22, 28) for tid in matched_ids)
            
            if has_t1:
                tier1_count += 1
            elif has_t2:
                tier2_count += 1
            
            if has_t1 or has_t2:
                c["matched_template_ids"] = matched_ids
                c["has_t1"] = has_t1
                clean_candidates_t1_t2.append(c)
                
    logger.info(f"Isolated {len(clean_candidates_t1_t2)} clean Tier 1/2 candidates from the pool.")

    # 3. Stage 2: Semantic Matching on pre-filtered subset
    with StageProfiler("Local Semantic Matching (Sentence-Transformers)") as prof:
        matcher = SemanticMatcher()
        semantic_scores = matcher.score_candidates_batch(clean_candidates_t1_t2, jd_text)

    # 4. Stage 3: Multi-Signal Scoring Engine
    scored_candidates = []
    with StageProfiler("Multi-Signal Scoring Engine") as prof:
        engine = ScoringEngine()
        for idx, c in enumerate(clean_candidates_t1_t2):
            matched_ids = c["matched_template_ids"]
            sem_score = semantic_scores[idx]
            
            score_breakdown = engine.score_candidate(c, matched_ids, sem_score)
            scored_candidates.append((c, score_breakdown))

    # 5. Stage 4: Ranking and Tie-Breaking
    # Sort criteria:
    # 1. final_score (Descending)
    # 2. candidate_id (Ascending, lexicographical tie-break)
    with StageProfiler("Ranking & Tie-Breaking") as prof:
        scored_candidates.sort(
            key=lambda x: (-x[1]["final_score"], x[0]["candidate_id"])
        )

    # Extract top 100 for submission, 1000 for dashboard
    top_1000 = scored_candidates[:1000]
    logger.info(f"Extracted top {len(top_1000)} ranked candidates for dashboard (Top 100 for submission).")

    # 6. Stage 5: Reasoning Generation
    import json
    ranked_rows = []
    dashboard_shortlist = []
    with StageProfiler("Rationale Generation") as prof:
        generator = ReasoningGenerator()
        for rank_idx, (c, breakdown) in enumerate(top_1000):
            rank = rank_idx + 1
            reasoning = generator.generate_reasoning(c, c["matched_template_ids"], breakdown)
            
            if rank <= 100:
                ranked_rows.append({
                    "candidate_id": c["candidate_id"],
                    "rank": rank,
                    "score": breakdown["final_score"],
                    "reasoning": reasoning
                })
                
            dashboard_shortlist.append({
                "rank": rank,
                "candidate_id": c["candidate_id"],
                "score_breakdown": breakdown,
                "reasoning": reasoning,
                "profile": c.get("profile", {}),
                "skills": c.get("skills", []),
                "redrob_signals": c.get("redrob_signals", {}),
                "career_history": c.get("career_history", []),
                "matched_template_ids": c.get("matched_template_ids", []),
                "has_t1": c.get("has_t1", False)
            })

    # 7. Stage 6: Save Outputs
    with StageProfiler("Saving Outputs") as prof:
        save_submission_csv(ranked_rows, args.out)
        
        base_dir = os.path.dirname(os.path.abspath(args.out))
        
        stats = {
            "total_raw": raw_count,
            "total_clean": clean_count,
            "total_anomalies": raw_count - clean_count,
            "tier1_count": tier1_count,
            "tier2_count": tier2_count,
            "total_shortlisted": len(clean_candidates_t1_t2)
        }
        stats_path = os.path.join(base_dir, "pipeline_stats.json")
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
            
        shortlist_path = os.path.join(base_dir, "dashboard_shortlist.json")
        with open(shortlist_path, "w", encoding="utf-8") as f:
            json.dump(dashboard_shortlist, f, indent=2)
        
    logger.info(f"Ranker pipeline completed successfully. Outputs saved in: {base_dir}")

if __name__ == "__main__":
    main()
