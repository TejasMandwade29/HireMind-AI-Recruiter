import os

# Central configuration for thresholds, weights, paths, and constants.

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "all-MiniLM-L6-v2")
UNIQUE_DESCS_PATH = os.path.join(BASE_DIR, "unique_descriptions.txt")
CANDIDATES_PATH = os.path.join(BASE_DIR, "candidates.jsonl")

# --- SCORING ENGINE WEIGHTS ---
# Balance weights: Template + Semantic + Behavioral + Career Progression + Stability = 1.0
WEIGHT_TEMPLATE = 0.25
WEIGHT_SEMANTIC = 0.25
WEIGHT_BEHAVIORAL = 0.20
WEIGHT_PROGRESSION = 0.15
WEIGHT_STABILITY = 0.15

# --- YOE (YEARS OF EXPERIENCE) FIT CONSTANTS ---
YOE_TARGET_MEAN = 7.0
YOE_TARGET_SIGMA = 1.5

# --- SERVICES COMPANY LIST ---
SERVICES_COMPANIES = {
    "tcs", 
    "tata consultancy services", 
    "infosys", 
    "wipro", 
    "accenture", 
    "cognizant", 
    "capgemini",
    "wipro limited",
    "infosys limited"
}
SERVICES_PENALTY_MULTIPLIER = 0.75  # Moderate penalty, not a hard rejection

# --- NOTICE PERIOD SCORE MAPPING ---
# Stated notice period days mapping to scores
NOTICE_PERIOD_MAPPING = {
    0: 1.0,
    15: 1.0,
    30: 1.0,
    45: 0.8,
    60: 0.6,
    90: 0.3,
    120: 0.1,
    150: 0.0,
    180: 0.0
}
DEFAULT_NOTICE_PERIOD_SCORE = 0.2

# --- BEHAVIORAL SIGNAL WEIGHTS ---
WEIGHT_SIG_RESPONSE_RATE = 0.40
WEIGHT_SIG_RESPONSE_TIME = 0.30
WEIGHT_SIG_OPEN_TO_WORK = 0.15
WEIGHT_SIG_COMPLETENESS = 0.15

# --- TEMPLATE SIMILARITY THRESHOLDS ---
TEMPLATE_EXACT_MATCH_COHERENCE = True
TEMPLATE_SEMANTIC_SIM_THRESHOLD = 0.75

# --- RUNTIME LOGGING SETTINGS ---
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
