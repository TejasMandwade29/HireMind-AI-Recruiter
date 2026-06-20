import json

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

found_count = 0
examples = []

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        cid = c.get("candidate_id")
        history = c.get("career_history", [])
        for job in history:
            desc = job.get("description", "")
            comp = job.get("company", "")
            if "founded" in desc.lower():
                found_count += 1
                examples.append((cid, comp, desc))
                if len(examples) > 100:
                    break
        if len(examples) > 100:
            break

print(f"Total jobs with 'founded' in description in first part: {found_count}")
for cid, comp, desc in examples[:5]:
    print(f"\nCandidate: {cid}, Company: {comp}")
    print(f"Description: {desc}")
