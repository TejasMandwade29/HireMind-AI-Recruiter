import json
from datetime import datetime

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

ai_keywords = ["ai ", " ai", "ml", "machine learning", "data scientist", "nlp", "computer vision", "retrieval", "search", "ranking", "recommend"]

relevant_candidates = []

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        prof = c.get("profile", {})
        title = str(prof.get("current_title", "")).lower()
        headline = str(prof.get("headline", "")).lower()
        summary = str(prof.get("summary", "")).lower()
        
        # Check if title or headline matches AI/ML keywords
        is_relevant = False
        if any(kw in title for kw in ai_keywords) or any(kw in headline for kw in ai_keywords):
            is_relevant = True
            
        # Also check past titles
        for job in c.get("career_history", []):
            jtitle = str(job.get("title", "")).lower()
            if any(kw in jtitle for kw in ai_keywords):
                is_relevant = True
                break
                
        if is_relevant:
            relevant_candidates.append(c)

print(f"Total candidates matching AI/ML keywords: {len(relevant_candidates)}")

# Print a few samples of AI/ML candidates in detail
print("\n--- SAMPLE AI/ML CANDIDATES (First 5) ---")
for i, c in enumerate(relevant_candidates[:5]):
    prof = c.get("profile", {})
    history = c.get("career_history", [])
    edu = c.get("education", [])
    skills = c.get("skills", [])
    signals = c.get("redrob_signals", {})
    
    print("=" * 60)
    print(f"Candidate #{i+1}: {c.get('candidate_id')} - {prof.get('anonymized_name')}")
    print(f"Headline: {prof.get('headline')}")
    print(f"Location: {prof.get('location')}, {prof.get('country')}")
    print(f"YOE: {prof.get('years_of_experience')} | Current: {prof.get('current_title')} at {prof.get('current_company')} ({prof.get('current_industry')})")
    
    print("\nCareer History:")
    for job in history:
        print(f"  - {job.get('title')} at {job.get('company')} ({job.get('duration_months')} mos, Current: {job.get('is_current')}, Industry: {job.get('industry')})")
        print(f"    Desc: {job.get('description')[:120]}...")
        
    print("\nEducation:")
    for school in edu:
        print(f"  - {school.get('degree')} in {school.get('field_of_study')} from {school.get('institution')} ({school.get('tier')}, Grad: {school.get('end_year')})")
        
    print("\nTop Skills (first 5):")
    for sk in skills[:5]:
        print(f"  - {sk.get('name')}: {sk.get('proficiency')} ({sk.get('duration_months')} mos, Endorse: {sk.get('endorsements')})")
        
    print("\nSignals:")
    print(f"  Notice Period: {signals.get('notice_period_days')} days | Sal: {signals.get('expected_salary_range_inr_lpa')} LPA")
    print(f"  Active: {signals.get('last_active_date')} | Response Rate: {signals.get('recruiter_response_rate')} | Avg Response: {signals.get('avg_response_time_hours')} hrs")
    print(f"  GitHub Score: {signals.get('github_activity_score')} | Saved by recruiters (30d): {signals.get('saved_by_recruiters_30d')}")
    print(f"  Email/Phone/LI: {signals.get('verified_email')}/{signals.get('verified_phone')}/{signals.get('linkedin_connected')}")
