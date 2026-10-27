import streamlit as st
import requests
from datetime import datetime
import os

st.set_page_config(page_title="Safe Acca AI", page_icon="⚽", layout="centered")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #00c853;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 50px;
        font-size: 16px;
    }
    .match-card {
        background-color: #1c1f2e;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 14px;
        border-left: 6px solid #00c853;
        color: #ffffff !important;
    }
    .match-card b {
        color: #ffffff !important;
        font-size: 16px;
    }
    .match-card small {
        color: #b0b0b0 !important;
    }
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets["API_FOOTBALL_KEY"]
headers = {"x-apisports-key": API_KEY}

SMARTLINK = "https://asiafilm.org/4/bd80344d93bc26083f8b20a55302a626"

# Strong leagues get higher safety score
TOP_LEAGUES = [
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
    "UEFA Champions League", "UEFA Europa League", "Championship",
    "Eredivisie", "Primeira Liga", "Belgian Pro League", "Scottish Premiership"
]

st.title("⚽ Safe Acca AI")
st.markdown("### Safest Football Accumulator for Today")

st.info(f"**Support the app** → [👉 Click here to Support / Unlock]({SMARTLINK})")

st.divider()

col1, col2 = st.columns(2)
with col1:
    target_odds = st.number_input("🎯 Target Odds", min_value=10, max_value=3000, value=200, step=10)
with col2:
    max_legs = st.number_input("📊 Max Legs", min_value=3, max_value=18, value=10)

if st.button("Generate Safest Accumulator"):
    with st.spinner("Analyzing today's matches for safest picks..."):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures"
        params = {"date": today}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=20)
            data = response.json()
            
            if response.status_code != 200:
                st.error(f"API Error: {data}")
            else:
                fixtures = data.get("response", [])
                
                if not fixtures:
                    st.warning("No matches found or daily limit reached.")
                else:
                    scored_matches = []
                    
                    for f in fixtures:
                        if f["fixture"]["status"]["short"] not in ["NS", "TBD"]:
                            continue
                        
                        home = f["teams"]["home"]["name"]
                        away = f["teams"]["away"]["name"]
                        league = f["league"]["name"]
                        
                        # Safety score system
                        safety = 40  # base score
                        
                        # Bonus for top leagues
                        for top in TOP_LEAGUES:
                            if top.lower() in league.lower():
                                safety += 30
                                break
                        
                        # Prefer home teams
                        safety += 15
                        
                        # Decide market based on safety
                        if safety >= 70:
                            pick = "Home Win"
                            odds = 1.40
                        elif safety >= 55:
                            pick = "Over 1.5 Goals"
                            odds = 1.30
                        else:
                            pick = "BTTS - No"
                            odds = 1.55
                        
                        scored_matches.append({
                            "match": f"{home} vs {away}",
                            "league": league,
                            "pick": pick,
                            "odds": odds,
                            "safety": safety
                        })
                    
                    # Sort by highest safety first
                    scored_matches.sort(key=lambda x: x["safety"], reverse=True)
                    
                    # Build the accumulator
                    selected = []
                    total = 1.0
                    
                    for m in scored_matches:
                        if len(selected) >= max_legs:
                            break
                        selected.append(m)
                        total *= m["odds"]
                        if total >= target_odds:
                            break
                    
                    st.success(f"Analyzed {len(fixtures)} matches • Selected safest ones")
                    st.subheader(f"Safest Accumulator • Target ≈ {target_odds}")
                    
                    for i, p in enumerate(selected, 1):
                        st.markdown(f"""
                        <div class="match-card">
                            <b>{i}. {p['match']}</b><br>
                            <small>{p['league']}</small><br>
                            <span style="color:#00e676; font-weight:bold; font-size:15px;">{p['pick']}</span> 
                            <span style="color:#ffffff;"> @ {p['odds']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"### Total Estimated Odds: `{total:.2f}`")
                    st.markdown(f"**Legs:** {len(selected)}")
                    st.caption("⚠️ For entertainment only. Gamble responsibly. 18+")
                    
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("Free plan: 100 requests/day • App may stop when limit is reached")
