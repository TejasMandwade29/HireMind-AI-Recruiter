import csv
import json
import logging
import time
from src.config import LOG_FORMAT

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("RedrobRanker")

def load_candidates_generator(file_path: str):
    """
    Yields candidate records sequentially from a JSONL file
    to minimize memory usage (ensures we scale to 100K+ candidates).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            yield json.loads(line)

def load_job_description(file_path: str) -> str:
    """
    Loads and returns the text of the job description.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def save_submission_csv(ranked_results: list[dict], output_path: str):
    """
    Saves the top 100 ranked candidates to a CSV file matching the required spec:
    candidate_id, rank, score, reasoning
    """
    # Columns in exact order: candidate_id, rank, score, reasoning
    headers = ["candidate_id", "rank", "score", "reasoning"]
    
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in ranked_results:
            writer.writerow([
                row["candidate_id"],
                row["rank"],
                f"{row['score']:.4f}",
                row["reasoning"]
            ])

class StageProfiler:
    """
    Utility class for measuring execution latency across ranking stages.
    """
    def __init__(self, name: str):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.info(f"Starting Stage: {self.name}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        logger.info(f"Completed Stage: {self.name} in {duration:.4f} seconds.")
