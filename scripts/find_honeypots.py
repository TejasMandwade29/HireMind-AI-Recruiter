import json
import collections
from datetime import datetime

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

title_keywords = ["ai", "ml", "machine learning", "data scientist", "nlp", "computer vision", "retrieval", "search", "ranking", "recommend"]

anomalies = []

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c.get("candidate_id")
        prof = c.get("profile", {})
        history = c.get("career_history", [])
        skills = c.get("skills", [])
        edu = c.get("education", [])
        signals = c.get("redrob_signals", {})
        
        reasons = []
        
        # Check 1: Expert proficiency in skills with 0 months used
        expert_zero = [s.get("name") for s in skills if s.get("proficiency") == "expert" and s.get("duration_months") == 0]
        if expert_zero:
            reasons.append(f"expert_skills_with_0_months: {expert_zero}")
            
        # Check 2: Single job duration exceeds total experience
        yoe = prof.get("years_of_experience", 0)
        yoe_months = yoe * 12
        for i, job in enumerate(history):
            dur = job.get("duration_months", 0)
            if dur > yoe_months + 1:
                reasons.append(f"job_{i}_duration_{dur}_months_exceeds_yoe_{yoe}_years")
                
        # Check 3: Current company size / age / details anomaly
        # Let's check if the company is "founded 3 years ago" but they worked there 8 years.
        # Wait, how to find when a company was founded? Is there any mention of company founding year?
        # Maybe in the job description or description of the company in career history?
        # Let's inspect descriptions in career history.
        for i, job in enumerate(history):
            desc = job.get("description", "")
            comp = job.get("company", "")
            # Look for years in description, like "founded in 2023" or similar
            if "founded" in desc.lower():
                # Extract year
                for word in desc.split():
                    clean_word = "".join(filter(str.isdigit, word))
                    if len(clean_word) == 4:
                        year = int(clean_word)
                        # Check start date of job
                        start_date = job.get("start_date")
                        if start_date:
                            start_yr = int(start_date.split("-")[0])
                            if start_yr < year:
                                reasons.append(f"job_{i}_started_{start_yr}_before_company_{comp}_founded_{year}")
                                
        # Check 4: Education completion vs start of work history
        # If someone started a full-time job before college started or graduated?
        # Sometimes people work during college, but let's check if there are extreme cases.
        
        # Check 5: Expected salary min > max
        sal = signals.get("expected_salary_range_inr_lpa", {})
        if sal and sal.get("min", 0) > sal.get("max", 0):
            reasons.append(f"expected_salary_min_{sal.get('min')}_greater_than_max_{sal.get('max')}")
            
        # Check 6: Check for "expert" in 10 skills with 0 years used (as mentioned in submission_spec)
        expert_count = sum(1 for s in skills if s.get("proficiency") == "expert")
        expert_zero_count = sum(1 for s in skills if s.get("proficiency") == "expert" and s.get("duration_months") == 0)
        if expert_zero_count >= 10:
            reasons.append(f"expert_skills_0_months_count_{expert_zero_count}_ge_10")
            
        # Check 7: Notice period negative or > 180
        np = signals.get("notice_period_days", 0)
        if np < 0 or np > 180:
            reasons.append(f"notice_period_days_{np}_out_of_range")
            
        if reasons:
            anomalies.append({
                "candidate_id": cid,
                "name": prof.get("anonymized_name"),
                "title": prof.get("current_title"),
                "yoe": yoe,
                "reasons": reasons
            })

print(f"Total anomalies found: {len(anomalies)}")
# Let's count categories of anomalies
counts = collections.Counter()
for a in anomalies:
    for r in a["reasons"]:
        type_r = r.split(":")[0]
        counts[type_r] += 1
        
print("\nAnomaly types and counts:")
for k, v in counts.items():
    print(f"  {k}: {v}")
    
# Let's check how many fit our AI/ML engineer profile keywords
ai_anom = 0
for a in anomalies:
    title_lower = str(a["title"]).lower()
    if any(kw in title_lower for kw in title_keywords):
        ai_anom += 1
print(f"\nAnomalous candidates with AI/ML titles: {ai_anom}")

print("\nSample anomalies (first 15):")
for a in anomalies[:15]:
    print(f"  ID: {a['candidate_id']}, Name: {a['name']}, Title: {a['title']}, YOE: {a['yoe']}")
    for r in a["reasons"]:
        print(f"    - {r}")
