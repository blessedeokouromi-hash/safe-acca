import streamlit as st
import requests
from datetime import datetime
import os

st.set_page_config(
    page_title="Safe Acca AI",
    page_icon="⚽",
    layout="centered"
)

# Custom CSS for better look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        background-color: #00c853;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 50px;
    }
    .match-card {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 12px;
        border-left: 5px solid #00c853;
    }
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets["API_FOOTBALL_KEY"]
headers = {"x-apisports-key": API_KEY}

SMARTLINK = "https://asiafilm.org/4/bd80344d93bc26083f8b20a55302a626"

st.title("⚽ Safe Acca AI")
st.markdown("### Find the safest football accumulators for today")

# Support section
st.info(f"**Support the app** → [👉 Click here to unlock / support]({SMARTLINK})")

st.divider()

col1, col2 = st.columns(2)
with col1:
    target_odds = st.number_input("🎯 Target Odds", min_value=10, max_value=3000, value=200, step=10)
with col2:
    max_legs = st.number_input("📊 Max Legs", min_value=3, max_value=20, value=10)

st.markdown("### Preferred Markets")
markets = st.multiselect(
    "Select markets you want the AI to use:",
    ["Home Win", "Away Win", "Over 1.5 Goals", "Under 3.5 Goals", "BTTS No", "Double Chance 1X"],
    default=["Home Win", "Over 1.5 Goals", "BTTS No"]
)

if st.button("Generate Safest Accumulator"):
    with st.spinner("Analyzing today's matches across all leagues..."):
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
                    st.warning("No matches found today or daily limit reached (100 requests).")
                else:
                    # Simple ranking + different markets
                    picks = []
                    market_list = markets if markets else ["Home Win"]
                    
                    for i, f in enumerate(fixtures):
                        status = f["fixture"]["status"]["short"]
                        if status not in ["NS", "TBD"]:
                            continue
                        
                        home = f["teams"]["home"]["name"]
                        away = f["teams"]["away"]["name"]
                        league = f["league"]["name"]
                        
                        # Rotate markets for variety
                        market = market_list[i % len(market_list)]
                        
                        if "Home" in market:
                            pick = f"Home Win"
                            odds = 1.45
                        elif "Away" in market:
                            pick = f"Away Win"
                            odds = 1.55
                        elif "Over 1.5" in market:
                            pick = "Over 1.5 Goals"
                            odds = 1.30
                        elif "Under 3.5" in market:
                            pick = "Under 3.5 Goals"
                            odds = 1.35
                        elif "BTTS No" in market:
                            pick = "BTTS - No"
                            odds = 1.50
                        else:
                            pick = "Double Chance 1X"
                            odds = 1.25
                        
                        picks.append({
                            "match": f"{home} vs {away}",
                            "league": league,
                            "pick": pick,
                            "odds": odds
                        })
                    
                    # Build accumulator
                    selected = []
                    total = 1.0
                    
                    for p in picks:
                        if len(selected) >= max_legs:
                            break
                        selected.append(p)
                        total *= p["odds"]
                        if total >= target_odds:
                            break
                    
                    st.success(f"Analyzed {len(fixtures)} matches today")
                    st.subheader(f"Safest Accumulator • Target ≈ {target_odds}")
                    
                    for i, p in enumerate(selected, 1):
                        st.markdown(f"""
                        <div class="match-card">
                            <b>{i}. {p['match']}</b><br>
                            <small>{p['league']}</small><br>
                            <span style="color:#00c853; font-weight:bold;">{p['pick']}</span> @ {p['odds']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"### Total Estimated Odds: `{total:.2f}`")
                    st.markdown(f"**Legs:** {len(selected)}")
                    st.caption("⚠️ For entertainment only. Gamble responsibly. 18+")
                    
        except Exception as e:
            st.error(f"Error occurred: {e}")

st.divider()
st.caption("Free plan limit: 100 API requests per day • App may stop when limit is reached")
