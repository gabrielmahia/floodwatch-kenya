"""
FloodWatch NBI — Landing page.

KPI summary, active alert banner, and enforcement gap headline.
All analytical pages are in pages/ and load via Streamlit multi-page routing.

⚠ DEMO DATA — All incident figures are illustrative samples.
  Real data should be sourced from NCC, NDOC, and Kenya Red Cross.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.charts import (
    dark_layout,
    enforcement_gap_chart,
    flood_timeline_chart,
)

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="FloodWatch NBI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load data ──────────────────────────────────────────────────
ROOT = Path(__file__).parent

@st.cache_data
def load_incidents():
    df = pd.read_csv(ROOT / "data" / "incidents.csv", parse_dates=["date"])
    df["policy_existed"]  = df["policy_existed"].astype(bool)
    df["policy_enforced"] = df["policy_enforced"].astype(bool)
    return df

@st.cache_data
def load_benchmarks():
    with open(ROOT / "data" / "city_benchmarks.json") as f:
        return json.load(f)["cities"]

df = load_incidents()

# ── Alert banner (hardcoded — replace with KMD API) ────────────
st.markdown("""
<div style="background:#7C2D12;border-left:4px solid #EF4444;padding:12px 16px;
            border-radius:4px;font-family:monospace;margin-bottom:1rem;">
  🔴 <b>ACTIVE ALERT — Long Rains Season</b> &nbsp;|&nbsp;
  Elevated flood risk: Mathare, Mukuru, Kibera &nbsp;|&nbsp;
  <span style="color:#FCA5A5;">Replace this banner with live KMD API data (see HANDOFF.md §6.1)</span>
</div>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────
st.markdown("# 🌊 FloodWatch NBI")
st.markdown(
    "**Urban flood resilience intelligence for Nairobi** — "
    "incident tracking, policy accountability, city benchmarking."
)
st.caption(
    "⚠️ DEMO DATA · Figures are illustrative samples. "
    "Production data: NCC incident reports · NDOC · Kenya Red Cross."
)
st.divider()

# ── KPI row ────────────────────────────────────────────────────
total_deaths     = int(df["deaths"].sum())
total_displaced  = int(df["displaced"].sum())
total_damage     = df["infra_damage_ksh_m"].sum()
avg_response     = df["response_days"].mean()
enforced_pct     = df["policy_enforced"].mean() * 100
policy_gap_pct   = (
    df[df["policy_existed"] & ~df["policy_enforced"]].shape[0] / len(df) * 100
)

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Deaths (sample)",       f"{total_deaths}",         delta=None)
col2.metric("Displaced (sample)",    f"{total_displaced:,}",    delta=None)
col3.metric("Damage (KSh M)",        f"{total_damage:,.0f}",    delta=None)
col4.metric("Avg Response (days)",   f"{avg_response:.1f}",     delta=None)
col5.metric("Policy Enforced",       f"{enforced_pct:.0f}%",
            delta=f"-{100-enforced_pct:.0f}% gap", delta_color="inverse")
col6.metric("Incidents sampled",     f"{len(df)}",              delta=None)

st.divider()

# ── Enforcement gap headline ────────────────────────────────────
col_a, col_b = st.columns([3, 2])
with col_a:
    st.markdown("### The Enforcement Gap")
    st.markdown(
        "In **{pct:.0f}%** of sampled incidents, a relevant flood policy existed "
        "but was **not being enforced** at the time of the event. "
        "This is the core accountability failure this platform tracks.".format(
            pct=policy_gap_pct
        )
    )
    st.plotly_chart(enforcement_gap_chart(df), use_container_width=True)

with col_b:
    st.markdown("### Timeline")
    st.plotly_chart(flood_timeline_chart(df), use_container_width=True)

st.divider()

# ── Navigation guide ────────────────────────────────────────────
st.markdown("### Explore")
nav_cols = st.columns(3)
pages = [
    ("📍 Incident Map",       "pages/01 — Folium map with severity filters, riparian overlays, and incident log"),
    ("📊 Impact Analysis",    "pages/02 — Zone breakdowns, seasonality, cause treemap, enforcement correlation"),
    ("📋 Policy Tracker",     "pages/03 — 10 policies: status, budget gap, blocker taxonomy, lives at risk"),
    ("🌍 City Benchmarks",    "pages/04 — Radar + scatter comparing Nairobi against Rotterdam, Medellin, Dhaka, Singapore, Jakarta"),
    ("🔧 Risk Calculator",    "pages/05 — Site-level composite flood risk scorer with input sliders"),
    ("📣 Community Report",   "pages/06 — Citizen flood incident submission form"),
]
for i, (title, desc) in enumerate(pages):
    nav_cols[i % 3].info(f"**{title}**\n\n{desc}")
