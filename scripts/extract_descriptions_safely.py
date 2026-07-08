import json
import collections
import sys

# Reconfigure stdout to use utf-8
sys.stdout.reconfigure(encoding='utf-8')

file_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"

all_descs = collections.Counter()

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        c = json.loads(line)
        for job in c.get("career_history", []):
            desc = job.get("description")
            if desc:
                all_descs[desc] += 1

output_path = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\unique_descriptions.txt"

with open(output_path, "w", encoding="utf-8") as out:
    out.write(f"Total unique job descriptions in full dataset: {len(all_descs)}\n\n")
    for idx, (desc, freq) in enumerate(all_descs.most_common()):
        out.write(f"[{idx+1}] Frequency: {freq}\n")
        out.write(f"Text: {desc}\n")
        out.write("-" * 80 + "\n")

print(f"Successfully processed full dataset and saved {len(all_descs)} unique descriptions to unique_descriptions.txt")
