import json
import os
import pickle
import sys
from sentence_transformers import SentenceTransformer

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"c:\Users\Dell\Downloads\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"
unique_desc_file = os.path.join(base_dir, "unique_descriptions.txt")
model_path = os.path.join(base_dir, "models", "all-MiniLM-L6-v2")
out_embeddings_file = os.path.join(base_dir, "models", "template_embeddings.pkl")
out_texts_file = os.path.join(base_dir, "models", "template_texts.json")

print("Parsing unique_descriptions.txt...")

templates = []
with open(unique_desc_file, "r", encoding="utf-8") as f:
    content = f.read()

parts = content.split("--------------------------------------------------------------------------------")
for part in parts:
    lines = part.strip().split("\n")
    text = ""
    for line in lines:
        if line.startswith("Text: "):
            text = line[6:].strip()
            break
    if text:
        templates.append(text)

print(f"Extracted {len(templates)} template descriptions.")

# Load model locally
print(f"Loading local model from '{model_path}'...")
model = SentenceTransformer(model_path, device="cpu")

# Encode templates
print("Encoding templates...")
embeddings = model.encode(templates, show_progress_bar=True)

# Save template texts to json
with open(out_texts_file, "w", encoding="utf-8") as out:
    json.dump(templates, out, indent=2, ensure_ascii=False)

# Save embeddings using pickle
with open(out_embeddings_file, "wb") as f:
    pickle.dump(embeddings, f)

print(f"Precomputation complete!")
print(f"Saved template texts to: {out_texts_file}")
print(f"Saved template embeddings to: {out_embeddings_file}")
