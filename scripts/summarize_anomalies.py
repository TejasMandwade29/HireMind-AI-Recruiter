import json
import collections
from datetime import datetime

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

anom_types = collections.Counter()
expert_zero_dur_counts = collections.Counter()
career_yoe_violations = 0
future_date_violations = 0
salary_violations = 0
founded_before_violations = 0
single_job_exceeds_violations = 0
expert_0_months_10plus = 0

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        prof = c.get("profile", {})
        history = c.get("career_history", [])
        skills = c.get("skills", [])
        signals = c.get("redrob_signals", {})
        yoe = prof.get("years_of_experience", 0)
        yoe_months = yoe * 12
        
        # 1. Expert skills with 0 months used
        expert_zero = [s.get("name") for s in skills if s.get("proficiency") == "expert" and s.get("duration_months") == 0]
        if expert_zero:
            anom_types["expert_skills_with_0_months"] += 1
            if len(expert_zero) >= 10:
                expert_0_months_10plus += 1
                
        # 2. Single job exceeds YOE
        single_job_exceeds = False
        for job in history:
            dur = job.get("duration_months", 0)
            if dur > yoe_months + 1:
                single_job_exceeds = True
        if single_job_exceeds:
            single_job_exceeds_violations += 1
            anom_types["single_job_exceeds_yoe"] += 1
            
        # 3. Job started before company founded (from description)
        started_before = False
        for job in history:
            desc = job.get("description", "")
            comp = job.get("company", "")
            if "founded" in desc.lower():
                for word in desc.split():
                    clean_word = "".join(filter(str.isdigit, word))
                    if len(clean_word) == 4:
                        year = int(clean_word)
                        start_date = job.get("start_date")
                        if start_date:
                            start_yr = int(start_date.split("-")[0])
                            if start_yr < year:
                                started_before = True
        if started_before:
            founded_before_violations += 1
            anom_types["started_before_founded"] += 1
            
        # 4. Expected salary min > max
        sal = signals.get("expected_salary_range_inr_lpa", {})
        if sal and sal.get("min", 0) > sal.get("max", 0):
            salary_violations += 1
            anom_types["salary_min_gt_max"] += 1
            
        # 5. Future dates
        future_dates = False
        for job in history:
            start = job.get("start_date")
            end = job.get("end_date")
            if start and datetime.strptime(start, "%Y-%m-%d") > datetime(2026, 6, 18):
                future_dates = True
            if end and datetime.strptime(end, "%Y-%m-%d") > datetime(2026, 6, 18):
                future_dates = True
        if future_dates:
            future_date_violations += 1
            anom_types["future_dates"] += 1

print("Summary of Anomaly Categories:")
for k, v in anom_types.items():
    print(f"  {k}: {v}")
    
print(f"\nSpecific Violations details:")
print(f"  Salary Min > Max: {salary_violations}")
print(f"  Single Job Exceeds YOE: {single_job_exceeds_violations}")
print(f"  Job Started Before Company Founded: {founded_before_violations}")
print(f"  Future Dates in Career History: {future_date_violations}")
print(f"  Expert Skills with 0 Months: {anom_types['expert_skills_with_0_months']}")
print(f"  10+ Expert Skills with 0 Months: {expert_0_months_10plus}")

# Let's count how many candidates are "honeypots" under the submission_spec's exact criteria:
# e.g., "8 years of experience at a company founded 3 years ago" OR "expert proficiency in 10 skills with 0 years used"
# Let's check how many fit these.
honeypots_count = 0
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        prof = c.get("profile", {})
        history = c.get("career_history", [])
        skills = c.get("skills", [])
        
        is_honeypot = False
        
        # Check A: Expert in 10+ skills with 0 months
        expert_zero_count = sum(1 for s in skills if s.get("proficiency") == "expert" and s.get("duration_months") == 0)
        if expert_zero_count >= 10:
            is_honeypot = True
            
        # Check B: Work duration exceeds time company has been founded
        # "8 years of experience at a company founded 3 years ago"
        # Let's see if there is a company founded X years ago and they worked there for Y years where Y > X.
        for job in history:
            desc = job.get("description", "")
            comp = job.get("company", "")
            start_date = job.get("start_date")
            end_date = job.get("end_date") or "2026-06-18" # use current date as end if null
            
            # calculate job duration in years from dates
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                job_years = (end_dt - start_dt).days / 365.25
            except:
                job_years = 0
                
            if "founded" in desc.lower():
                for word in desc.split():
                    clean_word = "".join(filter(str.isdigit, word))
                    if len(clean_word) == 4:
                        founded_year = int(clean_word)
                        # Company age at end of job
                        end_year = int(end_date.split("-")[0])
                        company_age = end_year - founded_year
                        # If candidate worked there longer than company age
                        # or started working before company was founded
                        if job_years > company_age + 0.5 or start_dt.year < founded_year:
                            is_honeypot = True
                            
        if is_honeypot:
            honeypots_count += 1

print(f"\nStrict Honeypots Count (based on exact rules): {honeypots_count}")
