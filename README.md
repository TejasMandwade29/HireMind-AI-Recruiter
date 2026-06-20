# HireMind — Local, Secure, and Explainable Talent Matching at Scale

HireMind is a lightweight, fully offline, and explainable candidate discovery and ranking system. Designed to run on consumer hardware under strict hackathon limits, HireMind processes **100,000 raw candidate resumes in under 70 seconds on CPU**, filters fraudulent "honeypot" profiles, calculates multidimensional relevance scores, and generates transparent, natural-language rationales for recruiters.

---

## 1. Problem Statement
Modern recruiting tools suffer from three critical flaws:
1. **Keyword Gaming:** Candidates easily game legacy Applicant Tracking Systems (ATS) by stuffing resumes with keywords.
2. **Data Leakage & Costs:** Standard AI tools rely on hosted APIs (OpenAI, Anthropic), leaking sensitive candidate CV data and incurring high scale costs.
3. **Data Pollution & Fraud:** Recruiter pools contain spam profiles and "honeypot" accounts with impossible, inconsistent experience or fake qualifications.

HireMind is built to solve these problems by validating data integrity programmatically and scoring semantic relevance locally on CPU, ensuring zero external APIs and zero data leakage.

---

## 2. Key Features
* **Programmatic Anomaly & Honeypot Filtering:** Automatically identifies and strips out fraudulent or inconsistent CVs (e.g. salary min > max, jobs exceeding total YOE, impossible founding dates).
* **Local Semantic Matching:** Computes dense vector similarity between the job description and candidate profiles using a local sentence-transformer model.
* **5-Signal Scoring Engine:** Balances structural fit, semantic skill similarity, candidate intent, career progression, and tenure stability.
* **Deterministic Explainable verdicts:** Generates 100% hallucination-free, fact-based textual rationales for every shortlisted candidate in plain English.
* **Recruiter Review Dashboard:** Provides a Streamlit UI for recruiters to input JDs, execute candidate discovery, and visually inspect candidate score breakdowns.

---

## 3. Technology Stack
* **Language:** Python 3.8+
* **Data Manipulation:** NumPy, Pandas
* **Model Engine:** Sentence Transformers (`all-MiniLM-L6-v2` - 120MB, 384 dimensions)
* **Presentation Layer:** Streamlit (UI Dashboard)
* **Slide Generation:** python-pptx (Developer scripts)

---

## 4. System Architecture

HireMind uses a decoupled, three-layer modular architecture optimized for local efficiency:

```
                  +-----------------------------------+
                  |        PRESENTATION LAYER         |
                  |     (Local Streamlit Dashboard)   |
                  +-----------------+-----------------+
                                    |
                       Ranked JSON  |  JD Text / Query
                         Results    |  Parameters
                                    v
                  +-----------------+-----------------+
                  |        INTELLIGENCE LAYER         |
                  |     - program filters (filters.py)|
                  |     - template classifier         |
                  |     - semantic matcher (MiniLM)   |
                  |     - multi-signal scorer         |
                  |     - deterministic rationales    |
                  +-----------------+-----------------+
                                    |
                      Pre-computed  |  Raw Profiles
                       Embeddings   |  (candidates.jsonl)
                                    v
                  +-----------------+-----------------+
                  |            DATA LAYER             |
                  |     (JSONL Store & NumPy Cache)   |
                  +-----------------------------------+
```

* **Data Layer:** Pre-computed offline sentence embeddings for candidate profiles are cached alongside the raw candidate profile store, eliminating embedding computation bottlenecks.
* **Intelligence Layer:** Conducts rule-based validation filtering, maps profiles against 44 role templates, scores skills, and generates explanations.
* **Presentation Layer:** Exposes search controls, filters, and tabular outputs to the recruiter.

---

## 5. Candidate Evaluation Methodology (5-Signal Score)
Candidates are scored out of 1.0 (before penalty multipliers) using five weights:
1. **Template Fit (25%):** Matches the candidate's career trajectory to 44 structured role archetypes.
2. **Semantic Skill Similarity (25%):** Measures cosine similarity between the resume text and target JD text.
3. **Candidate Intent (20%):** Weights response rate, response time, and activity signals.
4. **Career Progression / Growth (15%):** Evaluates increases in title tiers, tenure, and company sizes.
5. **Tenure Stability (15%):** Rewards long average job tenures and penalizes job-hopping (<18 months average tenure).

### Gate Multipliers
A candidate's base score is multiplied by three gates:
$$\text{Final Score} = \text{Weighted Base} \times \text{YOE Fit (Gaussian)} \times \text{Notice Period Score} \times \text{Services Penalty}$$
* **YOE Fit:** Gaussian curve centered around 7.0 years ($\sigma = 1.5$). Candidates with too little or too much experience are penalised.
* **Notice Period:** Sub-30-day notice receives a $1.0$ multiplier, scaling down to $0.0$ for 150+ days notice.
* **Services Penalty:** A moderate penalty ($0.75$ multiplier) is applied if the candidate's *entire* career has been spent in consulting/IT services companies to prioritize product-focused experience.

---

## 6. Explainability & Validation Logic
To guarantee **0% hallucinations**, HireMind does not use generative LLMs for reasoning. Instead, the `ReasoningGenerator` extracts verified facts (experience, matched roles, notice period, location) and outputs them using a deterministic, rule-based text formatter.

### Data Integrity Rules (Honeypot Filters)
Profiles containing any of the following inconsistencies are filtered before scoring:
1. **Duration Over YoE:** A single job duration exceeds the candidate's declared total Years of Experience (YoE) + 1 month.
2. **Expert Zero Duration:** Candidate claims "expert" proficiency in a skill but has 0 months of experience with it.
3. **Founded Year Anomaly:** A candidate claims to have started a job at a company before that company was founded.
4. **Salary Range Anomaly:** Expected salary minimum is greater than the maximum.

---

## 7. Challenge Compliance
* **100% Offline:** No cloud connections or network requests. Zero data leakage.
* **CPU Only:** Embeddings are mapped using NumPy matrix operations on CPU, running well within memory limits.
* **High Speed:** Processes all 100k records in **68.2 seconds** locally.

---

## 8. Project Structure
```
HireMind/
├── src/                         # Production Source Code
│   ├── career_progression.py    # Career trajectory scorer
│   ├── config.py                # Configuration constants
│   ├── dashboard.py             # Streamlit application
│   ├── filters.py               # Honeypot detection
│   ├── reasoning_generator.py   # Rationale compiler
│   ├── scoring_engine.py        # 5-Signal mathematical logic
│   ├── semantic_matching.py     # Local vector matching
│   ├── template_classifier.py   # Role archetype mapper
│   └── utils.py                 # File I/O helpers
├── models/                      # Offline models and pre-computed files
│   ├── all-MiniLM-L6-v2/        # Local transformer weights
│   ├── template_embeddings.pkl
│   └── template_texts.json
├── scripts/                     # Developer utility scripts
│   ├── create_slides_v3.py      # Programmatic slide builder
│   └── precompute_templates.py  # Embedding cache builder
├── tests/                       # Test suites & evaluation
│   ├── test_career_progression.py
│   ├── test_filters.py
│   ├── test_reasoning_generator.py
│   ├── test_scoring_engine.py
│   ├── test_semantic_matching.py
│   ├── test_template_classifier.py
│   ├── robustness_eval.py       # Performance evaluator
│   └── validate_submission.py   # Output CSV validator
├── docs/                        # Specifications and visual assets
│   ├── reference/               # Organizer guides
│   ├── assets/                  # Crops
│   └── ppt_assets/              # Rebuild assets
├── .gitignore                   # Git exclusions
├── README.md                    # Setup documentation
├── requirements.txt             # Dependency manifest
├── submission_metadata.yaml     # Portal upload parameters
├── job_description.txt          # Target Job Description file
├── unique_descriptions.txt       # Template reference database
└── hiremind_presentation.pptx   # Final pitch deck
```

---

## 9. Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/USERNAME/HireMind.git
   cd HireMind
   ```

2. **Set Up a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Dataset Placement:**
   Ensure `candidates.jsonl` is placed in the root directory (this file is excluded from commits via `.gitignore`).

---

## 10. Execution Guide

### Running the Ranking Pipeline
To process the 100k candidate pool and output the top 100 shortlisted candidate CSV:
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

### Launching the Dashboard UI
To view candidate profiles, scores, and rationales interactively:
```bash
streamlit run src/dashboard.py
```

### Running Validation & Test Suites
To run the automated format checks on the output CSV:
```bash
python tests/validate_submission.py --csv ./submission.csv
```
To run the unit test suite:
```bash
pytest tests/
```

---

## 11. Screenshots

### Candidate Score Breakdown Visualizer
Visual crop showing candidate signal distributions:
![Score Visualizer](/docs/assets/score_visualizer.png)

### Recruiter Verdict & Fact-Based Explanation
Visual crop showing factual reasoning card output:
![Recruiter Verdict](/docs/assets/recruiter_verdict.png)

---

## 12. Future Scope
* **Vector Index Integration:** Implement a lightweight local vector library (e.g. FAISS or hnswlib) to enable sub-second candidate matching at million-scale.
* **SQL/NoSQL Migration:** Move from flat JSONL profile parsing to indexed local database tables for optimized I/O pipelines.
* **Shortlist Refinement LLM:** Incorporate a small, quantized local LLM (e.g. Llama-3-8B-Instruct via llama.cpp) to run on the Top 100 shortlisted candidates only, generating deep conversational reasoning notes without violating execution time limits.
