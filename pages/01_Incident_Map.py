"""Page 1 — Incident Map: Folium map with filters, incident log table."""
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from utils.map_utils import build_incident_map, build_risk_heatmap

st.set_page_config(page_title="Incident Map · FloodWatch NBI", page_icon="📍", layout="wide")
st.markdown("# 📍 Incident Map")
st.caption("⚠️ DEMO DATA — 15 sampled incidents. Toggle between marker map and risk heatmap.")

@st.cache_data
def load(): return pd.read_csv("data/incidents.csv")
df = load()

with st.sidebar:
    st.markdown("## Filters")
    severities = st.multiselect("Severity", ["Critical","High","Medium","Low"],
                                default=["Critical","High","Medium","Low"])
    zones = st.multiselect("Zone", sorted(df["zone"].unique()), default=list(df["zone"].unique()))
    show_enforced = st.selectbox("Policy enforcement", ["All","Enforced only","Not enforced only"])
    map_mode = st.radio("Map mode", ["Incident markers", "Risk heatmap"])

filt = df[df["severity"].isin(severities) & df["zone"].isin(zones)]
if show_enforced == "Enforced only":
    filt = filt[filt["policy_enforced"] == True]
elif show_enforced == "Not enforced only":
    filt = filt[filt["policy_enforced"] != True]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Incidents shown", len(filt))
col2.metric("Deaths", int(filt["deaths"].sum()))
col3.metric("Displaced", f"{int(filt['displaced'].sum()):,}")
col4.metric("Enforcement gap",
    int((filt["policy_existed"] == True).sum() - (filt["policy_enforced"] == True).sum()))

st.divider()

if len(filt) == 0:
    st.warning("No incidents match current filters.")
else:
    m = build_incident_map(filt) if map_mode == "Incident markers" else build_risk_heatmap(filt)
    st_folium(m, width="100%", height=520, returned_objects=[])

st.divider()
st.markdown("### Incident Log")
display_cols = ["date","location","zone","severity","deaths","displaced","cause",
                "infra_damage_ksh_m","response_days","policy_existed","policy_enforced"]
st.dataframe(
    filt[display_cols].sort_values("date", ascending=False).reset_index(drop=True),
    use_container_width=True,
    column_config={
        "infra_damage_ksh_m": st.column_config.NumberColumn("Damage (KSh M)", format="%.1f"),
        "policy_existed":     st.column_config.CheckboxColumn("Policy existed"),
        "policy_enforced":    st.column_config.CheckboxColumn("Policy enforced"),
    }
)
