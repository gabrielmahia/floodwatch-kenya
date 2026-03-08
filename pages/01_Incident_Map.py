"""FloodWatch NBI - Page 01: Incident Map."""
from pathlib import Path
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from utils.map_utils import build_incident_map, build_risk_heatmap

st.set_page_config(page_title="Incident Map - FloodWatch NBI", page_icon="map", layout="wide")
st.title("Incident Map")
st.caption("DEMO DATA - illustrative sample. Blue lines = approximate riparian corridors (not WRMA-verified GIS).")

ROOT = Path(__file__).parent.parent

@st.cache_data
def load():
    df = pd.read_csv(ROOT / "data" / "incidents.csv", parse_dates=["date"])
    df["policy_existed"]  = df["policy_existed"].astype(bool)
    df["policy_enforced"] = df["policy_enforced"].astype(bool)
    return df

df = load()

with st.sidebar:
    st.header("Filters")
    severities = st.multiselect("Severity",
        options=["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"])
    zones = st.multiselect("Zone",
        options=sorted(df["zone"].unique()),
        default=list(df["zone"].unique()))
    causes = st.multiselect("Cause",
        options=sorted(df["cause"].unique()),
        default=list(df["cause"].unique()))
    enforcement_filter = st.selectbox("Policy enforcement status",
        options=["All", "Policy existed, not enforced", "Policy enforced", "No policy"])
    map_mode = st.radio("Map type", ["Incident markers", "Risk heatmap"])

filtered = df[
    df["severity"].isin(severities) &
    df["zone"].isin(zones) &
    df["cause"].isin(causes)
]
if enforcement_filter == "Policy existed, not enforced":
    filtered = filtered[filtered["policy_existed"] & ~filtered["policy_enforced"]]
elif enforcement_filter == "Policy enforced":
    filtered = filtered[filtered["policy_enforced"]]
elif enforcement_filter == "No policy":
    filtered = filtered[~filtered["policy_existed"]]

st.markdown(f"**{len(filtered)} incident(s)** matching filters")

if len(filtered) == 0:
    st.warning("No incidents match the current filters.")
else:
    m = build_risk_heatmap(filtered) if map_mode == "Risk heatmap" else build_incident_map(filtered)
    st_folium(m, width="100%", height=520)

st.divider()
st.markdown("### Incident Log")
display = filtered[[
    "date", "location", "zone", "severity", "deaths",
    "displaced", "cause", "infra_damage_ksh_m", "response_days",
    "policy_existed", "policy_enforced",
]].copy()
display["date"] = display["date"].dt.strftime("%Y-%m-%d")
display = display.rename(columns={
    "infra_damage_ksh_m": "damage_ksh_m",
    "policy_existed": "policy?",
    "policy_enforced": "enforced?",
})

def colour_severity(val):
    c = {"Critical": "#EF4444", "High": "#F97316", "Medium": "#EAB308", "Low": "#22C55E"}
    return f"color: {c.get(val, '')}"

st.dataframe(
    display.style.applymap(colour_severity, subset=["severity"]),
    use_container_width=True, height=380)

st.divider()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Deaths",         int(filtered["deaths"].sum()))
c2.metric("Displaced",      f"{int(filtered['displaced'].sum()):,}")
c3.metric("Damage (KSh M)", f"{filtered['infra_damage_ksh_m'].sum():,.0f}")
c4.metric("Avg response",   f"{filtered['response_days'].mean():.1f} days")
