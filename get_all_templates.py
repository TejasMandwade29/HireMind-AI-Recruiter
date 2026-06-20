import json
import collections

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

all_descs = collections.Counter()
limit = 10000 # check first 10k candidates
count = 0

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        count += 1
        for job in c.get("career_history", []):
            desc = job.get("description")
            if desc:
                all_descs[desc] += 1
        if count >= limit:
            break

print(f"Parsed {count} candidates.")
print(f"Total unique job descriptions found: {len(all_descs)}")
print("\n--- ALL UNIQUE JOB DESCRIPTIONS ---")
for idx, (desc, freq) in enumerate(all_descs.most_common()):
    print(f"\n[{idx+1}] Frequency: {freq}")
    print(f"Text: {desc}")
