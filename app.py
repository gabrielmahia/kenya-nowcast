# Copyright (c) 2026 Gabriel Mahia / AI Kung Fu LLC. MIT License.
# kenya-nowcast — County Economic Tracker
# Research basis:
#   IMF Working Paper 2026/020 "Nowcasting Economic Growth with ML and Satellite Data"
#   PLOS One 2025: "Shedding light on development" — VIIRS NTL for 34 SSA countries
#   Henderson, Storeygard, Weil (NBER 2009): "Measuring Economic Growth from Outer Space"
# First in Kenya: county-level economic health score using free satellite proxy data
# =============================================================================

import streamlit as st
import urllib.request
import json
import math
import datetime

st.set_page_config(
    page_title="Kenya County Economic Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  .stApp { background: #050f1a; }
  .title { font-size:1.4rem; font-weight:800; color:#03a9f4; text-align:center; }
  .sub   { font-size:0.82rem; color:#4fc3f7; text-align:center; margin-bottom:1rem; }
  .county-card { background:#071826; border:1px solid #0277bd; border-radius:8px;
                 padding:10px 12px; margin:4px; display:inline-block; min-width:180px; }
  .demo-tag { background:#b71c1c; color:#fff; font-size:0.65rem; padding:2px 6px;
              border-radius:3px; font-weight:700; margin-left:6px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌍 Kenya County Economic Tracker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub">Satellite-proxy economic health scores for all 47 counties '
    '<span class="demo-tag">DEMO — Synthetic Proxy Data</span></div>',
    unsafe_allow_html=True
)

# ── SYNTHETIC DEMO DATA ───────────────────────────────────────────────────────
# Source note: "DEMO — Synthetic data modeled on VIIRS NTL trends and KNBS county
#              indicators. Not official GDP estimates. For research/demonstration only."
# Methodology basis: IMF WP 2026/020, PLOS One 2025 (VIIRS + DHS wealth index)
COUNTIES = {
    "Nairobi": {"score": 82, "ntl_change": +4.2, "pop": 4.9, "region": "Central"},
    "Mombasa": {"score": 71, "ntl_change": +2.1, "pop": 1.3, "region": "Coast"},
    "Kisumu": {"score": 61, "ntl_change": +1.8, "pop": 1.2, "region": "Nyanza"},
    "Nakuru": {"score": 65, "ntl_change": +3.1, "pop": 2.2, "region": "Rift Valley"},
    "Kiambu": {"score": 74, "ntl_change": +3.8, "pop": 2.4, "region": "Central"},
    "Machakos": {"score": 55, "ntl_change": +1.2, "pop": 1.4, "region": "Eastern"},
    "Uasin Gishu": {"score": 62, "ntl_change": +2.4, "pop": 1.2, "region": "Rift Valley"},
    "Meru": {"score": 57, "ntl_change": +1.6, "pop": 1.6, "region": "Eastern"},
    "Kilifi": {"score": 42, "ntl_change": +0.8, "pop": 1.5, "region": "Coast"},
    "Kakamega": {"score": 45, "ntl_change": +0.5, "pop": 2.0, "region": "Western"},
    "Bungoma": {"score": 43, "ntl_change": +0.6, "pop": 1.7, "region": "Western"},
    "Kisii": {"score": 51, "ntl_change": +1.1, "pop": 1.3, "region": "Nyanza"},
    "Turkana": {"score": 18, "ntl_change": -0.3, "pop": 1.1, "region": "North Rift"},
    "Mandera": {"score": 15, "ntl_change": -0.5, "pop": 0.9, "region": "North Eastern"},
    "Wajir": {"score": 14, "ntl_change": -0.4, "pop": 0.8, "region": "North Eastern"},
    "Garissa": {"score": 22, "ntl_change": +0.1, "pop": 0.9, "region": "North Eastern"},
    "Marsabit": {"score": 16, "ntl_change": -0.2, "pop": 0.5, "region": "North Eastern"},
    "Isiolo": {"score": 25, "ntl_change": +0.4, "pop": 0.3, "region": "Eastern"},
    "Tana River": {"score": 19, "ntl_change": -0.1, "pop": 0.4, "region": "Coast"},
    "Samburu": {"score": 20, "ntl_change": +0.0, "pop": 0.4, "region": "North Rift"},
    "Embu": {"score": 58, "ntl_change": +1.4, "pop": 0.6, "region": "Eastern"},
    "Nyeri": {"score": 60, "ntl_change": +2.0, "pop": 0.8, "region": "Central"},
    "Murang'a": {"score": 63, "ntl_change": +2.8, "pop": 1.1, "region": "Central"},
    "Kirinyaga": {"score": 59, "ntl_change": +1.9, "pop": 0.6, "region": "Central"},
    "Nyandarua": {"score": 50, "ntl_change": +0.9, "pop": 0.6, "region": "Central"},
    "Laikipia": {"score": 48, "ntl_change": +1.0, "pop": 0.5, "region": "Central"},
    "Nyamira": {"score": 44, "ntl_change": +0.7, "pop": 0.7, "region": "Nyanza"},
    "Migori": {"score": 47, "ntl_change": +0.8, "pop": 1.1, "region": "Nyanza"},
    "Homa Bay": {"score": 40, "ntl_change": +0.3, "pop": 1.2, "region": "Nyanza"},
    "Siaya": {"score": 41, "ntl_change": +0.5, "pop": 1.0, "region": "Nyanza"},
    "Vihiga": {"score": 42, "ntl_change": +0.4, "pop": 0.6, "region": "Western"},
    "Trans Nzoia": {"score": 50, "ntl_change": +1.1, "pop": 1.0, "region": "North Rift"},
    "Elgeyo-Marakwet": {"score": 38, "ntl_change": +0.3, "pop": 0.5, "region": "North Rift"},
    "West Pokot": {"score": 24, "ntl_change": -0.2, "pop": 0.7, "region": "North Rift"},
    "Baringo": {"score": 35, "ntl_change": +0.2, "pop": 0.7, "region": "North Rift"},
    "Narok": {"score": 45, "ntl_change": +0.9, "pop": 1.2, "region": "Rift Valley"},
    "Bomet": {"score": 43, "ntl_change": +0.7, "pop": 0.9, "region": "Rift Valley"},
    "Kericho": {"score": 55, "ntl_change": +1.5, "pop": 0.9, "region": "Rift Valley"},
    "Nandi": {"score": 48, "ntl_change": +0.9, "pop": 0.9, "region": "Rift Valley"},
    "Kajiado": {"score": 60, "ntl_change": +3.0, "pop": 1.1, "region": "Rift Valley"},
    "Makueni": {"score": 46, "ntl_change": +0.8, "pop": 1.0, "region": "Eastern"},
    "Kitui": {"score": 38, "ntl_change": +0.3, "pop": 1.2, "region": "Eastern"},
    "Taita-Taveta": {"score": 40, "ntl_change": +0.6, "pop": 0.4, "region": "Coast"},
    "Kwale": {"score": 36, "ntl_change": +0.4, "pop": 0.9, "region": "Coast"},
    "Lamu": {"score": 44, "ntl_change": +0.8, "pop": 0.2, "region": "Coast"},
    "Tharaka-Nithi": {"score": 45, "ntl_change": +0.7, "pop": 0.4, "region": "Eastern"},
    "Busia": {"score": 39, "ntl_change": +0.4, "pop": 0.9, "region": "Western"},
}

def score_to_label(s):
    if s >= 70: return "🟢 Strong", "#4caf50"
    if s >= 55: return "🟡 Growing", "#cddc39"
    if s >= 40: return "🟠 Developing", "#ff9800"
    if s >= 25: return "🔴 Lagging", "#f44336"
    return "🔴 Critical", "#d32f2f"

# ── Filters ───────────────────────────────────────────────────────────────────
regions = sorted(set(v["region"] for v in COUNTIES.values()))
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    sel_region = st.selectbox("Filter by Region", ["All Regions"] + regions)
with col_f2:
    sort_by = st.selectbox("Sort by", ["Economic Score ↓", "NTL Growth ↓", "Name A-Z"])

filtered = {k: v for k, v in COUNTIES.items()
            if sel_region == "All Regions" or v["region"] == sel_region}
if sort_by == "Economic Score ↓":
    filtered = dict(sorted(filtered.items(), key=lambda x: -x[1]["score"]))
elif sort_by == "NTL Growth ↓":
    filtered = dict(sorted(filtered.items(), key=lambda x: -x[1]["ntl_change"]))
else:
    filtered = dict(sorted(filtered.items()))

# ── Summary metrics ───────────────────────────────────────────────────────────
scores = [v["score"] for v in filtered.values()]
m1, m2, m3, m4 = st.columns(4)
m1.metric("Counties Tracked", len(filtered))
m2.metric("Avg Economic Score", f"{sum(scores)/len(scores):.0f}/100")
m3.metric("Strong (70+)", sum(1 for s in scores if s >= 70))
m4.metric("Critical (<25)", sum(1 for s in scores if s < 25))

# ── County cards ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 47 County Economic Health Dashboard")

cols = st.columns(3)
for idx, (county, data) in enumerate(filtered.items()):
    label, color = score_to_label(data["score"])
    ntl = data["ntl_change"]
    ntl_arrow = "↑" if ntl > 0 else ("↓" if ntl < 0 else "→")
    ntl_color = "#4caf50" if ntl > 0 else ("#f44336" if ntl < 0 else "#9e9e9e")
    with cols[idx % 3]:
        st.markdown(f"""
<div class="county-card">
  <div style="font-weight:800;color:#e3f2fd;font-size:0.95rem">{county}</div>
  <div style="font-size:0.7rem;color:#4fc3f7">{data["region"]}</div>
  <div style="font-size:1.4rem;font-weight:800;color:{color}">{data["score"]}<span style="font-size:0.7rem">/100</span></div>
  <div style="font-size:0.75rem;color:{color}">{label}</div>
  <div style="font-size:0.72rem;color:{ntl_color};margin-top:3px">
    NTL Proxy: {ntl_arrow} {abs(ntl):.1f}% &nbsp;·&nbsp; Pop: {data["pop"]}M
  </div>
</div>""", unsafe_allow_html=True)

st.markdown("---")
st.info(
    "📡 **Methodology (DEMO):** Economic scores modeled using nighttime light (NTL) satellite "
    "proxy data — methodology from IMF WP 2026/020 and PLOS One 2025 (VIIRS DNBF data across "
    "34 Sub-Saharan African countries). **Synthetic data** representative of county-level "
    "economic divergence patterns. Not official KNBS statistics.\n\n"
    "Real implementation would use NASA Black Marble VIIRS data (earthengine.google.com) "
    "combined with KNBS county economic surveys."
)
st.caption("🌍 kenya-nowcast · AI Kung Fu LLC · Research: IMF WP 2026/020 | PLOS One 2025 | Henderson, Storeygard & Weil (NBER 2009)")
