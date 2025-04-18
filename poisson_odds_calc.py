import streamlit as st
from scipy.stats import poisson
import pandas as pd
from cachetools import cached, TTLCache
import logging
import math

# Custom CSS styling
st.markdown("""
<style>
    /* Main page styling */
    .main {background-color: #f5f5f5}
    
    /* Header styling */
    h1 {color: #2e7d32; border-bottom: 2px solid #2e7d32}
    h2 {color: #1a237e}
    
    /* Input section styling */
    .stNumberInput, .stTextInput {padding: 8px; border-radius: 4px}
    
    /* Results cards */
    .result-card {
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background: white;
        margin: 1rem 0;
    }
    
    /* Highlight numbers */
    .highlight {color: #d32f2f; font-weight: bold}
</style>
""", unsafe_allow_html=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cache for fetched data with a TTL of 10 minutes
cache = TTLCache(maxsize=100, ttl=600)

# Page setup
st.title("⚽ Poisson Odds Calculator")
st.markdown("Calculate match probabilities using Poisson distribution")

# Team inputs
col1, col2 = st.columns(2)
with col1:
    home_team = st.text_input("Home Team", placeholder="Enter home team name")
with col2:
    away_team = st.text_input("Away Team", placeholder="Enter away team name")

# League averages
st.subheader("League Averages")
avg_col1, avg_col2 = st.columns(2)
with avg_col1:
    home_avg_goals = st.number_input("Home Team League Avg Goals", min_value=0.0, value=0.75, step=0.01)
with avg_col2:
    away_avg_goals = st.number_input("Away Team League Avg Goals", min_value=0.0, value=0.75, step=0.01)

# Team statistics
with st.expander("Team Statistics (Expand)"):
    st.subheader("Home Team Stats")
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1:
        home_goals_for = st.number_input("Home Goals Scored", min_value=0.0, value=0.0)
    with h_col2:
        home_goals_against = st.number_input("Home Goals Conceded", min_value=0.0, value=0.0)
    with h_col3:
        home_matches_played = st.number_input("Home Matches Played", min_value=0.0, value=0.0)

    st.subheader("Away Team Stats")
    a_col1, a_col2, a_col3 = st.columns(3)
    with a_col1:
        away_goals_for = st.number_input("Away Goals Scored", min_value=0.0, value=0.0)
    with a_col2:
        away_goals_against = st.number_input("Away Goals Conceded", min_value=0.0, value=0.0)
    with a_col3:
        away_matches_played = st.number_input("Away Matches Played", min_value=0.0, value=0.0)

# Calculate averages
avg_home_goals_for = home_goals_for / home_matches_played if home_matches_played > 0 else 0
avg_home_goals_against = home_goals_against / home_matches_played if home_matches_played > 0 else 0
home_attack = avg_home_goals_for / home_avg_goals if home_avg_goals > 0 else 0
home_defense = avg_home_goals_against / away_avg_goals if away_avg_goals > 0 else 0

avg_away_goals_for = away_goals_for / away_matches_played if away_matches_played > 0 else 0
avg_away_goals_against = away_goals_against / away_matches_played if away_matches_played > 0 else 0
away_attack = avg_away_goals_for / away_avg_goals if away_avg_goals > 0 else 0
away_defense = avg_away_goals_against / home_avg_goals if home_avg_goals > 0 else 0

# Calculate expected goals
home_expected_goals = home_attack * away_defense * home_avg_goals
away_expected_goals = away_attack * home_defense * away_avg_goals

# Display expected goals with styling
st.subheader("Expected Goals")
exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    st.markdown(f"<div class='result-card'>🏠 **{home_team}**: <span class='highlight'>{home_expected_goals:.2f}</span></div>", unsafe_allow_html=True)
with exp_col2:
    st.markdown(f"<div class='result-card'>✈️ **{away_team}**: <span class='highlight'>{away_expected_goals:.2f}</span></div>", unsafe_allow_html=True)

# Poisson calculation function (same as before)
def calculate_odds(home_exp, away_exp):
    home_win_prob = 0.0
    draw_prob = 0.0
    away_win_prob = 0.0
    over_2_5_prob = 0.0
    
    max_goals = 10
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            prob = poisson.pmf(home_goals, home_exp) * poisson.pmf(away_goals, away_exp)
            if home_goals > away_goals:
                home_win_prob += prob
            elif home_goals == away_goals:
                draw_prob += prob
            else:
                away_win_prob += prob
            if home_goals + away_goals > 2.5:
                over_2_5_prob += prob
    
    under_2_5_prob = 1.0 - over_2_5_prob
    
    home_win_odds = 1.0 / home_win_prob if home_win_prob > 0 else float('inf')
    draw_odds = 1.0 / draw_prob if draw_prob > 0 else float('inf')
    away_win_odds = 1.0 / away_win_prob if away_win_prob > 0 else float('inf')
    over_2_5_odds = 1.0 / over_2_5_prob if over_2_5_prob > 0 else float('inf')
    under_2_5_odds = 1.0 / under_2_5_prob if under_2_5_prob > 0 else float('inf')
    
    return {
        '1': home_win_odds,
        'X': draw_odds,
        '2': away_win_odds,
        'Over 2.5': over_2_5_odds,
        'Under 2.5': under_2_5_odds
    }

# Calculate and display odds
if home_expected_goals > 0 and away_expected_goals > 0:
    odds = calculate_odds(home_expected_goals, away_expected_goals)
    
    st.subheader("📊 Match Odds")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='result-card'>" +
                    f"<h4>1X2 Odds</h4>" +
                    f"<p>🏠 Home Win: <span class='highlight'>{odds['1']:.2f}</span></p>" +
                    f"<p>🤝 Draw: <span class='highlight'>{odds['X']:.2f}</span></p>" +
                    f"<p>✈️ Away Win: <span class='highlight'>{odds['2']:.2f}</span></p>" +
                    "</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='result-card'>" +
                    f"<h4>Goal Markets</h4>" +
                    f"<p>⚽ Over 2.5: <span class='highlight'>{odds['Over 2.5']:.2f}</span></p>" +
                    f"<p>🛡️ Under 2.5: <span class='highlight'>{odds['Under 2.5']:.2f}</span></p>" +
                    "</div>", unsafe_allow_html=True)
else:
    st.warning("⚠️ Please enter valid statistics to calculate odds")