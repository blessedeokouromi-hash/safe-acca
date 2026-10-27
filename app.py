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

st.title("⚽ Safe Acca AI")
st.markdown("### Real Predictions • Safest Accumulator")

st.info(f"**Support the app** → [👉 Click here to Support / Unlock]({SMARTLINK})")
st.caption("This version uses real API predictions")

st.divider()

col1, col2 = st.columns(2)
with col1:
    target_odds = st.number_input("🎯 Target Odds", min_value=10, max_value=2000, value=150, step=10)
with col2:
    max_legs = st.number_input("📊 Max Legs", min_value=3, max_value=12, value=8)

if st.button("Generate Safest Accumulator (Real Predictions)"):
    with st.spinner("Fetching fixtures + real predictions..."):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Get fixtures
        fixtures_url = "https://v3.football.api-sports.io/fixtures"
        fixtures_res = requests.get(fixtures_url, headers=headers, params={"date": today}, timeout=20)
        fixtures_data = fixtures_res.json()
        
        if fixtures_res.status_code != 200:
            st.error(f"Fixtures Error: {fixtures_data}")
        else:
            fixtures = fixtures_data.get("response", [])
            not_started = [f for f in fixtures if f["fixture"]["status"]["short"] in ["NS", "TBD"]]
            
            if not not_started:
                st.warning("No upcoming matches found today.")
            else:
                selected_fixtures = not_started[:14]  # limit to save requests
                
                predictions = []
                
                for f in selected_fixtures:
                    fixture_id = f["fixture"]["id"]
                    home = f["teams"]["home"]["name"]
                    away = f["teams"]["away"]["name"]
                    league = f["league"]["name"]
                    country = f["league"].get("country", "International")
                    
                    # Get prediction
                    pred_url = f"https://v3.football.api-sports.io/predictions?fixture={fixture_id}"
                    pred_res = requests.get(pred_url, headers=headers, timeout=15)
                    
                    if pred_res.status_code == 200:
                        pred_data = pred_res.json().get("response", [])
                        if pred_data:
                            pred = pred_data[0]
                            percent = pred.get("predictions", {}).get("percent", {})
                            advice = pred.get("predictions", {}).get("advice", "")
                            
                            home_pct = float(percent.get("home", "0").replace("%", "") or 0)
                            draw_pct = float(percent.get("draw", "0").replace("%", "") or 0)
                            away_pct = float(percent.get("away", "0").replace("%", "") or 0)
                            
                            # Choose best market
                            if home_pct >= 55:
                                pick = "Home Win"
                                odds = 1.40
                                conf = home_pct
                            elif away_pct >= 55:
                                pick = "Away Win"
                                odds = 1.50
                                conf = away_pct
                            elif home_pct + draw_pct >= 68:
                                pick = "Double Chance 1X"
                                odds = 1.25
                                conf = home_pct + draw_pct
                            else:
                                pick = "Over 1.5 Goals"
                                odds = 1.30
                                conf = 58
                            
                            predictions.append({
                                "match": f"{home} vs {away}",
                                "league": f"{country} - {league}",
                                "pick": pick,
                                "odds": odds,
                                "confidence": conf,
                                "advice": advice
                            })
                
                predictions.sort(key=lambda x: x["confidence"], reverse=True)
                
                selected = []
                total = 1.0
                
                for p in predictions:
                    if len(selected) >= max_legs:
                        break
                    selected.append(p)
                    total *= p["odds"]
                    if total >= target_odds:
                        break
                
                if not selected:
                    st.warning("Could not get enough predictions.")
                else:
                    st.success(f"Used real predictions • {len(predictions)} matches analyzed")
                    st.subheader(f"Safest Accumulator • Target ≈ {target_odds}")
                    
                    for i, p in enumerate(selected, 1):
                        st.markdown(f"""
                        <div class="match-card">
                            <b>{i}. {p['match']}</b><br>
                            <small style="color:#00e676;">{p['league']}</small><br>
                            <span style="color:#00e676; font-weight:bold;">{p['pick']}</span> 
                            <span style="color:#fff;"> @ {p['odds']}</span><br>
                            <small>Confidence: {p['confidence']:.0f}%</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown(f"### Total Estimated Odds: `{total:.2f}`")
                    st.markdown(f"**Legs:** {len(selected)}")
                    st.caption("⚠️ For entertainment only. Gamble responsibly. 18+")
                    
        st.caption(f"Requests used this time: \~{1 + len(selected_fixtures)}")

st.divider()
st.caption("Free plan: 100 requests/day")
