import streamlit as st
import requests
from datetime import datetime

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

# Strong leagues
TOP_LEAGUES = ["premier league", "la liga", "serie a", "bundesliga", "ligue 1",
               "champions league", "europa league", "championship", "eredivisie",
               "primeira liga", "belgian", "scottish", "super lig"]

# Leagues that usually have more goals
HIGH_SCORING = ["bundesliga", "eredivisie", "liga mx", "a-league", "mls"]

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
    with st.spinner("Analyzing matches and choosing best market for each..."):
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
                    scored = []
                    
                    for f in fixtures:
                        if f["fixture"]["status"]["short"] not in ["NS", "TBD"]:
                            continue
                        
                        home = f["teams"]["home"]["name"]
                        away = f["teams"]["away"]["name"]
                        league = f["league"]["name"]
                        league_lower = league.lower()
                        
                        # Calculate safety score
                        safety = 45
                        
                        # Bonus for top leagues
                        is_top = any(top in league_lower for top in TOP_LEAGUES)
                        if is_top:
                            safety += 25
                        
                        # Home advantage
                        safety += 12
                        
                        # Decide the BEST market for this specific match
                        if is_top:
                            pick = "Home Win"
                            odds = 1.42
                            reason = "Strong league + Home advantage"
                        elif any(h in league_lower for h in HIGH_SCORING):
                            pick = "Over 1.5 Goals"
                            odds = 1.28
                            reason = "High-scoring league"
                        else:
                            pick = "BTTS - No"
                            odds = 1.50
                            reason = "Tighter match expected"
                        
                        # Small extra variation
                        if "cup" in league_lower or "trophy" in league_lower:
                            pick = "Double Chance 1X"
                            odds = 1.30
                            reason = "Cup match - safer with Double Chance"
                        
                        scored.append({
                            "match": f"{home} vs {away}",
                            "league": league,
                            "pick": pick,
                            "odds": odds,
                            "safety": safety,
                            "reason": reason
                        })
                    
                    # Sort by safety (best first)
                    scored.sort(key=lambda x: x["safety"], reverse=True)
                    
                    selected = []
                    total = 1.0
                    
                    for m in scored:
                        if len(selected) >= max_legs:
                            break
                        selected.append(m)
                        total *= m["odds"]
                        if total >= target_odds:
                            break
                    
                    st.success(f"Analyzed {len(fixtures)} matches • Chose best market for each")
                    st.subheader(f"Safest Accumulator • Target ≈ {target_odds}")
                    
                    for i, p in enumerate(selected, 1):
                        st.markdown(f"""
                        <div class="match-card">
                            <b>{i}. {p['match']}</b><br>
                            <small>{p['league']}</small><br>
                            <span style="color:#00e676; font-weight:bold; font-size:15px;">{p['pick']}</span> 
                            <span style="color:#ffffff;"> @ {p['odds']}</span><br>
                            <small style="color:#888;">{p['reason']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"### Total Estimated Odds: `{total:.2f}`")
                    st.markdown(f"**Legs:** {len(selected)}")
                    st.caption("⚠️ For entertainment only. Gamble responsibly. 18+")
                    
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("Free plan: 100 requests/day • App may stop when limit is reached")
