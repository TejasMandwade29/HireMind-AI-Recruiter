import json
from datetime import datetime

unique_desc_file = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\unique_descriptions.txt"
candidates_file = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

descriptions = []
with open(unique_desc_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("Text: "):
            descriptions.append(line[6:].strip())

desc_to_id = {desc: idx+1 for idx, desc in enumerate(descriptions)}

def get_desc_id(text):
    if not text:
        return None
    text_clean = text.strip().replace("", "").replace("—", "-").replace("", "'").replace("'", "")
    for desc, idx in desc_to_id.items():
        desc_clean = desc.strip().replace("", "").replace("—", "-").replace("", "'").replace("'", "")
        if desc_clean in text_clean or text_clean in desc_clean:
            return idx
    return None

tier_1_ids = set(range(28, 45))

# We'll collect signals for Tier 1 vs General
t1_signals = []
gen_signals = []

count = 0
with open(candidates_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        count += 1
        
        history = c.get("career_history", [])
        job_ids = []
        for job in history:
            desc = job.get("description", "")
            did = get_desc_id(desc)
            if did:
                job_ids.append(did)
                
        has_t1 = any(did in tier_1_ids for did in job_ids)
        sig = c.get("redrob_signals", {})
        
        # Check if they are anomalous (to avoid mixing honeypots in our distribution analysis)
        sal = sig.get("expected_salary_range_inr_lpa", {})
        is_anomalous = False
        if sal and sal.get("min", 0) > sal.get("max", 0):
            is_anomalous = True
            
        yoe = c.get("profile", {}).get("years_of_experience", 0)
        yoe_months = yoe * 12
        for idx, job in enumerate(history):
            dur = job.get("duration_months", 0)
            if dur > yoe_months + 1:
                is_anomalous = True
                
        # Extract numeric signals
        sig_data = {
            "profile_completeness": sig.get("profile_completeness_score", 0),
            "profile_views": sig.get("profile_views_received_30d", 0),
            "applications": sig.get("applications_submitted_30d", 0),
            "response_rate": sig.get("recruiter_response_rate", 0),
            "response_time": sig.get("avg_response_time_hours", 0),
            "connections": sig.get("connection_count", 0),
            "endorsements": sig.get("endorsements_received", 0),
            "notice_period": sig.get("notice_period_days", 0),
            "github_score": sig.get("github_activity_score", -1),
            "search_appearance": sig.get("search_appearance_30d", 0),
            "saved_by_recruiters": sig.get("saved_by_recruiters_30d", 0),
            "interview_rate": sig.get("interview_completion_rate", 0),
            "offer_rate": sig.get("offer_acceptance_rate", -1),
            "open_to_work": sig.get("open_to_work_flag", False),
            "verified_email": sig.get("verified_email", False),
            "verified_phone": sig.get("verified_phone", False),
            "linkedin": sig.get("linkedin_connected", False),
            "expected_salary_min": sal.get("min", 0),
            "expected_salary_max": sal.get("max", 0),
            "yoe": yoe,
            "is_anomalous": is_anomalous
        }
        
        if has_t1:
            t1_signals.append(sig_data)
        else:
            if count <= 5000: # collect a sample of general candidates
                gen_signals.append(sig_data)

# Let's print averages
def print_stats(name, data_list):
    print(f"\n===== Averages for {name} (N={len(data_list)}) =====")
    keys = ["yoe", "profile_completeness", "profile_views", "applications", "response_rate", "response_time", 
            "connections", "endorsements", "notice_period", "github_score", "search_appearance", "saved_by_recruiters", 
            "interview_rate", "offer_rate", "expected_salary_min", "expected_salary_max"]
    
    # Filter out anomalous candidates for averages
    clean_list = [d for d in data_list if not d["is_anomalous"]]
    anom_list = [d for d in data_list if d["is_anomalous"]]
    
    print(f"Clean count: {len(clean_list)}, Anomalous count: {len(anom_list)}")
    
    for k in keys:
        vals = [d[k] for d in clean_list]
        avg = sum(vals) / len(vals) if vals else 0
        v_min = min(vals) if vals else 0
        v_max = max(vals) if vals else 0
        print(f"  {k:20s}: Mean={avg:8.2f} | Min={v_min:8.2f} | Max={v_max:8.2f}")
        
    # Categorical/bool fractions
    bools = ["open_to_work", "verified_email", "verified_phone", "linkedin"]
    for b in bools:
        frac = sum(1 for d in clean_list if d[b]) / len(clean_list) if clean_list else 0
        print(f"  {b:20s}: Fraction={frac*100:6.2f}%")

print_stats("Clean Tier 1", t1_signals)
print_stats("Clean General Sample", gen_signals)
