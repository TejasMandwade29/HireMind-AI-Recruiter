import json
from datetime import datetime

unique_desc_file = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\unique_descriptions.txt"
candidates_file = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

# 1. Load the 44 unique descriptions
descriptions = []
current_desc = []
with open(unique_desc_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("Text: "):
            desc_text = line[6:].strip()
            descriptions.append(desc_text)

print(f"Loaded {len(descriptions)} unique descriptions from text file.")

# We will index them 1-based to match our file
desc_to_id = {desc: idx+1 for idx, desc in enumerate(descriptions)}

# Let's write a robust matcher that works even with minor spacing/encoding variations
def get_desc_id(text):
    if not text:
        return None
    text_clean = text.strip().replace("", "").replace("—", "-").replace("", "'").replace("'", "")
    for desc, idx in desc_to_id.items():
        desc_clean = desc.strip().replace("", "").replace("—", "-").replace("", "'").replace("'", "")
        if desc_clean in text_clean or text_clean in desc_clean:
            return idx
    return None

# AI/ML/Search/Ranking description IDs are [28, 44]
# Let's define the tiers of AI roles:
# Tier 1 (High-end AI/ML/Search/Ranking): 28 to 44
# Tier 2 (Mid-level ML/Data Science): 22 to 27
# Tier 3 (Data Infrastructure / Devops / Backend): 10 to 21
# Tier 4 (Non-tech / unrelated): 1 to 9

tier_1_ids = set(range(28, 45))
tier_2_ids = set(range(22, 28))

total_candidates = 0
tier_1_candidates = []
tier_2_candidates = []

with open(candidates_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        total_candidates += 1
        
        history = c.get("career_history", [])
        job_ids = []
        for job in history:
            desc = job.get("description", "")
            did = get_desc_id(desc)
            if did:
                job_ids.append(did)
                
        c["job_desc_ids"] = job_ids
        
        # Check if candidate has Tier 1 or Tier 2 jobs
        has_t1 = any(did in tier_1_ids for did in job_ids)
        has_t2 = any(did in tier_2_ids for did in job_ids)
        
        if has_t1:
            tier_1_candidates.append(c)
        elif has_t2:
            tier_2_candidates.append(c)

print(f"\n--- Classification Results ---")
print(f"Total Candidates: {total_candidates}")
print(f"Tier 1 (High-end AI/ML/Search/Ranking) Candidates: {len(tier_1_candidates)}")
print(f"Tier 2 (Mid-level ML/Data Science) Candidates: {len(tier_2_candidates)}")

# Let's perform a detailed analysis of Tier 1 candidates
print("\n--- Detailed Analysis of Tier 1 Candidates ---")
# Count by location
locations = {}
countries = {}
yoe_dist = []
active_30d = 0
open_to_work = 0
verified_contact = 0
avg_response_rate = []
avg_response_time = []
notice_periods = {}
salary_ranges = []
anomalous_t1 = []
clean_t1 = []

for c in tier_1_candidates:
    prof = c.get("profile", {})
    signals = c.get("redrob_signals", {})
    
    loc = prof.get("location")
    locations[loc] = locations.get(loc, 0) + 1
    
    ctr = prof.get("country")
    countries[ctr] = countries.get(ctr, 0) + 1
    
    yoe = prof.get("years_of_experience", 0)
    yoe_dist.append(yoe)
    
    # Active/Open
    last_act = signals.get("last_active_date")
    is_active = False
    if last_act:
        try:
            dt = datetime.strptime(last_act, "%Y-%m-%d")
            if dt >= datetime(2026, 5, 18):
                is_active = True
        except:
            pass
    if is_active:
        active_30d += 1
        
    if signals.get("open_to_work_flag"):
        open_to_work += 1
        
    if signals.get("verified_email") and signals.get("verified_phone"):
        verified_contact += 1
        
    avg_response_rate.append(signals.get("recruiter_response_rate", 0))
    avg_response_time.append(signals.get("avg_response_time_hours", 0))
    
    np = signals.get("notice_period_days", 0)
    notice_periods[np] = notice_periods.get(np, 0) + 1
    
    sal = signals.get("expected_salary_range_inr_lpa", {})
    
    # Anomaly check
    reasons = []
    
    # Salary min > max
    if sal and sal.get("min", 0) > sal.get("max", 0):
        reasons.append(f"Salary min ({sal.get('min')}) > max ({sal.get('max')})")
        
    # Single job exceeds YOE
    yoe_months = yoe * 12
    for idx, job in enumerate(c.get("career_history", [])):
        dur = job.get("duration_months", 0)
        if dur > yoe_months + 1:
            reasons.append(f"Job {idx} duration ({dur} mos) > total YOE ({yoe} yrs)")
            
    # Expert skills with 0 months
    skills = c.get("skills", [])
    expert_zero = [s.get("name") for s in skills if s.get("proficiency") == "expert" and s.get("duration_months") == 0]
    if expert_zero:
        reasons.append(f"Expert skills with 0 duration: {expert_zero}")
        
    # Future dates in history
    future_dates = False
    for job in c.get("career_history", []):
        start = job.get("start_date")
        end = job.get("end_date")
        if start and datetime.strptime(start, "%Y-%m-%d") > datetime(2026, 6, 18):
            future_dates = True
        if end and datetime.strptime(end, "%Y-%m-%d") > datetime(2026, 6, 18):
            future_dates = True
    if future_dates:
        reasons.append("Future dates in career history")
        
    if reasons:
        anomalous_t1.append((c, reasons))
    else:
        clean_t1.append(c)

print(f"Total Tier 1 candidates: {len(tier_1_candidates)}")
print(f"Clean Tier 1 candidates: {len(clean_t1)}")
print(f"Anomalous Tier 1 candidates: {len(anomalous_t1)}")

print("\nLocation distribution for Tier 1:")
for k, v in sorted(locations.items(), key=lambda x: x[1], reverse=True):
    print(f"  {k}: {v}")
    
print("\nCountry distribution for Tier 1:")
for k, v in sorted(countries.items(), key=lambda x: x[1], reverse=True):
    print(f"  {k}: {v}")

print(f"\nYOE range: {min(yoe_dist)} to {max(yoe_dist)} years")
print(f"YOE mean: {sum(yoe_dist)/len(yoe_dist):.2f} years")

print(f"\nEngagement Signals:")
print(f"  Active in last 30d: {active_30d} ({active_30d/len(tier_1_candidates)*100:.2f}%)")
print(f"  Open to work: {open_to_work} ({open_to_work/len(tier_1_candidates)*100:.2f}%)")
print(f"  Both email & phone verified: {verified_contact} ({verified_contact/len(tier_1_candidates)*100:.2f}%)")
print(f"  Mean response rate: {sum(avg_response_rate)/len(avg_response_rate)*100:.2f}%")
print(f"  Mean response time: {sum(avg_response_time)/len(avg_response_time):.2f} hours")

print("\nNotice period distribution:")
for k, v in sorted(notice_periods.items()):
    print(f"  {k} days: {v}")

print("\nAnomalous candidate list in Tier 1 (Honeypots!):")
for idx, (c, reasons) in enumerate(anomalous_t1):
    print(f"  [{idx+1}] ID: {c.get('candidate_id')} - {c.get('profile', {}).get('anonymized_name')} - YOE: {c.get('profile', {}).get('years_of_experience')}")
    print(f"      Reasons: {reasons}")
