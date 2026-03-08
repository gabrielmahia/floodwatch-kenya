"""FloodWatch NBI - Page 04: City Benchmarks."""
from pathlib import Path
import json
import streamlit as st
from utils.charts import resilience_radar, resilience_scatter

st.set_page_config(page_title="City Benchmarks - FloodWatch NBI", page_icon="globe", layout="wide")
st.title("City Benchmarks")
st.markdown(
    "**Diagnostic, not aspirational.** Rotterdam is the ceiling. "
    "Medellin is the relevant analogue. Dhaka is the warning."
)
st.caption(
    "Resilience scores are manually curated composites. "
    "See HANDOFF.md for scoring methodology."
)

ROOT = Path(__file__).parent.parent

@st.cache_data
def load():
    with open(ROOT / "data" / "city_benchmarks.json") as f:
        return json.load(f)["cities"]

cities = load()
city_names = [c["name"] for c in cities]

with st.sidebar:
    st.header("Radar selection")
    selected = st.multiselect(
        "Cities to compare",
        options=city_names,
        default=city_names,
    )

if len(selected) >= 2:
    st.plotly_chart(resilience_radar(cities, selected), use_container_width=True)
else:
    st.info("Select at least 2 cities to render the radar.")

st.divider()
st.plotly_chart(resilience_scatter(cities), use_container_width=True)

st.divider()
st.markdown("### City Profiles")

for city in cities:
    score = city["resilience_score"]
    color = "#22C55E" if score >= 70 else "#EAB308" if score >= 40 else "#EF4444"
    with st.expander(f"{city['name']}, {city['country']} — Score: {score}/100"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Resilience score", f"{score}/100")
        c2.metric("Deaths/event avg", city["deaths_per_event_avg"])
        c3.metric("Budget USD/capita", f"${city['flood_budget_usd_per_capita']}")
        c4.metric("Years to resilience", city.get("years_to_resilience") or "Unknown")

        st.markdown(f"**Key intervention:** {city['key_intervention']}")
        st.markdown(f"**Political enabler:** {city['political_enabler']}")
        if city["transferable"]:
            st.markdown("**Transferable to Nairobi:**")
            for lesson in city["transferable"]:
                st.markdown(f"  - {lesson}")
        else:
            st.markdown("*No transferable lessons identified yet.*")
