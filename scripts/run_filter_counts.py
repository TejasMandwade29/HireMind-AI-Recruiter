import json
import os
import sys

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.filters import (
    has_salary_anomaly,
    has_duration_anomaly,
    has_skill_anomaly,
    is_clean_candidate
)

candidates_file = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

total_candidates = 0
salary_removed = 0
duration_removed = 0
skill_removed = 0
clean_remaining = 0

print("Scanning candidates.jsonl for anomaly counts...")

with open(candidates_file, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        total_candidates += 1
        c = json.loads(line)
        
        prof = c.get("profile", {})
        history = c.get("career_history", [])
        skills = c.get("skills", [])
        signals = c.get("redrob_signals", {})
        
        yoe = prof.get("years_of_experience", 0.0)
        salary = signals.get("expected_salary_range_inr_lpa", {})
        
        # We track each anomaly independently to get individual counts
        is_salary_anom = has_salary_anomaly(salary)
        is_duration_anom = has_duration_anomaly(history, yoe)
        is_skill_anom = has_skill_anomaly(skills)
        
        if is_salary_anom:
            salary_removed += 1
        if is_duration_anom:
            duration_removed += 1
        if is_skill_anom:
            skill_removed += 1
            
        # Is clean candidate check
        if is_clean_candidate(c):
            clean_remaining += 1

print(f"\n--- Validation Report ---")
print(f"Total Candidates: {total_candidates}")
print(f"Salary Anomaly Flagged: {salary_removed} ({salary_removed/total_candidates*100:.2f}%)")
print(f"Duration Anomaly Flagged: {duration_removed} ({duration_removed/total_candidates*100:.2f}%)")
print(f"Skill Anomaly Flagged: {skill_removed} ({skill_removed/total_candidates*100:.2f}%)")
print(f"Total Clean Candidates Remaining: {clean_remaining} ({clean_remaining/total_candidates*100:.2f}%)")
