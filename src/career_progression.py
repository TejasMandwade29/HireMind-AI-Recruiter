class CareerProgressionScorer:
    def __init__(self):
        # Company size weights for measuring company scale changes
        self.scale_weights = {
            "1-10": 1,
            "11-50": 2,
            "51-200": 3,
            "201-500": 4,
            "501-1000": 5,
            "1001-5000": 6,
            "5001-10000": 7,
            "10001+": 8
        }

    def _get_title_level(self, title: str) -> int:
        """
        Classifies a job title into a numeric level:
        1: Junior / Associate / Intern / Assistant
        2: Mid-level developer / Engineer
        3: Senior / Lead / Principal / Staff / Director / Manager
        """
        if not title:
            return 2
        t_lower = title.lower()
        if any(w in t_lower for w in ["junior", "jr", "intern", "associate", "assistant", "trainee"]):
            return 1
        elif any(w in t_lower for w in ["senior", "sr", "lead", "principal", "staff", "manager", "head", "director", "founding", "chief"]):
            return 3
        return 2

    def calculate_progression_score(self, career_history: list) -> float:
        """
        Computes role level progression score between 0.0 and 1.0.
        If candidate progressed to higher levels, score is > 0.5.
        """
        if not career_history:
            return 0.5
            
        # Sort history chronologically
        sorted_jobs = sorted(career_history, key=lambda x: x.get("start_date", ""))
        
        levels = [self._get_title_level(j.get("title", "")) for j in sorted_jobs]
        
        if len(levels) < 2:
            # Single job: check if it's already a senior level
            if levels[0] == 3:
                return 0.8  # Started at senior level
            elif levels[0] == 2:
                return 0.5  # Neutral mid-level
            return 0.3      # Junior level
            
        # Calculate start vs. end delta
        delta = levels[-1] - levels[0]  # range [-2, 2]
        base_prog = delta / 2.0         # range [-1.0, 1.0]
        score = 0.5 + 0.5 * base_prog   # range [0.0, 1.0]
        
        # Add a small bonus for non-decreasing progression
        is_monotonic = all(levels[i] >= levels[i-1] for i in range(1, len(levels)))
        if is_monotonic and delta > 0:
            score = min(score + 0.1, 1.0)
            
        return float(score)

    def calculate_growth_velocity(self, career_history: list, total_yoe: float) -> float:
        """
        Calculates company size growth velocity and promotion speed.
        Returns a score between 0.0 and 1.0.
        """
        if not career_history:
            return 0.5
            
        sorted_jobs = sorted(career_history, key=lambda x: x.get("start_date", ""))
        
        # 1. Company Size Transition Score
        company_sizes = [j.get("company_size", "11-50") for j in sorted_jobs]
        scale_scores = [self.scale_weights.get(sz, 2) for sz in company_sizes]
        
        if len(scale_scores) >= 2:
            scale_delta = scale_scores[-1] - scale_scores[0] # range [-7, 7]
            scale_prog = scale_delta / 7.0                   # range [-1.0, 1.0]
            scale_score = 0.5 + 0.5 * scale_prog             # range [0.0, 1.0]
        else:
            scale_score = 0.5
            
        # 2. Promotion Speed (average years spent to reach Level 3)
        levels = [self._get_title_level(j.get("title", "")) for j in sorted_jobs]
        
        promo_score = 0.5
        if 3 in levels:
            first_sr_idx = levels.index(3)
            if first_sr_idx > 0 and total_yoe and total_yoe > 0:
                # Approximate years to first senior role
                # Sum duration of jobs before the first senior role
                months_before_sr = sum(sorted_jobs[idx].get("duration_months", 0) for idx in range(first_sr_idx))
                years_to_sr = months_before_sr / 12.0
                
                if years_to_sr <= 3.0:
                    promo_score = 0.9  # Very fast growth
                elif years_to_sr <= 5.0:
                    promo_score = 0.7  # Good standard growth
                else:
                    promo_score = 0.4  # Slower growth
            elif first_sr_idx == 0:
                # Started career directly in a senior/staff role
                promo_score = 0.8
                
        # Combine company size growth and promotion speed
        return float(0.5 * scale_score + 0.5 * promo_score)

    def get_combined_progression_score(self, career_history: list, total_yoe: float) -> float:
        """
        Returns a single unified progression score.
        """
        prog = self.calculate_progression_score(career_history)
        velocity = self.calculate_growth_velocity(career_history, total_yoe)
        
        return float(0.6 * prog + 0.4 * velocity)
