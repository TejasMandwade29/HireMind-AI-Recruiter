def has_salary_anomaly(expected_salary: dict) -> bool:
    """
    Checks if a candidate profile has a salary anomaly:
    where min expected salary is strictly greater than max expected salary.
    """
    if not expected_salary:
        return False
    s_min = expected_salary.get("min")
    s_max = expected_salary.get("max")
    if s_min is not None and s_max is not None:
        return s_min > s_max
    return False


def has_duration_anomaly(career_history: list, total_yoe: float) -> bool:
    """
    Checks if a candidate has a career history duration anomaly:
    where the duration of a single job exceeds their total stated years of experience.
    """
    if not career_history or total_yoe is None:
        return False
    yoe_months = total_yoe * 12
    # Tolerance of 1 month for rounding issues
    for job in career_history:
        dur = job.get("duration_months")
        if dur is not None and dur > yoe_months + 1.0:
            return True
    return False


def has_skill_anomaly(skills: list) -> bool:
    """
    Checks if a candidate has a skill anomaly:
    where they claim "expert" proficiency in a skill but have 0 months of usage.
    """
    if not skills:
        return False
    for skill in skills:
        prof = skill.get("proficiency")
        dur = skill.get("duration_months")
        if prof == "expert" and dur == 0:
            return True
    return False


def is_clean_candidate(profile_record: dict) -> bool:
    """
    Combines salary, duration, and skill checks to verify if a candidate is clean
    and free from any honeypot or synthetic anomalies.
    """
    if not profile_record:
        return False
        
    profile = profile_record.get("profile", {})
    history = profile_record.get("career_history", [])
    skills = profile_record.get("skills", [])
    signals = profile_record.get("redrob_signals", {})
    
    yoe = profile.get("years_of_experience", 0.0)
    salary = signals.get("expected_salary_range_inr_lpa", {})
    
    if has_salary_anomaly(salary):
        return False
    if has_duration_anomaly(history, yoe):
        return False
    if has_skill_anomaly(skills):
        return False
        
    return True
