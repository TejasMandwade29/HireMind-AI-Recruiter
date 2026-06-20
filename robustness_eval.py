import os
import sys
import numpy as np

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.template_classifier import TemplateClassifier

# Define test cases for evaluation
# Format: list of dicts containing original template ID (1-based), target tier, and perturbations
eval_data = [
    {
        "id": 29,
        "tier": 1,
        "name": "Template 29 (LTR Search)",
        "paraphrase": "Managed the ranking module for a retail search engine, shifting from manual score weighting to a learning-to-rank approach. I set up training and validation loops, feature creation, and click-through labeling. The project succeeded in raising search revenue by 12%, though infra was the main bottleneck.",
        "synonyms": "Controlled the ranking level for an e-commerce search platform, developing it from a manually-tuned scoring algorithm to a learning-to-rank architecture over 9 months. Structured the relevance rating workflow (combination of click-through statistics and direct human reviews), the feature pipeline, and the training/evaluation workflow. Most of the effort was infrastructure and data quality - the modeling portion was nearly the straightforward piece. Final model increased revenue-per-search by 12%.",
        "reordered": "Most of the work was infrastructure and data quality - the modeling part was almost the easy bit. Final model improved revenue-per-search by 12%. Designed the relevance labeling pipeline (mix of click-through data and explicit human judgments), the feature pipeline, and the training/eval workflow. Owned the ranking layer for an e-commerce search product, evolving it from a hand-tuned scoring function to a learning-to-rank model over 9 months.",
        "noisy": "Owned the ranking layer for an e-commerce search product, evolving it from a hand-tuned scoring function to a learning-to-rank model over 9 months. Designed the relevance labeling pipeline (mix of click-through data and explicit human judgments), the feature pipeline, and the training/eval workflow. Most of the work was infrastructure and data quality - the modeling part was almost the easy bit. Final model improved revenue-per-search by 12%!!! Candidate details: email: recruiter-trap@company.com, phone: +91 99999 99999. [Click here for portfolio](http://myportfolio.io)."
    },
    {
        "id": 31,
        "tier": 1,
        "name": "Template 31 (Semantic Search)",
        "paraphrase": "Built a vector-based search system for a 500k-document wiki. Utilized sentence-transformers models alongside FAISS to index and retrieve. Added query expansion to resolve term differences. Achieved a 35% increase in search relevancy compared to our previous Elasticsearch BM25 baseline.",
        "synonyms": "Created a semantic search module for an internal database of ~500K files. Employed sentence-transformers (all-MiniLM-L6-v2 at first, subsequently migrated to bge-base) with FAISS for rapid nearest-neighbor search. Planned the query expansion component that manages language mismatch between user questions and document vocabulary. Reported search-relevance upgrade of 35% over the earlier Elasticsearch BM25 tool, proven by human evaluation.",
        "reordered": "Reported search-relevance improvement of 35% over the prior Elasticsearch BM25 setup, validated through human relevance judgments. Designed the query expansion module that handles vocabulary mismatch between user queries and document terms. Developed a semantic search feature for an internal knowledge base of ~500K documents. Used sentence-transformers (all-MiniLM-L6-v2 initially, later upgraded to bge-base) with FAISS for fast nearest-neighbor retrieval.",
        "noisy": "DEVELOPED A SEMANTIC SEARCH FEATURE FOR AN INTERNAL KNOWLEDGE BASE OF ~500K DOCUMENTS. USED SENTENCE-TRANSFORMERS (ALL-MINILM-L6-V2 INITIALLY, LATER UPGRADED TO BGE-BASE) WITH FAISS FOR FAST NEAREST-NEIGHBOR RETRIEVAL. Designed the query expansion module that handles vocabulary mismatch between user queries and document terms. Reported search-relevance improvement of 35% over the prior Elasticsearch BM25 setup, validated through human relevance judgments. Tags: #python #machinelearning #faiss #elasticsearch #vectorsearch #ai"
    },
    {
        "id": 35,
        "tier": 1,
        "name": "Template 35 (Fine-tuning LLMs)",
        "paraphrase": "I performed LoRA and QLoRA fine-tuning on LLaMA-2-7B and Mistral-7B models to match resumes with job descriptions. Created a dataset of 200,000 feedback pairs and set up an evaluation framework. Served the models using BentoML on Kubernetes with INT8 quantization, achieving <200ms latency and reducing API costs from $0.04 to $0.001.",
        "synonyms": "Optimized LLaMA-2-7B and Mistral-7B models utilizing LoRA and QLoRA parameters for vertical candidate-JD mapping. Created the dataset filtering system that produced 200K high-value preference records from hiring labels, plus the validation suite utilizing both rank metrics and human feedback scores. Deployed the system using BentoML on K8s with sub-200ms p95 response time by quantizing to INT8 and batching requests. Cost per query fell from $0.04 with GPT-3.5 to below $0.001.",
        "reordered": "Cost per inference dropped from $0.04 with GPT-3.5-fallback to under $0.001. Deployed the model via BentoML on Kubernetes with sub-200ms p95 latency by quantizing to INT8 and batching at the request level. Fine-tuned LLaMA-2-7B and Mistral-7B variants using LoRA and QLoRA for domain-specific candidate-JD matching. Built the data curation pipeline that generated 200K high-quality preference pairs from recruiter labels, plus the eval harness using both ranking metrics and human-quality scores.",
        "noisy": "Fine-tuned LLaMA-2-7B and Mistral-7B variants using LoRA and QLoRA for domain-specific candidate-JD matching. Built the data curation pipeline that generated 200K high-quality preference pairs from recruiter labels. Deployed the model via BentoML on Kubernetes with sub-200ms p95 latency. <script>alert('xss')</script> Cost per inference dropped from $0.04 to under $0.001. Resume ID: 94829. References available on request."
    },
    {
        "id": 24,
        "tier": 2,
        "name": "Template 24 (Recommendation System)",
        "paraphrase": "Developed production recommender tools for a growing startup. We utilized matrix factorization collaborative filtering alongside gradient-boosted models to rerank items using user activity metrics. I worked on the modeling side, while platform engineers deployed it.",
        "synonyms": "Created recommendation-type functions at a growth startup - less complex than ranking frameworks at big tech, but production. Utilized a mixture of collaborative filtering (matrix factorization in implicit-feedback library) and gradient-boosted re-ranking over user behavior signals. Solely machine learning portion of the project; production hosting was managed by the infra team.",
        "reordered": "Pure ML side of the work; production deployment was handled by the platform team. Used a combination of collaborative filtering (matrix factorization in implicit-feedback library) and gradient-boosted re-ranking over engagement signals. Built recommendation-style features at a mid-stage startup - lighter weight than ranking systems at FAANG, but production.",
        "noisy": "Built recommendation-style features at a mid-stage startup - lighter weight than ranking systems at FAANG, but production. Used a combination of collaborative filtering and gradient-boosted re-ranking over engagement signals. Email me: info@startup.com. Resume version 3.2. Keywords: RecSys, Collaborative Filtering, Matrix Factorization, XGBoost."
    },
    {
        "id": 25,
        "tier": 2,
        "name": "Template 25 (CV Image Moderation)",
        "paraphrase": "Created image filtering tools by training ResNet neural networks with PyTorch on 200k images. Maintained training scripts, image preprocessing, and inference code. My experience is largely computer vision focused, but I'm looking to pivot to NLP.",
        "synonyms": "Developed computer vision classifiers for our application's picture moderation utility using PyTorch - adapted ResNet models on a annotated dataset of ~200K photos. Structured the training pipeline (data ingestion, augmentation, testing) and the model-serving service. Majority of my task work has been in computer vision; I am currently aiming to pivot to NLP/LLM tasks but my hands-on background there is small.",
        "reordered": "Most of my project work has been in CV; I'm now interested in transitioning toward NLP/LLM work but my professional experience there is limited. Set up the training pipeline (data loading, augmentation, evaluation) and the inference service. Built computer vision models for our product's image moderation feature using PyTorch - fine-tuned ResNet variants on a labeled dataset of ~200K images.",
        "noisy": "Built computer vision models for our product's image moderation feature using PyTorch - fine-tuned ResNet variants on a labeled dataset of ~200K images. Set up the training pipeline (data loading, augmentation, evaluation) and the inference service. <div>Image Moderation Project 2025</div> Most of my project work has been in CV; I'm now interested in transitioning toward NLP/LLM work."
    },
    {
        "id": 26,
        "tier": 2,
        "name": "Template 26 (Time-series Forecasting)",
        "paraphrase": "Developed models for predicting supply chain demands using Prophet, LightGBM, and LSTMs. The LightGBM system was put into production. I also tested reinforcement learning models for pricing and worked with business operations.",
        "synonyms": "Employed on time-series prediction classifiers for logistics supply-chain demand prediction at a shipping enterprise. Created models in Prophet, LightGBM, and (for a single project) a minor LSTM - the LightGBM classifier was finally deployed. Additionally conducted some reinforcement learning tests for automated pricing but those were not shipped. The task was a blend of modeling, analytics, and business communication with the logistics team.",
        "reordered": "Also ran some reinforcement learning experiments for dynamic pricing but those didn't make it to production. The work was a mix of modeling, analysis, and stakeholder communication with the operations team. Worked on time-series forecasting models for supply-chain demand prediction at a logistics company. Built models in Prophet, LightGBM, and (for one project) a small LSTM - the LightGBM model ended up shipping.",
        "noisy": "Worked on time-series forecasting models for supply-chain demand prediction at a logistics company. Built models in Prophet, LightGBM, and (for one project) a small LSTM - the LightGBM model ended up shipping. Also ran some reinforcement learning experiments for dynamic pricing but those didn't make it to production. --- END OF HISTORY --- Note: Stated notice period is negotiable."
    },
    {
        "id": 2,
        "tier": 3, # Tier 3/4 non-AI
        "name": "Template 2 (Customer Support Lead)",
        "paraphrase": "Led a customer service group of 8 representatives for a SaaS tool. We handled ticket triage, customer feedback integration, and escalations. Developed training guides and agent onboarding plans. Strong management background without software engineering skills.",
        "synonyms": "Client assistance team supervisor at a software application. Directed a group of 8 support representatives resolving tier-1 and tier-2 issues; managed the escalation pipeline to developers and the customer-feedback pathway to product management. Created the support wiki and the agent coaching program. Skillful on the leadership aspect and the process flow; weaker on engineering capability beyond tool familiarity.",
        "reordered": "Built out the support knowledge base and the agent training program. Strong on the people-management side and the process side; lighter on technical depth beyond product expertise. Customer support team lead at a SaaS product. Managed a team of 8 support agents handling tier-1 and tier-2 tickets; owned the escalation process to engineering and the customer-feedback loop to product.",
        "noisy": "Customer support team lead at a SaaS product. Managed a team of 8 support agents handling tier-1 and tier-2 tickets. Built out the support knowledge base and the agent training program. Lighter on technical depth beyond product expertise. Contact: support-lead@saas-example.com."
    },
    {
        "id": 11,
        "tier": 3, # Tier 3/4 non-AI
        "name": "Template 11 (DevOps/Cloud)",
        "paraphrase": "DevOps engineer managing AWS resources (VPCs, security groups, subnets) and Kubernetes clusters. Developed Terraform scripts to define infrastructure and set up CI/CD via GitLab and ArgoCD, plus monitoring using Prometheus and Grafana. Very little software development experience.",
        "synonyms": "Cloud systems administration and DevOps tasks at an enterprise software firm. Managed the AWS environment architecture (VPC, IAM, networking), the Terraform scripts for our system deployments, and the Kubernetes orchestration operations. Created the CI/CD pipelines (GitLab CI + ArgoCD) and the observability suite (Prometheus, Grafana, Loki). Skilled on the environment and operations part; have not done significant backend application programming.",
        "reordered": "Designed the CI/CD pipelines (GitLab CI + ArgoCD) and the monitoring stack (Prometheus, Grafana, Loki). Cloud infrastructure and DevOps work at an enterprise SaaS company. Owned the AWS account architecture (VPC, IAM, networking), the Terraform modules for our service deployments, and the Kubernetes cluster operations. Strong on the infra and ops side; haven't done much application development.",
        "noisy": "Cloud infrastructure and DevOps work at an enterprise SaaS company. Owned the AWS account architecture (VPC, IAM, networking), the Terraform modules for our service deployments, and the Kubernetes cluster operations. Designed the CI/CD pipelines (GitLab CI + ArgoCD) and the monitoring stack (Prometheus, Grafana, Loki). Internal employee ID: EMP-10395. Status: Active."
    },
    {
        "id": 15,
        "tier": 3, # Tier 3/4 non-AI
        "name": "Template 15 (Full Stack Web Dev)",
        "paraphrase": "Full stack programmer creating React frontends and Node/Express backends. Managed SQL database tables, API routes, and containerized deployment with Docker and Kubernetes. Competent across the web stack, primarily focused on backend systems.",
        "synonyms": "Full-stack internet application development at a SaaS enterprise. Constructed React-based dashboard views and the Node.js REST API serving them. Active across the stack: UI controls, API route planning, PostgreSQL schemas, hosting using Docker/Kubernetes. Adaptable in majority of a standard web stack although my primary focus is the backend and database framework. Recent education is in automation checks and CI/CD workflows.",
        "reordered": "Comfortable in most parts of a typical web stack though my comfort zone is the backend and database side. Recent learning has been on the testing and CI/CD discipline. Full-stack web application development at a SaaS company. Built React-based admin interfaces and the Node.js REST API backing them. Worked across the stack: frontend components, REST endpoint design, PostgreSQL schema, deployment via Docker/Kubernetes.",
        "noisy": "Full-stack web application development at a SaaS company. Built React-based admin interfaces and the Node.js REST API backing them. Worked across the stack: frontend components, REST endpoint design, PostgreSQL schema. Deployment via Docker/Kubernetes. Profile updated: 2026. Keywords: Javascript, Node.js, Express, React, PostgreSQL."
    }
]

def get_tier_from_id(template_id):
    if template_id is None:
        return 4 # Unclassified / Unrelated
    if template_id in range(28, 46): # T1 is 28 to 45 (1-based)
        return 1
    if template_id in range(22, 28): # T2 is 22 to 27 (1-based)
        return 2
    return 3 # Tier 3/4 (all other template IDs)

def main():
    print("Initializing Template Classifier...")
    classifier = TemplateClassifier()
    # Force load sentence-transformer model
    classifier._load_model()
    
    thresholds = [0.75, 0.80, 0.85, 0.90]
    perturbations = ["paraphrase", "synonyms", "reordered", "noisy"]
    
    # Store results
    # results[threshold][perturbation] = list of (is_correct, is_tier_correct, similarity_score)
    results = {th: {p: [] for p in perturbations} for th in thresholds}
    
    print("\nStarting Robustness Evaluation...")
    print("Target Tiers: T1 (IDs 28-45), T2 (IDs 22-27), T3/4 (Other IDs)")
    
    for case in eval_data:
        target_id = case["id"]
        target_tier = case["tier"]
        name = case["name"]
        
        print(f"\nEvaluating {name} (Target Template ID: {target_id}, Tier: {target_tier})...")
        
        for p in perturbations:
            text = case[p]
            
            # For logging similarities, let's pre-calculate manually first
            desc_embedding = classifier.model.encode(text, show_progress_bar=False)
            similarities = []
            for temp_emb in classifier.template_embeddings:
                norm_a = np.linalg.norm(desc_embedding)
                norm_b = np.linalg.norm(temp_emb)
                if norm_a == 0 or norm_b == 0:
                    sim = 0.0
                else:
                    sim = np.dot(desc_embedding, temp_emb) / (norm_a * norm_b)
                similarities.append(sim)
            
            max_idx = int(np.argmax(similarities))
            max_sim = float(similarities[max_idx])
            matched_id = max_idx + 1
            
            # Print similarity information
            print(f"  [{p}] Max matching template: ID {matched_id} with similarity {max_sim:.4f}")
            
            for th in thresholds:
                # Classify with threshold
                final_id = matched_id if max_sim >= th else None
                final_tier = get_tier_from_id(final_id)
                
                # Check accuracy
                is_correct = (final_id == target_id)
                is_tier_correct = (final_tier == target_tier)
                
                results[th][p].append({
                    "is_correct": is_correct,
                    "is_tier_correct": is_tier_correct,
                    "similarity": max_sim,
                    "matched_id": final_id,
                    "matched_tier": final_tier,
                    "target_id": target_id,
                    "target_tier": target_tier
                })
                
    print("\n================== ROBUSTNESS EVALUATION REPORT ==================")
    
    # 1. Output accuracy table by perturbation type
    print(f"{'Perturbation Type':<20} | {'Thresh 0.75':<12} | {'Thresh 0.80':<12} | {'Thresh 0.85':<12} | {'Thresh 0.90':<12}")
    print("-" * 77)
    
    for p in perturbations:
        accs = []
        for th in thresholds:
            runs = results[th][p]
            tier_correct_count = sum(1 for r in runs if r["is_tier_correct"])
            acc = tier_correct_count / len(runs)
            accs.append(f"{acc*100:6.1f}%")
        print(f"{p.capitalize():<20} | {accs[0]:<12} | {accs[1]:<12} | {accs[2]:<12} | {accs[3]:<12}")
        
    # 2. Overall Tier Accuracy
    print("-" * 77)
    overall_accs = []
    for th in thresholds:
        total_runs = 0
        correct_runs = 0
        for p in perturbations:
            runs = results[th][p]
            total_runs += len(runs)
            correct_runs += sum(1 for r in runs if r["is_tier_correct"])
        overall_acc = correct_runs / total_runs
        overall_accs.append(f"{overall_acc*100:6.1f}%")
    print(f"{'OVERALL TIER ACCURACY':<20} | {overall_accs[0]:<12} | {overall_accs[1]:<12} | {overall_accs[2]:<12} | {overall_accs[3]:<12}")
    
    # 3. Specific Detailed Classification Failures & Stats
    print("\nDetailed Tier Analysis:")
    for th in thresholds:
        print(f"\n--- Analysis for Threshold: {th} ---")
        t1_correct = 0
        t1_total = 0
        t2_correct = 0
        t2_total = 0
        t3_correct = 0 # Non-AI should not be classified as T1/T2
        t3_total = 0
        
        for p in perturbations:
            for r in results[th][p]:
                if r["target_tier"] == 1:
                    t1_total += 1
                    if r["matched_tier"] == 1:
                        t1_correct += 1
                elif r["target_tier"] == 2:
                    t2_total += 1
                    if r["matched_tier"] == 2:
                        t2_correct += 1
                else:
                    t3_total += 1
                    if r["matched_tier"] == 3 or r["matched_id"] is None:
                        t3_correct += 1
                        
        print(f"  Tier 1 Recall: {t1_correct}/{t1_total} ({t1_correct/t1_total*100:.1f}%)")
        print(f"  Tier 2 Recall: {t2_correct}/{t2_total} ({t2_correct/t2_total*100:.1f}%)")
        print(f"  Tier 3/4 Clean Rejection Rate (True Negatives): {t3_correct}/{t3_total} ({t3_correct/t3_total*100:.1f}%)")

if __name__ == "__main__":
    main()
