import json
import collections

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

all_descriptions = collections.Counter()
mismatched_count = 0
total_jobs = 0

# Keywords for titles and description types to see how they align
title_keywords = {
    "project manager": ["project", "scrum", "agile", "delivery", "stakeholder"],
    "marketing manager": ["marketing", "seo", "brand", "campaign", "growth"],
    "sales executive": ["sales", "quota", "client", "customer", "pipeline", "deal"],
    "customer support": ["support", "ticket", "customer", "agent", "escalation"],
    "operations manager": ["operations", "logistics", "warehouse", "fulfillment", "kpi"],
    "accountant": ["accounting", "tax", "audit", "ledger", "close", "gaap"],
    "civil engineer": ["civil", "construction", "site", "design", "structural", "concrete"],
    "mechanical engineer": ["mechanical", "cad", "solidworks", "hardware", "prototype", "tooling"],
    "graphic designer": ["designer", "visual", "creative", "brand", "adobe", "figma"],
    "software engineer": ["software", "code", "development", "architecture", "git"],
    "ai engineer": ["ai", "ml", "machine learning", "nlp", "model", "inference", "embedding"],
    "data scientist": ["data", "model", "analysis", "statistics", "science", "python"]
}

coherent_count = 0
incoherent_count = 0
checked_candidates = 0

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        checked_candidates += 1
        history = c.get("career_history", [])
        
        is_coherent = True
        has_ai_jobs = False
        
        for job in history:
            title = str(job.get("title", "")).lower()
            desc = str(job.get("description", "")).lower()
            total_jobs += 1
            all_descriptions[job.get("description")] += 1
            
            # Check coherence: does the description align with the title?
            # We check if at least one keyword matching the title category appears in the description
            # or if the description matches another category much better.
            matched_category = None
            max_matches = 0
            
            # Count keyword matches for each category in the description
            matches = {}
            for cat, kws in title_keywords.items():
                match_count = sum(1 for kw in kws if kw in desc)
                matches[cat] = match_count
                if match_count > max_matches:
                    max_matches = match_count
                    matched_category = cat
            
            # Find which category the title belongs to
            title_category = None
            for cat in title_keywords:
                if cat in title:
                    title_category = cat
                    break
                    
            if title_category and matched_category and title_category != matched_category:
                # If another category has a high number of matches (e.g. >= 2) and the title's category has 0 or 1, it's incoherent
                if matches[matched_category] >= 2 and matches.get(title_category, 0) <= 0:
                    is_coherent = False
                    
            if "ai" in title or "ml" in title or "machine learning" in title or "nlp" in title or "data scientist" in title:
                has_ai_jobs = True
                
        if is_coherent:
            coherent_count += 1
        else:
            incoherent_count += 1
            
        if checked_candidates >= 1000:
            break

print(f"Checked first {checked_candidates} candidates:")
print(f"  Coherent profiles (based on rough title-desc check): {coherent_count}")
print(f"  Incoherent profiles: {incoherent_count}")
print(f"  Total jobs checked: {total_jobs}")
print(f"  Number of unique job descriptions: {len(all_descriptions)}")

print("\nTop 10 most common job descriptions:")
for desc, count in all_descriptions.most_common(10):
    print("-" * 40)
    print(f"Frequency: {count}")
    print(f"Snippet: {desc[:200]}...")
