import json
from datetime import datetime

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

# The unique index of job descriptions that represent AI/ML/Search/Ranking:
# In our previous script, the descriptions [28] to [44] were the ones. Let's list their exact texts to match.
ai_descriptions = [
    "Owned the ranking layer for an e-commerce search product, evolving it from a hand-tuned scoring function to a learning-to-rank model over 9 months.",
    "Trained and shipped multiple ranking models for our product's discovery feed using XGBoost and LightGBM.",
    "Developed a semantic search feature for an internal knowledge base of ~500K documents.",
    "Implemented a RAG-based customer support chatbot integrated with our existing ticketing system.",
    "Built a content recommendation system serving 10M+ users that combined collaborative filtering with content-based ranking.",
    "Built and operated production ML pipelines using MLflow for experiment tracking,",
    "Fine-tuned LLaMA-2-7B and Mistral-7B variants using LoRA and QLoRA for domain-specific candidate-JD matching.",
    "Built a RAG-based ranking pipeline serving 50M+ queries per month for an internal recruiter-facing search product.",
    "Built and shipped a production recommendation system at a marketplace product, going from offline experimentation to live A/B test in 5 months.",
    "Owned the end-to-end ranking pipeline at a recommendations-heavy consumer product: candidate sourcing",
    "Owned the design and rollout of a large-scale semantic search system serving an internal corpus of 35M+ items.",
    "Led the migration from keyword-based to embedding-based search across a 30M+ candidate corpus over 8 months.",
    "Built systems that understand what users are looking for and connect them to the most relevant matches across a large dataset.",
    "Shipped the personalization infrastructure: the system that learns from user behavior and improves relevance over time.",
    "Designed the ranking layer for the company's flagship product: how do we surface the right thing at the right time,",
    "Owned the search and discovery experience end-to-end at a consumer product, from how content is represented internally",
    "Led the engineering team building infrastructure to surface relevant content to users at scale."
]

def contains_ai_desc(history):
    for job in history:
        desc = job.get("description", "")
        for ai_d in ai_descriptions:
            if ai_d in desc:
                return True
    return False

all_ai_candidates = []
clean_ai_candidates = []
anomalous_ai_candidates = []

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        history = c.get("career_history", [])
        
        if contains_ai_desc(history):
            all_ai_candidates.append(c)
            
            # Anomaly Checks:
            prof = c.get("profile", {})
            skills = c.get("skills", [])
            signals = c.get("redrob_signals", {})
            yoe = prof.get("years_of_experience", 0)
            yoe_months = yoe * 12
            
            reasons = []
            
            # Check 1: Expert skills with 0 months
            expert_zero = [s.get("name") for s in skills if s.get("proficiency") == "expert" and s.get("duration_months") == 0]
            if expert_zero:
                reasons.append(f"expert_skills_0_months: {expert_zero}")
                
            # Check 2: Single job duration exceeds YOE
            for i, job in enumerate(history):
                dur = job.get("duration_months", 0)
                if dur > yoe_months + 1:
                    reasons.append(f"job_{i}_duration_{dur}_months_exceeds_yoe_{yoe}_years")
                    
            # Check 3: Expected salary min > max
            sal = signals.get("expected_salary_range_inr_lpa", {})
            if sal and sal.get("min", 0) > sal.get("max", 0):
                reasons.append(f"expected_salary_min_{sal.get('min')}_greater_than_max_{sal.get('max')}")
                
            # Check 4: Future dates
            future_dates = False
            for job in history:
                start = job.get("start_date")
                end = job.get("end_date")
                if start and datetime.strptime(start, "%Y-%m-%d") > datetime(2026, 6, 18):
                    future_dates = True
                if end and datetime.strptime(end, "%Y-%m-%d") > datetime(2026, 6, 18):
                    future_dates = True
            if future_dates:
                reasons.append("career_history_has_future_dates")
                
            # Check 5: Education vs career start mismatch
            # Let's check if they graduated and how many years of experience they have relative to graduation.
            # If their stated years of experience is 8, but they graduated in 2025 (1 year ago)
            # and they have no other education that started 8 years ago.
            edu_years = [edu.get("end_year") for edu in c.get("education", []) if edu.get("end_year")]
            if edu_years:
                min_grad_year = min(edu_years)
                # Experience post-graduation (current year is 2026)
                post_grad_years = 2026 - min_grad_year
                # If they graduated and have YOE way more than time since graduation
                # (e.g. YOE is 8, but they graduated in 2024 - 2 years ago - and first job started in 2018 - 8 years ago,
                # which means they worked for 6 years during college. That is possible, but let's check if there are extreme cases)
                pass
                
            if reasons:
                anomalous_ai_candidates.append((c, reasons))
            else:
                clean_ai_candidates.append(c)

print(f"Total AI/ML candidates: {len(all_ai_candidates)}")
print(f"Clean AI/ML candidates: {len(clean_ai_candidates)}")
print(f"Anomalous AI/ML candidates: {len(anomalous_ai_candidates)}")

print("\n--- SAMPLE CLEAN AI/ML CANDIDATES (First 5) ---")
for i, c in enumerate(clean_ai_candidates[:5]):
    prof = c.get("profile", {})
    signals = c.get("redrob_signals", {})
    print(f"ID: {c.get('candidate_id')} | Name: {prof.get('anonymized_name')} | YOE: {prof.get('years_of_experience')} | Location: {prof.get('location')}, {prof.get('country')}")
    print(f"  Current Title: {prof.get('current_title')} at {prof.get('current_company')}")
    print(f"  Notice Period: {signals.get('notice_period_days')} days | Sal: {signals.get('expected_salary_range_inr_lpa')} LPA | Active: {signals.get('last_active_date')}")

print("\n--- SAMPLE ANOMALOUS AI/ML CANDIDATES (First 5) ---")
for i, (c, reasons) in enumerate(anomalous_ai_candidates[:5]):
    prof = c.get("profile", {})
    print(f"ID: {c.get('candidate_id')} | Name: {prof.get('anonymized_name')} | YOE: {prof.get('years_of_experience')} | Current: {prof.get('current_title')}")
    print(f"  Anomalies: {reasons}")
