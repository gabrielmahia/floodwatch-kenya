"""Page 4 — City Benchmarks: radar + scatter 6-city resilience comparison."""
import streamlit as st
import json
from utils.charts import resilience_radar, deaths_per_event_scatter, dark_layout
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="City Benchmarks · FloodWatch NBI", page_icon="🌍", layout="wide")
st.markdown("# 🌍 City Benchmarks")
st.caption("⚠️ Benchmark scores are manually curated composites — not formula outputs. See README for methodology.")

@st.cache_data
def load():
    with open("data/city_benchmarks.json") as f:
        return json.load(f)["cities"]

cities = load()

STATUS_LABELS = {
    "current":  ("🔴", "Current state — Nairobi"),
    "analogue":  ("🟡", "Relevant analogue — messy city that made progress"),
    "ceiling":   ("🟢", "Ceiling case — shows what is possible"),
    "warning":   ("⚫", "Warning — trajectory Nairobi must avoid"),
}

with st.sidebar:
    st.markdown("## City selection")
    selected_names = st.multiselect(
        "Compare cities",
        [c["name"] for c in cities],
        default=[c["name"] for c in cities],
    )
    selected = [c for c in cities if c["name"] in selected_names]
    st.divider()
    st.markdown("**Legend**")
    for key, (icon, label) in STATUS_LABELS.items():
        st.markdown(f"{icon} {label}")

if not selected:
    st.warning("Select at least one city.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(resilience_radar(selected), use_container_width=True)
with col2:
    st.plotly_chart(deaths_per_event_scatter(selected), use_container_width=True)

st.divider()
st.markdown("### City profiles")
for city in selected:
    icon, label = STATUS_LABELS.get(city.get("status",""), ("⚪",""))
    color = city.get("color","#888")
    years = city.get("years_to_resilience")
    years_str = f"{years} years from start" if years else "trajectory unclear"
    with st.expander(f"{icon} **{city['name']}, {city['country']}** — Resilience score: {city['resilience_score']}/100"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Resilience score", city["resilience_score"])
        c2.metric("Deaths/event avg", city["deaths_per_event_avg"])
        c3.metric("Riparian compliance", f"{city['riparian_compliance_pct']}%")
        c4.metric("Flood budget/capita", f"USD {city['flood_budget_usd_per_capita']:.0f}")

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(f"**Drainage coverage:** {city['drainage_coverage_pct']}%")
            st.markdown(f"**Early warning:** {city['early_warning_hours']}h")
            st.markdown(f"**Flood-vulnerable population:** {city['flood_vulnerable_pct']}%")
            st.markdown(f"**Time to current resilience:** {years_str}")
        with cc2:
            st.markdown(f"**Key intervention:**
{city['key_intervention']}")
            st.markdown(f"**Political enabler:**
{city['political_enabler']}")

        if city.get("transferable"):
            st.markdown("**Transferable to Nairobi:**")
            for lesson in city["transferable"]:
                st.markdown(f"- {lesson}")

st.divider()
df = pd.DataFrame(selected)
st.markdown("### Raw comparison table")
show_cols = ["name","country","resilience_score","deaths_per_event_avg",
             "riparian_compliance_pct","drainage_coverage_pct",
             "early_warning_hours","flood_budget_usd_per_capita","flood_vulnerable_pct"]
st.dataframe(df[show_cols].set_index("name"), use_container_width=True)
