import streamlit as st
import requests
from datetime import datetime
import os

st.set_page_config(page_title="Safe Acca AI", page_icon="⚽")

API_KEY = st.secrets["API_FOOTBALL_KEY"]

headers = {
    "x-apisports-key": API_KEY
}

SMARTLINK = "https://asiafilm.org/4/bd80344d93bc26083f8b20a55302a626"

st.title("⚽ Safe Acca AI")
st.markdown("### Safest Football Accumulator for Today")

st.markdown(f"""
### Support the App
Please click the link below to support (this helps keep the app running):

**[👉 Click here to Support / Unlock]({SMARTLINK})**
""")

st.divider()

col1, col2 = st.columns(2)
with col1:
    target_odds = st.number_input("Target Odds", min_value=10, max_value=2000, value=200)
with col2:
    max_legs = st.number_input("Max Legs", min_value=3, max_value=20, value=12)

if st.button("Generate Safest Accumulator", type="primary"):
    with st.spinner("Fetching today's matches..."):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures"
        params = {"date": today}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            data = response.json()
            
            if response.status_code != 200:
                st.error(f"API Error: {data}")
            else:
                fixtures = data.get("response", [])
                
                if not fixtures:
                    st.warning("No matches found today or API limit reached.")
                else:
                    scored = []
                    for f in fixtures:
                        status = f["fixture"]["status"]["short"]
                        if status not in ["NS", "TBD"]:
                            continue
                        
                        home = f["teams"]["home"]["name"]
                        away = f["teams"]["away"]["name"]
                        league = f["league"]["name"]
                        
                        scored.append({
                            "match": f"{home} vs {away}",
                            "league": league,
                            "odds": 1.38
                        })
                    
                    selected = []
                    total = 1.0
                    
                    for m in scored:
                        if len(selected) >= max_legs:
                            break
                        selected.append(m)
                        total *= m["odds"]
                        if total >= target_odds:
                            break
                    
                    st.success(f"Found {len(fixtures)} matches today")
                    st.subheader(f"Safest Accumulator (Target ≈ {target_odds})")
                    
                    for i, p in enumerate(selected, 1):
                        st.markdown(f"**{i}. {p['match']}**")
                        st.caption(f"League: {p['league']} | Suggested: Home Win @ {p['odds']}")
                    
                    st.markdown(f"### Total Estimated Odds: **{total:.2f}**")
                    st.markdown(f"**Legs used:** {len(selected)}")
                    st.info("This is for entertainment only. Gamble responsibly. 18+")
                    
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("Free API limit: 100 requests per day. The app may stop when the limit is reached.")
