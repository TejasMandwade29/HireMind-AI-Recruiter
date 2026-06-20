import zlib
from src.config import SERVICES_COMPANIES

class ReasoningGenerator:
    def __init__(self):
        # Maps matched template IDs to high-impact achievements for reasoning
        self.achievements = {
            28: "building an e-commerce search learning-to-rank layer",
            29: "training feed discovery ranking models using XGBoost & LightGBM",
            30: "developing semantic search features for large document corpora",
            31: "implementing a RAG-based customer support chatbot",
            32: "deploying content recommendation systems for 10M+ users",
            34: "fine-tuning LLaMA & Mistral models for candidate-JD matching",
            35: "shipping a large-scale recruiter-facing RAG search pipeline",
            36: "building marketplace recommendations using Thompson sampling",
            37: "owning an end-to-end BGE and Pinecone search ranking pipeline",
            38: "rolling out a 35M+ item semantic search system",
            39: "migrating keyword-based search to embedding-based search",
            40: "overhauling a large matching and retrieval layer",
            41: "deploying real-time personalization infrastructure",
            42: "designing a flagship search ranking layer",
            43: "owning a consumer product search and discovery experience",
            44: "scaling contents and relevance engineering pipelines"
        }

    def _get_hash_index(self, candidate_id: str, num_options: int) -> int:
        """
        Generates a deterministic hash of candidate_id to select templates,
        ensuring lexical variety across the ranked list.
        """
        if not candidate_id:
            return 0
        return zlib.adler32(candidate_id.encode("utf-8")) % num_options

    def _get_matched_skills(self, skills: list) -> list[str]:
        """
        Identifies key skills relevant to the Senior AI Engineer role.
        """
        if not skills:
            return []
        
        target_skills = {
            "pinecone": "vector search databases",
            "faiss": "FAISS indexing",
            "milvus": "vector databases",
            "qdrant": "Qdrant vector stores",
            "embeddings": "dense embeddings",
            "sentence-transformers": "sentence-transformers",
            "nlp": "natural language processing",
            "pytorch": "PyTorch deep learning",
            "xgboost": "XGBoost learning-to-rank",
            "lightgbm": "LightGBM ranking",
            "rag": "RAG architecture",
            "llama": "LLM fine-tuning",
            "mistral": "Mistral models"
        }
        
        found = []
        for sk in skills:
            sk_name = sk.get("name", "").lower()
            for key, desc in target_skills.items():
                if key in sk_name and desc not in found:
                    found.append(desc)
        return found

    def generate_reasoning(self, candidate_record: dict, matched_ids: list, score_breakdown: dict) -> str:
        """
        Compiles candidate facts and dynamically assembles a recruiter-like rationale.
        """
        candidate_id = candidate_record.get("candidate_id", "CAND_0000000")
        profile = candidate_record.get("profile", {})
        signals = candidate_record.get("redrob_signals", {})
        skills = candidate_record.get("skills", [])
        
        name = profile.get("anonymized_name", "Candidate")
        yoe = profile.get("years_of_experience", 0.0)
        title = profile.get("current_title", "Engineer")
        company = profile.get("current_company", "a tech startup")
        
        # 1. Determine Core Achievement from matched templates
        achievement = "shipping production machine learning systems"
        if matched_ids:
            # Find the highest matched template ID
            max_tid = max(matched_ids)
            if max_tid in self.achievements:
                achievement = self.achievements[max_tid]
            elif max_tid in range(22, 28):
                achievement = "building predictive models and time-series pipelines"
                
        # 2. Extract matching skills
        key_skills = self._get_matched_skills(skills)
        skills_str = ", ".join(key_skills[:2]) if key_skills else "applied ML"
        
        # 3. Availability and notice
        notice = signals.get("notice_period_days", 60)
        
        # 4. Location and Relocation
        loc = profile.get("location", "India")
        willing = signals.get("willing_to_relocate", False)
        loc_str = f"based in {loc}"
        if willing and loc.lower() not in ["pune", "noida", "delhi", "gurgaon", "delhi ncr"]:
            loc_str += " (open to relocation)"

        # 5. Check consulting company status
        is_services = False
        comp_lower = company.lower()
        for svc in SERVICES_COMPANIES:
            if svc in comp_lower:
                is_services = True
                break

        # Check relevance tiers to select appropriate tone/templates
        is_tier_1 = any(tid in range(28, 45) for tid in matched_ids)
        is_tier_2 = any(tid in range(22, 28) for tid in matched_ids)
        
        # Define sentences based on pattern
        
        # Line 1: Strongest technical signal
        if key_skills:
            line1 = f"Strong {skills_str} experience built across {yoe:.1f} years in ML-focused engineering roles."
        else:
            line1 = f"Technical background built across {yoe:.1f} years in software engineering roles, primarily involving {achievement}."
            
        # Line 2: Career trajectory or progression
        prog_score = score_breakdown.get("progression_score", 0)
        if prog_score > 0.7:
            line2 = "Demonstrates a clear progression from early engineering environments into production AI systems with evidence of increasing responsibility and ownership."
        elif prog_score > 0.4:
            line2 = "Shows consistent career stability with relevant experience executing complex technical projects."
        else:
            line2 = "Career history indicates a mix of adjacent roles with some recent exposure to modern AI engineering patterns."
            
        # Add consulting context to Line 2 if applicable
        if is_services:
            line2 = line2.replace("early engineering environments", "enterprise consulting environments")
            
        # Line 3: Availability/location/recruiter recommendation
        beh_score = score_breakdown.get("behavioral_score", 0)
        intent_desc = "strong intent signals" if beh_score > 0.6 else "moderate intent signals"
        if is_tier_1:
            rec = "highly recommended for recruiter review"
        elif is_tier_2:
            rec = "recommended for technical screening"
        else:
            rec = "worth keeping on file for future roles"
            
        line3 = f"Based in {loc} with {intent_desc} and a {notice}-day notice period; {rec}."
        
        # Combine into a single natural paragraph
        reasoning = f"{line1} {line2} {line3}"
        return reasoning
