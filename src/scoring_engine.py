import math
from datetime import datetime
from src.config import (
    WEIGHT_TEMPLATE,
    WEIGHT_SEMANTIC,
    WEIGHT_BEHAVIORAL,
    WEIGHT_PROGRESSION,
    WEIGHT_STABILITY,
    YOE_TARGET_MEAN,
    YOE_TARGET_SIGMA,
    SERVICES_COMPANIES,
    SERVICES_PENALTY_MULTIPLIER,
    NOTICE_PERIOD_MAPPING,
    DEFAULT_NOTICE_PERIOD_SCORE,
    WEIGHT_SIG_RESPONSE_RATE,
    WEIGHT_SIG_RESPONSE_TIME,
    WEIGHT_SIG_OPEN_TO_WORK,
    WEIGHT_SIG_COMPLETENESS
)
from src.career_progression import CareerProgressionScorer

class ScoringEngine:
    def __init__(self):
        self.progression_scorer = CareerProgressionScorer()

    def calculate_yoe_fit(self, yoe: float) -> float:
        """
        Gaussian bell curve centered around YOE_TARGET_MEAN (7.0 years) with
        standard deviation YOE_TARGET_SIGMA (1.5 years).
        """
        if yoe is None or yoe < 0:
            return 0.0
        exponent = -((yoe - YOE_TARGET_MEAN) ** 2) / (2 * (YOE_TARGET_SIGMA ** 2))
        return float(math.exp(exponent))

    def calculate_stability_score(self, career_history: list) -> float:
        """
        Measures stability based on the average tenure (duration in months) per job.
        Penalizes job hopping (< 18 months average tenure).
        """
        if not career_history:
            return 0.5
            
        durations = [j.get("duration_months", 0) for j in career_history if j.get("duration_months") is not None]
        if not durations:
            return 0.5
            
        mean_dur = sum(durations) / len(durations)
        
        # Stability grading
        if mean_dur >= 36.0:
            return 1.0
        elif mean_dur >= 24.0:
            return 0.8
        elif mean_dur >= 18.0:
            return 0.5
        elif mean_dur >= 12.0:
            return 0.3
        return 0.1

    def get_services_penalty(self, career_history: list, current_company: str) -> float:
        """
        Applies a moderate penalty multiplier (0.75) if the candidate's ENTIRE
        career has been spent at consulting/IT services companies.
        """
        if not career_history and not current_company:
            return 1.0
            
        companies = set()
        if current_company:
            companies.add(current_company.lower().strip())
        for job in career_history:
            comp = job.get("company")
            if comp:
                companies.add(comp.lower().strip())
                
        if not companies:
            return 1.0
            
        # Check if all known companies are in the services list
        all_services = True
        for comp in companies:
            is_service = False
            for svc in SERVICES_COMPANIES:
                if svc in comp:
                    is_service = True
                    break
            if not is_service:
                all_services = False
                break
                
        return SERVICES_PENALTY_MULTIPLIER if all_services else 1.0

    def get_notice_score(self, notice_days: int) -> float:
        """
        Maps the candidate's notice period to a score between 0.0 and 1.0.
        Sub-30-day notice gets 1.0; 90+ days gets lower.
        """
        if notice_days is None:
            return DEFAULT_NOTICE_PERIOD_SCORE
            
        # Find closest match or direct map
        if notice_days in NOTICE_PERIOD_MAPPING:
            return NOTICE_PERIOD_MAPPING[notice_days]
            
        # Fallback linear interpolation
        if notice_days <= 30:
            return 1.0
        elif notice_days <= 60:
            return 0.6
        elif notice_days <= 90:
            return 0.3
        elif notice_days <= 120:
            return 0.1
        return 0.0

    def calculate_behavioral_score(self, signals: dict) -> float:
        """
        Weights multiple engagement, availability, and response rate signals.
        """
        if not signals:
            return 0.5
            
        # 1. Recruiter Response Rate
        resp_rate = signals.get("recruiter_response_rate", 0.0)
        
        # 2. Average Response Time Score (lower is better, log scaled)
        resp_time = signals.get("avg_response_time_hours", 168.0) # default 1 week if missing
        if resp_time <= 4.0:
            time_score = 1.0
        elif resp_time <= 24.0:
            time_score = 0.8
        elif resp_time <= 72.0:
            time_score = 0.5
        elif resp_time <= 168.0:
            time_score = 0.2
        else:
            time_score = 0.0
            
        # 3. Last Active Date Score
        last_active = signals.get("last_active_date")
        active_score = 0.1
        if last_active:
            try:
                # Target date: 2026-06-18
                dt = datetime.strptime(last_active, "%Y-%m-%d")
                days_diff = (datetime(2026, 6, 18) - dt).days
                if days_diff <= 30:
                    active_score = 1.0
                elif days_diff <= 90:
                    active_score = 0.7
                elif days_diff <= 180:
                    active_score = 0.4
            except:
                pass
                
        # 4. Stated Intent & Open to work
        open_to_work = 1.0 if signals.get("open_to_work_flag") else 0.0
        completeness = (signals.get("profile_completeness_score", 0.0)) / 100.0
        
        # Combine intent signals
        intent_score = 0.5 * open_to_work + 0.5 * completeness
        
        # Weighted sum of components
        score = (
            WEIGHT_SIG_RESPONSE_RATE * resp_rate +
            WEIGHT_SIG_RESPONSE_TIME * time_score +
            WEIGHT_SIG_OPEN_TO_WORK * intent_score +
            WEIGHT_SIG_COMPLETENESS * active_score
        )
        return float(score)

    def calculate_template_score(self, matched_ids: list) -> float:
        """
        Scores candidate based on matching templates in career history.
        """
        if not matched_ids:
            return 0.0
            
        tier_1_ids = set(range(28, 45))
        tier_2_ids = set(range(22, 28))
        
        has_t1 = any(tid in tier_1_ids for tid in matched_ids)
        has_t2 = any(tid in tier_2_ids for tid in matched_ids)
        
        if has_t1:
            return 1.0
        elif has_t2:
            return 0.5
        return 0.0

    def score_candidate(self, candidate_record: dict, matched_ids: list, semantic_sim: float) -> dict:
        """
        Combines all signals, applies modifiers, and returns the final score 
        along with a detailed feature breakdown.
        """
        profile = candidate_record.get("profile", {})
        history = candidate_record.get("career_history", [])
        signals = candidate_record.get("redrob_signals", {})
        
        yoe = profile.get("years_of_experience", 0.0)
        current_company = profile.get("current_company", "")
        notice_days = signals.get("notice_period_days")
        
        # 1. Base Signal Scores
        t_score = self.calculate_template_score(matched_ids)
        s_score = semantic_sim
        b_score = self.calculate_behavioral_score(signals)
        p_score = self.progression_scorer.get_combined_progression_score(history, yoe)
        st_score = self.calculate_stability_score(history)
        
        # 2. Balanced Base Scoring Sum
        weighted_base = (
            WEIGHT_TEMPLATE * t_score +
            WEIGHT_SEMANTIC * s_score +
            WEIGHT_BEHAVIORAL * b_score +
            WEIGHT_PROGRESSION * p_score +
            WEIGHT_STABILITY * st_score
        )
        
        # 3. Apply Multipliers (Gaussian YOE, Notice Period, Services Penalty)
        yoe_fit = self.calculate_yoe_fit(yoe)
        notice_mult = self.get_notice_score(notice_days)
        services_mult = self.get_services_penalty(history, current_company)
        
        final_score = weighted_base * yoe_fit * notice_mult * services_mult
        
        return {
            "candidate_id": candidate_record.get("candidate_id"),
            "template_score": float(t_score),
            "semantic_score": float(s_score),
            "behavioral_score": float(b_score),
            "progression_score": float(p_score),
            "stability_score": float(st_score),
            "final_score": float(final_score)
        }
