import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

# Set path to include workspace
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    CANDIDATES_PATH,
    SERVICES_COMPANIES,
    SERVICES_PENALTY_MULTIPLIER
)
from src.utils import (
    load_candidates_generator,
    load_job_description,
    logger
)
from src.filters import is_clean_candidate
from src.template_classifier import TemplateClassifier
from src.semantic_matching import SemanticMatcher
from src.scoring_engine import ScoringEngine
from src.reasoning_generator import ReasoningGenerator

# Set page configuration with layout and theme
st.set_page_config(
    page_title="HireMind",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark-mode aesthetic, glassmorphism, and transitions
st.markdown(
    """
    <style>
    /* Global Theme */
    .stApp {
        background-color: #0F172A !important;
    }

    /* Remove Streamlit top colored decoration bar */
    header[data-testid="stHeader"] {visibility: hidden;}
    div[data-testid="stDecoration"] {visibility: hidden; height: 0; display: none;}
    
    /* Hide the footer and main menu */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* SelectBox Customization (Remove red borders) */
    div[data-baseweb="select"] > div {
        background-color: rgba(18, 22, 32, 0.8) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(0, 242, 254, 0.5) !important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #00f2fe !important;
        box-shadow: 0 0 0 1px #00f2fe !important;
    }
    
    /* Tabs Customization (Remove red underline, add cyan) */
    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00f2fe !important;
        border-bottom-color: #00f2fe !important;
        background: rgba(0,242,254,0.05) !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #00f2fe !important;
    }
    
    /* Brand Title */
    .brand-title {
        color: #00f2fe;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3.2rem;
        margin-bottom: 0.2rem;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
    }
    
    /* Subtle subtitle */
    .subtitle-text {
        color: #94A3B8;
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(25, 30, 41, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 242, 254, 0.3);
    }
    .metric-title {
        color: #8a99ad;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hero Metric Card */
    .hero-metric-card {
        background: linear-gradient(135deg, rgba(0,242,254,0.1) 0%, rgba(79,172,254,0.05) 100%);
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 242, 254, 0.15);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-metric-title {
        color: #00f2fe;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .hero-metric-value {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 800;
        font-family: 'Outfit', sans-serif;
        text-shadow: 0 2px 10px rgba(0,242,254,0.3);
    }

    /* Candidate detail card */
    .detail-card {
        background: rgba(18, 22, 32, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-top: 0.5rem;
    }
    .candidate-name {
        color: #00f2fe;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Funnel Components */
    .funnel-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 2rem;
        margin-bottom: 1rem;
        background: rgba(18, 22, 32, 0.5);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .funnel-step {
        text-align: center;
        flex: 1;
    }
    .funnel-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
    }
    .funnel-label {
        font-size: 0.85rem;
        color: #8a99ad;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.4rem;
        font-weight: 600;
    }
    .funnel-arrow {
        color: #00f2fe;
        font-size: 1.5rem;
        margin: 0 0.5rem;
        opacity: 0.6;
    }
    
    /* Integrity Card */
    .integrity-card {
        background: linear-gradient(90deg, rgba(239,68,68,0.1) 0%, rgba(18,22,32,0) 100%);
        border-left: 4px solid #ef4444;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        margin-bottom: 2.5rem;
        display: flex;
        align-items: center;
    }
    .integrity-text {
        color: #e2e8f0;
        font-size: 0.95rem;
        margin-left: 1rem;
        font-family: 'Inter', sans-serif;
    }
    .integrity-highlight {
        color: #ef4444;
        font-weight: 700;
        font-size: 1.05rem;
    }
    
    /* Spotlight Card */
    .spotlight-card {
        background: linear-gradient(145deg, rgba(18,22,32,0.9) 0%, rgba(15,23,42,0.95) 100%);
        border: 1px solid rgba(0, 242, 254, 0.4);
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.15);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2.5rem;
        position: relative;
    }
    .spotlight-badge {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        background: rgba(0, 242, 254, 0.1);
        border: 1px solid #00f2fe;
        color: #00f2fe;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .spotlight-header {
        display: flex;
        gap: 2rem;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    .spotlight-score-box {
        text-align: center;
        background: rgba(0,0,0,0.2);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        min-width: 140px;
    }
    .spotlight-score {
        font-size: 3rem;
        font-weight: 800;
        color: #00f2fe;
        font-family: 'Outfit', sans-serif;
        line-height: 1;
        text-shadow: 0 2px 10px rgba(0,242,254,0.3);
    }
    .spotlight-score-label {
        color: #8a99ad;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }
    .spotlight-name {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    .spotlight-title {
        font-size: 1.1rem;
        color: #94a3b8;
    }
    .spotlight-verdict {
        background: rgba(0,0,0,0.2);
        border-left: 3px solid #00f2fe;
        padding: 1.2rem;
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
        border-radius: 0 8px 8px 0;
    }
    .spotlight-why {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 0.5rem;
    }
    .spotlight-bullets {
        list-style-type: none;
        padding-left: 0;
        margin-bottom: 0;
    }
    .spotlight-bullets li {
        position: relative;
        padding-left: 1.8rem;
        margin-bottom: 0.8rem;
        color: #cbd5e1;
        font-size: 0.95rem;
    }
    .spotlight-bullets li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #00f2fe;
        font-weight: bold;
        background: rgba(0,242,254,0.1);
        border-radius: 50%;
        width: 1.2rem;
        height: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        top: 0.1rem;
    }
    .signal-pill {
        display: inline-block;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        color: #94a3b8;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        margin-top: 0.5rem;
    }
    .signal-pill.top {
        color: #00f2fe;
        border-color: rgba(0,242,254,0.3);
        background: rgba(0,242,254,0.05);
    }
    
    .candidate-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    /* Reasoning box */
    .reasoning-box {
        background: rgba(0, 242, 254, 0.05);
        border-left: 4px solid #00f2fe;
        padding: 1.2rem;
        border-radius: 4px;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.5;
        color: #e2e8f0;
    }
    
    /* Info items */
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    .info-item {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.03);
        padding: 0.8rem;
        border-radius: 8px;
    }
    .info-label {
        font-size: 0.75rem;
        color: #8a99ad;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .info-val {
        font-size: 1rem;
        color: #ffffff;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Workspace Paths
workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
candidates_file = os.path.join(workspace_dir, "candidates.jsonl")
jd_file = os.path.join(workspace_dir, "job_description.txt")

@st.cache_data(ttl=5)
def load_dashboard_data():
    """Loads precomputed candidate shortlist and pipeline stats."""
    import json
    stats_file = os.path.join(workspace_dir, "pipeline_stats.json")
    shortlist_file = os.path.join(workspace_dir, "dashboard_shortlist.json")
    
    if not os.path.exists(stats_file) or not os.path.exists(shortlist_file):
        st.error("Precomputed data files missing. Please run `python rank.py` first.")
        return {}, [], ""
        
    with open(stats_file, "r", encoding="utf-8") as f:
        stats = json.load(f)
        
    with open(shortlist_file, "r", encoding="utf-8") as f:
        shortlist_data = json.load(f)
        
    jd_text = ""
    if os.path.exists(jd_file):
        with open(jd_file, "r", encoding="utf-8") as f:
            jd_text = f.read()
            
    return stats, shortlist_data, jd_text

# Initialize App data
with st.spinner("Loading precomputed candidate pool..."):
    pipeline_stats, precomputed_shortlist, jd_text = load_dashboard_data()

# Sidebar controls
st.sidebar.markdown("<h2 style='color: #00f2fe; margin-bottom: 1.5rem;'>Dashboard Controls</h2>", unsafe_allow_html=True)

st.sidebar.markdown("### Active Scoring Model Weights")
st.sidebar.caption("- Template Match: **25.0%**")
st.sidebar.caption("- Semantic similarity: **25.0%**")
st.sidebar.caption("- Behavioral Signals: **20.0%**")
st.sidebar.caption("- Career Progression: **15.0%**")
st.sidebar.caption("- Profile Stability: **15.0%**")
st.sidebar.info("Weights are locked to ensure 100% alignment with the official ranker submission output.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Candidate Filtering")
filter_tier = st.sidebar.selectbox("Filter by Fit Tier:", ["All Clean (Tier 1 & 2)", "Tier 1 Only (Core)", "Tier 2 Only (Adjacent)"])
top_n = st.sidebar.number_input("Shortlist Size:", min_value=10, max_value=200, value=100)

# Filter shortlist based on selection
filtered_shortlist = []
for c in precomputed_shortlist:
    if filter_tier == "Tier 1 Only (Core)" and not c.get("has_t1", False):
        continue
    if filter_tier == "Tier 2 Only (Adjacent)" and c.get("has_t1", False):
        continue
    filtered_shortlist.append(c)

shortlist = filtered_shortlist[:top_n]

total_sample_count = pipeline_stats.get("total_raw", 0)
clean_sample_count = pipeline_stats.get("total_clean", 0)
candidates_pool_len = pipeline_stats.get("total_shortlisted", 0)
anomalies_count = pipeline_stats.get("total_anomalies", 0)
top_n_count = len(shortlist)

# Main Dashboard Interface
col_header_1, col_header_2 = st.columns([2, 1])
with col_header_1:
    st.markdown("<div class='brand-title'>HireMind</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-text'>From 100,000 Candidates to the Right Hire</div>", unsafe_allow_html=True)


tab_overview, tab_profile, tab_compare = st.tabs(["📊 Overview & Funnel", "👤 Candidate Profile", "⚖️ Compare Hub"])

with tab_overview:
    # Dashboard Key Metrics
    col_hero, col_supp = st.columns([1, 2])
    with col_hero:
        best_score = shortlist[0]["score_breakdown"]["final_score"] if shortlist else 0.0
        st.markdown(
            f"""<div class='hero-metric-card'>
                <div class='hero-metric-title'>🏆 Top Candidate Match</div>
                <div class='hero-metric-value'>{best_score*100:.1f}%</div>
            </div>""", unsafe_allow_html=True
        )

    with col_supp:
        # Adding some vertical centering or padding to align with the tall hero card
        st.markdown("<div style='padding-top: 1rem;'></div>", unsafe_allow_html=True)
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown(
                f"""<div class='metric-card'>
                    <div class='metric-title'>Total Pool Size</div>
                    <div class='metric-value'>{total_sample_count:,}</div>
                </div>""", unsafe_allow_html=True
            )
        with s_col2:
            st.markdown(
                f"""<div class='metric-card'>
                    <div class='metric-title'>Clean Candidates</div>
                    <div class='metric-value'>{clean_sample_count:,}</div>
                </div>""", unsafe_allow_html=True
            )
        with s_col3:
            st.markdown(
                f"""<div class='metric-card'>
                    <div class='metric-title'>Qualified Candidates</div>
                    <div class='metric-value'>{candidates_pool_len:,}</div>
                </div>""", unsafe_allow_html=True
            )

    # Pipeline Funnel Visualization
    st.markdown(f"""
        <div class="funnel-container">
            <div class="funnel-step">
                <div class="funnel-value">{total_sample_count:,}</div>
                <div class="funnel-label">Raw Candidates</div>
            </div>
            <div class="funnel-arrow">➔</div>
            <div class="funnel-step">
                <div class="funnel-value">{clean_sample_count:,}</div>
                <div class="funnel-label">Clean Candidates</div>
            </div>
            <div class="funnel-arrow">➔</div>
            <div class="funnel-step">
                <div class="funnel-value">{candidates_pool_len:,}</div>
                <div class="funnel-label">Qualified Candidates</div>
            </div>
            <div class="funnel-arrow">➔</div>
            <div class="funnel-step">
                <div class="funnel-value">{top_n_count:,}</div>
                <div class="funnel-label">Top Ranked</div>
            </div>
        </div>

        <div class="integrity-card">
            <div style="font-size: 1.8rem;">🛡️</div>
            <div class="integrity-text">
                <span class="integrity-highlight">{anomalies_count:,} Anomalies Removed</span> &nbsp;•&nbsp; Data Integrity Verified &nbsp;•&nbsp; Honeypots Filtered Before Ranking
            </div>
        </div>
    """, unsafe_allow_html=True)

    if len(shortlist) > 0:
        tc = shortlist[0]
        tc_prof = tc.get("profile", {})
        tc_breakdown = tc.get("score_breakdown", {})
        tc_signals = tc.get("redrob_signals", {})

        tc_name = tc_prof.get("anonymized_name", "Unknown")
        tc_title = tc_prof.get("current_title", "Engineer")
        tc_company = tc_prof.get("current_company", "Company")
        tc_score = tc_breakdown.get("final_score", 0.0)
        tc_verdict = tc.get("reasoning", "")

        signals_dict = {
            "Role Fit": tc_breakdown.get("semantic_score", 0),
            "Stability": tc_breakdown.get("stability_score", 0),
            "Career Growth": tc_breakdown.get("progression_score", 0),
            "Intent Signal": tc_breakdown.get("behavioral_score", 0)
        }
        top_signals = sorted(signals_dict.items(), key=lambda x: x[1], reverse=True)[:3]
        pills_html = "".join([f"<span class='signal-pill top'>{s[0]}</span>" for s in top_signals])

        bullets = []
        yoe = tc_prof.get("years_of_experience", 0)
        if "Role Fit" in [s[0] for s in top_signals]:
            bullets.append("Strongest semantic alignment to the core technical requirements of the target role")
        else:
            bullets.append("Excellent balance of template matching and required technical skills")

        if "Career Growth" in [s[0] for s in top_signals] or "Stability" in [s[0] for s in top_signals]:
            bullets.append(f"Consistent ML career progression and stability over {yoe} years of experience")
        else:
            bullets.append(f"Solid technical execution over {yoe} years of experience")

        notice = tc_signals.get("notice_period_days", 30)
        bullets.append(f"High recruiter engagement with a favorable {notice}-day notice period")

        bullets_html = "".join([f"<li>{b}</li>" for b in bullets])

        st.markdown(f"""
            <div class="spotlight-card">
                <div class="spotlight-badge">⭐ Rank #1 Spotlight</div>
                <div class="spotlight-header">
                    <div class="spotlight-score-box">
                        <div class="spotlight-score">{tc_score*100:.1f}%</div>
                        <div class="spotlight-score-label">Final Score</div>
                    </div>
                    <div>
                        <div class="spotlight-name">{tc_name}</div>
                        <div class="spotlight-title">{tc_title} at {tc_company}</div>
                        <div style="margin-top: 0.5rem;">{pills_html}</div>
                    </div>
                </div>
                <div class="spotlight-verdict">{tc_verdict}</div>
                <div class="spotlight-why">Why This Candidate Won</div>
                <ul class="spotlight-bullets">
                    {bullets_html}
                </ul>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### Candidate Shortlist")

    # Construct display DataFrame
    data_rows = []
    for idx, c in enumerate(shortlist):
        prof = c.get("profile", {})
        signals = c.get("redrob_signals", {})
        breakdown = c["score_breakdown"]

        data_rows.append({
            "Rank": c.get("rank", idx + 1),
            "Candidate ID": c["candidate_id"],
            "Name": prof.get("anonymized_name", "Anonymous"),
            "Tier": "Tier 1 (Core)" if c.get("has_t1") else "Tier 2 (Adjacent)",
            "Final Score": f"{breakdown['final_score']*100:.1f}%",
            "Title": prof.get("current_title", "N/A"),
            "Company": prof.get("current_company", "N/A"),
            "YOE": f"{prof.get('years_of_experience', 0.0):.1f} yrs",
            "Notice Period": f"{signals.get('notice_period_days', 0)} days",
        })
    df_shortlist = pd.DataFrame(data_rows)
    df_shortlist = df_shortlist.sort_values(by="Rank", ascending=True)

    # Display table
    st.dataframe(df_shortlist, use_container_width=True, hide_index=True)

    # Explorer section

with tab_profile:
    st.markdown("### Candidate Explorer")
    selected_name = st.selectbox("Select a Candidate to inspect details:", df_shortlist["Name"].tolist() if not df_shortlist.empty else ["No Candidates Available"])

    if not df_shortlist.empty and selected_name != "No Candidates Available":
        # Find matching candidate record
        selected_idx = df_shortlist[df_shortlist["Name"] == selected_name].iloc[0]["Rank"] - 1
        c = shortlist[selected_idx]
        breakdown = c["score_breakdown"]

        prof = c.get("profile", {})
        signals = c.get("redrob_signals", {})
        history = c.get("career_history", [])
        skills = c.get("skills", [])

        # Generate reasoning
        reasoning = c.get("reasoning", "")

        tab1, tab2, tab3 = st.tabs(["🤖 AI Verdict & Scores", "📈 Career Trajectory", "🛠️ Raw Signals & Skills"])

        with tab1:
            col_verdict1, col_verdict2 = st.columns([1, 1])

            with col_verdict1:
                st.markdown(
                    f"""<div class='detail-card'>
                        <div class='candidate-name'>{prof.get('anonymized_name', 'Anonymous')}</div>
                        <div class='candidate-title'>{prof.get('current_title', 'N/A')} at {prof.get('current_company', 'N/A')}</div>
                        <div class='info-grid'>
                            <div class='info-item'><div class='info-label'>Candidate ID</div><div class='info-val'>{c['candidate_id']}</div></div>
                            <div class='info-item'><div class='info-label'>Experience</div><div class='info-val'>{prof.get('years_of_experience', 0.0):.1f} Years</div></div>
                            <div class='info-item'><div class='info-label'>Location</div><div class='info-val'>{prof.get('location', 'N/A')}</div></div>
                            <div class='info-item'><div class='info-label'>Notice Period</div><div class='info-val'>{signals.get('notice_period_days', 0)} Days</div></div>
                        </div>
                        <div class='reasoning-box'><strong>AI Recruiter Verdict:</strong><br><br>{reasoning}</div>
                    </div>""", unsafe_allow_html=True
                )

            with col_verdict2:
                st.markdown("#### Score Breakdown Visualizer")

                role_fit = ((breakdown["template_score"] + breakdown["semantic_score"]) / 2.0) * 100
                career_growth = breakdown["progression_score"] * 100
                stability = breakdown["stability_score"] * 100
                intent = breakdown["behavioral_score"] * 100

                st.markdown(f"""
                <div style="margin-top: 1rem; padding: 1.5rem; background: rgba(0,0,0,0.03); border-radius: 12px; border: 1px solid rgba(0,0,0,0.05);">
                    <div style="margin-bottom: 1.2rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                            <span style="color: #8a99ad; font-size: 0.85rem; text-transform: uppercase;">Role Fit</span>
                            <span style="color: #ffffff; font-weight: 600;">{role_fit:.1f}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); border-radius: 4px; width: 100%; height: 8px;">
                            <div style="background: #00f2fe; width: {role_fit}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 1.2rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                            <span style="color: #8a99ad; font-size: 0.85rem; text-transform: uppercase;">Career Growth</span>
                            <span style="color: #ffffff; font-weight: 600;">{career_growth:.1f}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); border-radius: 4px; width: 100%; height: 8px;">
                            <div style="background: #ffb347; width: {career_growth}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 1.2rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                            <span style="color: #8a99ad; font-size: 0.85rem; text-transform: uppercase;">Stability</span>
                            <span style="color: #ffffff; font-weight: 600;">{stability:.1f}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); border-radius: 4px; width: 100%; height: 8px;">
                            <div style="background: #00e676; width: {stability}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div style="margin-bottom: 1.2rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                            <span style="color: #8a99ad; font-size: 0.85rem; text-transform: uppercase;">Intent Signal</span>
                            <span style="color: #ffffff; font-weight: 600;">{intent:.1f}%</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); border-radius: 4px; width: 100%; height: 8px;">
                            <div style="background: #d500f9; width: {intent}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            st.markdown("#### Career Timeline")
            for job in history:
                duration = job.get("duration_months", 0)
                st.markdown(f"**{job.get('title', 'Developer')}** at *{job.get('company', 'Company')}* ({duration} months)")
                st.caption(job.get("description", ""))
                st.markdown("---")

        with tab3:
            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                st.markdown("#### Platform Behavioral Signals")
                st.markdown(f"""
                <div style="padding: 1rem; background: rgba(25, 30, 41, 0.4); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                    <ul style="color: #e2e8f0; line-height: 1.8;">
                        <li>Active Date: <strong>{signals.get('last_active_date', 'N/A')}</strong></li>
                        <li>Response Rate: <strong>{signals.get('recruiter_response_rate', 0.0)*100:.1f}%</strong></li>
                        <li>Avg Response Time: <strong>{signals.get('avg_response_time_hours', 0.0):.1f} Hours</strong></li>
                        <li>Open to Work: <strong>{'Yes' if signals.get('open_to_work_flag') else 'No'}</strong></li>
                        <li>Email Verified: <strong>{'Yes' if signals.get('verified_email') else 'No'}</strong></li>
                        <li>Phone Verified: <strong>{'Yes' if signals.get('verified_phone') else 'No'}</strong></li>
                        <li>Github Activity Score: <strong>{signals.get('github_activity_score', 0)}</strong></li>
                        <li>Interview Completion: <strong>{signals.get('interview_completion_rate', 0.0)*100:.1f}%</strong></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col_sub2:
                st.markdown("#### Technical Skills")
                if skills:
                    badges = []
                    for s in skills:
                        name = s.get('name', 'N/A')
                        duration = s.get('duration_months', 0)
                        badges.append(f"<span style='background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.3); color: #00f2fe; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; margin-right: 0.5rem; margin-bottom: 0.5rem; display: inline-block;'>{name} <span style='color: #8a99ad; font-size: 0.75rem; margin-left: 4px;'>{duration}m</span></span>")
                    st.markdown(f"<div style='margin-top: 1rem;'>{''.join(badges)}</div>", unsafe_allow_html=True)
                else:
                    st.caption("No explicit skills listed.")

    # Display Job Description details in expander at bottom
    st.markdown("---")
    st.markdown("### Target Job Description")

    jd_lines = jd_text.split('\n')
    summary_dict = {}
    for line in jd_lines[:10]:
        if ":" in line:
            k, v = line.split(":", 1)
            summary_dict[k.strip()] = v.strip()

    st.markdown(f"""
    **JD Summary:** {summary_dict.get('Job Description', 'Senior AI Engineer — Founding Team')} at {summary_dict.get('Company', 'Redrob AI')}  
    **Experience Range:** {summary_dict.get('Experience Required', '5–9 years')}  
    **Key Responsibilities:** Own the ranking, retrieval, and matching systems. Audit existing system, ship v2 ranking system, and set up evaluation infrastructure.  
    **Required Skills:** Production embeddings-based retrieval, vector databases, strong Python, evaluation frameworks (NDCG, MRR).
    """)

    with st.expander("Expand Full JD", expanded=False):
        st.text(jd_text)

with tab_compare:
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    if len(shortlist) >= 2:
        names = [c.get("profile", {}).get("anonymized_name", "Anonymous") for c in shortlist]
        
        c1, c2 = st.columns(2)
        with c1:
            name_a = st.selectbox("Left Candidate", names, index=0, key="comp_a")
        with c2:
            name_b = st.selectbox("Right Candidate", names, index=1, key="comp_b")
            
        def get_cand(n):
            for c in shortlist:
                if c.get("profile", {}).get("anonymized_name", "Anonymous") == n:
                    return c
            return shortlist[0]
            
        cand_a = get_cand(name_a)
        cand_b = get_cand(name_b)
        
        def render_comp_card(c, other_c):
            prof = c.get("profile", {})
            bdown = c.get("score_breakdown", {})
            sigs = c.get("redrob_signals", {})
            
            o_prof = other_c.get("profile", {})
            o_bdown = other_c.get("score_breakdown", {})
            o_sigs = other_c.get("redrob_signals", {})
            
            def get_val(item, key, default=0):
                return item.get(key, default)
                
            def style_metric(label, val1, val2, is_higher_better=True, format_str="{v}", is_hero=False):
                color = "white"
                border = "rgba(255,255,255,0.05)"
                if val1 > val2:
                    if is_higher_better:
                        color = "#00f2fe"
                        border = "#00f2fe"
                    else:
                        color = "white"
                        border = "rgba(255,255,255,0.05)"
                elif val1 < val2:
                    if not is_higher_better:
                        color = "#00f2fe"
                        border = "#00f2fe"
                        
                v1_str = format_str.replace("{v}", str(val1))
                font_sz = "2.5rem" if is_hero else "1.2rem"
                lbl_color = "#00f2fe" if is_hero else "#8a99ad"
                lbl_weight = "700" if is_hero else "400"
                return f"<div style='margin-bottom: 0.8rem; background: rgba(255,255,255,0.02); padding: 0.8rem; border-radius: 8px; border-left: 2px solid {border};'><div style='font-size: 0.75rem; color: {lbl_color}; text-transform: uppercase; margin-bottom: 0.2rem; font-weight: {lbl_weight};'>{label}</div><div style='font-size: {font_sz}; font-weight: 800; font-family: Outfit, sans-serif; color: {color};'>{v1_str}</div></div>"

            html = f"<div class='spotlight-card' style='padding: 1.5rem; height: 100%; margin-bottom: 0;'><div style='font-size: 1.5rem; font-weight: 700; color: white; margin-bottom: 0.2rem;'>{prof.get('anonymized_name', 'Name')}</div><div style='color: #94a3b8; font-size: 0.95rem; margin-bottom: 1.5rem;'>{prof.get('current_title', 'Title')} at {prof.get('current_company', 'Company')}</div>"
            
            # Final Score
            html += style_metric("Final Score", round(bdown.get('final_score',0)*100, 1), round(o_bdown.get('final_score',0)*100, 1), True, "{v}%", is_hero=True)
            # YOE
            html += style_metric("Years of Experience", round(prof.get('years_of_experience',0), 1), round(o_prof.get('years_of_experience',0), 1), True, "{v} yrs")
            # Role Fit Score
            html += style_metric("Role Fit Score", round(bdown.get('semantic_score',0)*100, 1), round(o_bdown.get('semantic_score',0)*100, 1), True, "{v}%")
            # Career Growth Score
            html += style_metric("Career Growth Score", round(bdown.get('progression_score',0)*100, 1), round(o_bdown.get('progression_score',0)*100, 1), True, "{v}%")
            # Stability Score
            html += style_metric("Stability Score", round(bdown.get('stability_score',0)*100, 1), round(o_bdown.get('stability_score',0)*100, 1), True, "{v}%")
            # Intent Signal Score
            html += style_metric("Intent Signal Score", round(bdown.get('behavioral_score',0)*100, 1), round(o_bdown.get('behavioral_score',0)*100, 1), True, "{v}%")
            
            # Notice Period (lower is better usually, let's treat it as neutral or lower=better)
            # Actually, the user asked to highlight higher score... Wait, if notice period is 15 vs 30, 15 is better.
            html += style_metric("Notice Period", sigs.get('notice_period_days', 30), o_sigs.get('notice_period_days', 30), False, "{v} days")
            
            # Location
            loc = prof.get('location', 'N/A')
            html += f"<div style='margin-bottom: 0.8rem; background: rgba(255,255,255,0.02); padding: 0.8rem; border-radius: 8px; border-left: 2px solid rgba(255,255,255,0.05);'><div style='font-size: 0.75rem; color: #8a99ad; text-transform: uppercase; margin-bottom: 0.2rem;'>Location</div><div style='font-size: 1.1rem; color: white;'>{loc}</div></div>"
            
            # Verdict
            verdict = c.get('reasoning', '')
            html += f"<div style='margin-top: 1.5rem; background: rgba(0,0,0,0.2); border-left: 3px solid rgba(255,255,255,0.1); padding: 1rem; border-radius: 0 8px 8px 0;'><div style='font-size: 0.75rem; color: #8a99ad; text-transform: uppercase; margin-bottom: 0.4rem;'>Recruiter Verdict</div><div style='font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;'>{verdict}</div></div>"
            
            # Top Skills
            skills = prof.get('skills', [])
            skills_html = ""
            if skills:
                badges = []
                for skill in skills[:6]:  # Limit to 6 skills so it doesn't overflow
                    badges.append(f"<span style='display: inline-block; background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.3); color: #00f2fe; padding: 0.2rem 0.6rem; border-radius: 12px; font-size: 0.75rem; margin-right: 0.4rem; margin-bottom: 0.4rem;'>{skill}</span>")
                skills_html = f"<div style='margin-top: 1.5rem;'><div style='font-size: 0.75rem; color: #8a99ad; text-transform: uppercase; margin-bottom: 0.4rem;'>Top Skills</div><div>{''.join(badges)}</div></div>"
            html += skills_html
            
            html += "</div>"
            return html
            
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(render_comp_card(cand_a, cand_b), unsafe_allow_html=True)
        with c2:
            st.markdown(render_comp_card(cand_b, cand_a), unsafe_allow_html=True)
            
