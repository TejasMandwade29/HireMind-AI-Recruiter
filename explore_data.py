import json
import collections
from datetime import datetime

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

total_candidates = 0
locations = collections.Counter()
countries = collections.Counter()
yoe = []
current_titles = collections.Counter()
industries = collections.Counter()
company_sizes = collections.Counter()
education_tiers = collections.Counter()
skills = collections.Counter()
git_scores = []
open_to_work = 0
email_verified = 0
phone_verified = 0
linkedin_connected = 0
active_in_30d = 0 # active since 2026-05-18

# For scanning anomalies (potential honeypots)
anomalous_candidates = []

print("Starting exploration of candidates.jsonl...")

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        total_candidates += 1
        
        prof = c.get("profile", {})
        locations[prof.get("location")] += 1
        countries[prof.get("country")] += 1
        yoe.append(prof.get("years_of_experience", 0))
        current_titles[prof.get("current_title")] += 1
        industries[prof.get("current_industry")] += 1
        company_sizes[prof.get("current_company_size")] += 1
        
        for edu in c.get("education", []):
            education_tiers[edu.get("tier")] += 1
            
        for sk in c.get("skills", []):
            skills[sk.get("name")] += 1
            
        signals = c.get("redrob_signals", {})
        git_scores.append(signals.get("github_activity_score", -1))
        if signals.get("open_to_work_flag"):
            open_to_work += 1
        if signals.get("verified_email"):
            email_verified += 1
        if signals.get("verified_phone"):
            phone_verified += 1
        if signals.get("linkedin_connected"):
            linkedin_connected += 1
            
        # Check active date
        last_active = signals.get("last_active_date")
        if last_active:
            try:
                dt = datetime.strptime(last_active, "%Y-%m-%d")
                if dt >= datetime(2026, 5, 18): # active in last 30 days
                    active_in_30d += 1
            except:
                pass
                
        # Honeypot checks:
        # Check 1: Expert proficiency in skills with 0 months used
        expert_zero_months = []
        for sk in c.get("skills", []):
            if sk.get("proficiency") == "expert" and sk.get("duration_months") == 0:
                expert_zero_months.append(sk.get("name"))
                
        # Check 2: Total duration of career history exceeds possible duration (e.g. starting career before education start if education was long, or years of experience mismatch)
        # Let's sum duration of all jobs in career history (in months) and check if it exceeds (years_of_experience * 12 + 12) or something.
        career_durations = [j.get("duration_months", 0) for j in c.get("career_history", [])]
        total_career_months = sum(career_durations)
        stated_experience_months = prof.get("years_of_experience", 0) * 12
        
        # Check 3: Current job start date and end date contradiction or overlapping current job
        # Let's check if there are specific dates that are in the future relative to 2026-06-18
        future_dates = False
        for job in c.get("career_history", []):
            start = job.get("start_date")
            end = job.get("end_date")
            if start and datetime.strptime(start, "%Y-%m-%d") > datetime(2026, 6, 18):
                future_dates = True
            if end and datetime.strptime(end, "%Y-%m-%d") > datetime(2026, 6, 18):
                future_dates = True
                
        # Check 4: Notice period and expected salary anomalies (e.g. max salary < min salary)
        salary_range = signals.get("expected_salary_range_inr_lpa", {})
        salary_anomaly = False
        if salary_range:
            s_min = salary_range.get("min", 0)
            s_max = salary_range.get("max", 0)
            if s_max < s_min:
                salary_anomaly = True
                
        # Check 5: Stated years of experience vs education completion
        # If someone graduated in 2024 but has 10 years of experience, that's possible (if they worked before/during college),
        # but let's see if there is any candidate with a very clear impossibility, like graduating in 2029 (future) and already having 10 years of experience.
        edu_anomaly = False
        for edu in c.get("education", []):
            end_yr = edu.get("end_year")
            if end_yr and end_yr > 2026 and not edu.get("is_current", False):
                # wait, check if end_year is greater than 2026
                pass
                
        # Collect anomalies
        anomaly_reasons = []
        if len(expert_zero_months) >= 5: # e.g. expert in 5+ skills with 0 months used
            anomaly_reasons.append(f"Expert in {len(expert_zero_months)} skills with 0 months used")
        if total_career_months > stated_experience_months + 24: # more than 2 years discrepancy
            # Note: overlapping jobs can happen, but let's check if it's way off
            pass
        if salary_anomaly:
            anomaly_reasons.append("Expected max salary < min salary")
        if future_dates:
            anomaly_reasons.append("Career history has future dates")
            
        # Specific honeypot hints: "8 years of experience at a company founded 3 years ago; 'expert' proficiency in 10 skills with 0 years used"
        # Let's inspect some candidates with expert proficiency and 0 duration
        expert_zero_all = [sk for sk in c.get("skills", []) if sk.get("proficiency") == "expert" and sk.get("duration_months") == 0]
        if len(expert_zero_all) >= 5:
            anomaly_reasons.append(f"Expert in {len(expert_zero_all)} skills with 0 duration")
            
        # Mismatch of years of experience: total years of experience is e.g. 8 years, but a single job duration is 120 months (10 years)
        single_job_exceeds = False
        for job in c.get("career_history", []):
            dur = job.get("duration_months", 0)
            if dur > stated_experience_months + 3:
                single_job_exceeds = True
                anomaly_reasons.append(f"Single job duration ({dur} mos) exceeds total experience ({prof.get('years_of_experience')} yrs)")
                break
                
        # If any anomaly detected, add to list
        if anomaly_reasons:
            anomalous_candidates.append({
                "candidate_id": c.get("candidate_id"),
                "name": prof.get("anonymized_name"),
                "experience": prof.get("years_of_experience"),
                "reasons": anomaly_reasons,
                "skills_expert_zero": [sk.get("name") for sk in c.get("skills", []) if sk.get("proficiency") == "expert" and sk.get("duration_months") == 0]
            })

print(f"Total Candidates parsed: {total_candidates}")
print("\n--- Basic Statistics ---")
print(f"Average Years of Experience: {sum(yoe)/len(yoe):.2f}")
print(f"Min Years of Experience: {min(yoe)}")
print(f"Max Years of Experience: {max(yoe)}")
print(f"Open to work: {open_to_work} ({open_to_work/total_candidates*100:.2f}%)")
print(f"Email verified: {email_verified} ({email_verified/total_candidates*100:.2f}%)")
print(f"Phone verified: {phone_verified} ({phone_verified/total_candidates*100:.2f}%)")
print(f"LinkedIn connected: {linkedin_connected} ({linkedin_connected/total_candidates*100:.2f}%)")
print(f"Active in last 30 days: {active_in_30d} ({active_in_30d/total_candidates*100:.2f}%)")

print("\nTop 10 Locations:")
for loc, count in locations.most_common(10):
    print(f"  {loc}: {count}")

print("\nTop 10 Countries:")
for ctr, count in countries.most_common(10):
    print(f"  {ctr}: {count}")

print("\nTop 10 Current Titles:")
for tit, count in current_titles.most_common(10):
    print(f"  {tit}: {count}")

print("\nTop 10 Current Industries:")
for ind, count in industries.most_common(10):
    print(f"  {ind}: {count}")

print("\nEducation Tier counts:")
for tier, count in education_tiers.items():
    print(f"  {tier}: {count}")

print("\nNumber of Anomalous Candidates detected (potential honeypots):", len(anomalous_candidates))
if anomalous_candidates:
    print("\nSample Anomalous Candidates:")
    for ac in anomalous_candidates[:10]:
        print(f"  ID: {ac['candidate_id']}, Name: {ac['name']}, YOE: {ac['experience']}, Reasons: {ac['reasons']}")
