import os
from sentence_transformers import SentenceTransformer

model_name = "all-MiniLM-L6-v2"
target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "all-MiniLM-L6-v2")

print(f"Downloading model '{model_name}' and saving to '{target_dir}'...")

# Force CPU loading to be safe
model = SentenceTransformer(model_name, device="cpu")

# Save model locally
model.save(target_dir)

print(f"Model successfully saved offline to: {target_dir}")
