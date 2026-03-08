"""
FloodWatch NBI — Urban flood resilience intelligence for Nairobi.

Landing page: alert banner, KPI summary, quick navigation.

⚠️  DEMO DATA — All incident and policy records are representative samples.
    Real data sources listed in README § 12.
"""
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="FloodWatch NBI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_incidents():
    return pd.read_csv("data/incidents.csv")

@st.cache_data
def load_policies():
    return pd.read_csv("data/policies.csv")

incidents = load_incidents()
policies  = load_policies()

# ── Alert banner ──────────────────────────────────────────────────────────────
# Replace with live KMD API call when available — see README § 6.1
ALERT_ACTIVE  = True
ALERT_LEVEL   = "HIGH"
ALERT_MESSAGE = "Long-rains season active (April–June). Mathare and Mukuru zones on elevated watch. Drainage clearance operations reported incomplete in 7 sub-wards."

if ALERT_ACTIVE:
    color = {"HIGH": "#FF6B35", "CRITICAL": "#FF3333", "WATCH": "#FFB347"}.get(ALERT_LEVEL, "#FF6B35")
    st.markdown(f"""
    <div style="background:{color}22;border-left:4px solid {color};padding:12px 16px;
                border-radius:4px;margin-bottom:16px;">
      <span style="color:{color};font-weight:700">⚠ FLOOD ALERT — {ALERT_LEVEL}</span>
      <span style="color:#E8E8E8;margin-left:12px">{ALERT_MESSAGE}</span>
    </div>
    """, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🌊 FloodWatch NBI")
st.markdown(
    "Urban flood resilience intelligence for Nairobi. "
    "Tracking incidents, policy accountability, and the enforcement gap."
)
st.markdown(
    "<small style='color:#888'>⚠️ DEMO DATA — representative samples only. "
    "See sidebar for navigation and README for real data sources.</small>",
    unsafe_allow_html=True,
)
st.divider()

# ── KPI row ───────────────────────────────────────────────────────────────────
total_deaths     = int(incidents["deaths"].sum())
total_displaced  = int(incidents["displaced"].sum())
total_damage_ksh = incidents["infra_damage_ksh_m"].sum()
critical_count   = len(incidents[incidents["severity"] == "Critical"])
policy_gap       = incidents["policy_existed"].sum() - incidents["policy_enforced"].sum()
avg_response     = incidents["response_days"].mean()

# Policy-level KPIs
total_policies   = len(policies)
stalled_or_not   = len(policies[policies["status"].isin(["Stalled","Not Enforced","Not Started","Draft Only"])])
lives_at_risk    = policies[policies["status"] != "Completed"]["lives_saved_estimate"].sum()
budget_allocated = policies["budget_allocated_ksh_m"].sum()
budget_utilized  = (policies["budget_allocated_ksh_m"] * policies["budget_utilized_pct"] / 100).sum()
budget_idle_pct  = round((1 - budget_utilized / budget_allocated) * 100, 1) if budget_allocated else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💀 Deaths (sampled)", f"{total_deaths:,}", help="Deaths across 15 sampled incidents")
col2.metric("🏠 Displaced (sampled)", f"{total_displaced:,}", help="Persons displaced across sampled incidents")
col3.metric("⚡ Critical Incidents", critical_count, help="Severity = Critical")
col4.metric("❌ Enforcement Gap", int(policy_gap), help="Incidents where policy existed but was not enforced")
col5.metric("⏱ Avg Response (days)", f"{avg_response:.1f}", help="Days to formal response from incident")

st.divider()

col6, col7, col8, col9 = st.columns(4)
col6.metric("📋 Policies Tracked", total_policies)
col7.metric("🚫 Stalled / Not Enforced", stalled_or_not,
            delta=f"{round(stalled_or_not/total_policies*100)}% of policies",
            delta_color="inverse")
col8.metric("❤ Lives at Risk (policy gap)", f"{lives_at_risk:,}",
            help="Estimated lives saved if stalled policies were fully implemented")
col9.metric("💰 Budget Idle", f"{budget_idle_pct}%",
            help=f"KSh {budget_allocated - budget_utilized:.0f}M of KSh {budget_allocated:.0f}M unspent",
            delta_color="inverse")

st.divider()

# ── Navigation cards ──────────────────────────────────────────────────────────
st.markdown("### Navigate")
c1, c2, c3 = st.columns(3)
with c1:
    st.info("📍 **Incident Map**

Interactive map of flood events with severity markers, riparian corridors, and risk heatmap.")
with c2:
    st.info("📊 **Impact Analysis**

Zone breakdowns, seasonal patterns, and the enforcement gap visualised.")
with c3:
    st.info("📋 **Policy Tracker**

Budget utilisation, blocking factors, and lives at risk from stalled policies.")

c4, c5, c6 = st.columns(3)
with c4:
    st.info("🌍 **City Benchmarks**

Radar and scatter comparison of Nairobi against Medellin, Rotterdam, Jakarta, Dhaka, Singapore.")
with c5:
    st.info("🔧 **Risk Calculator**

Site-level composite flood risk score — test any location's vulnerability.")
with c6:
    st.info("📣 **Community Report**

Submit a flood incident or infrastructure failure from the field.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌊 FloodWatch NBI")
    st.markdown("**v0.1.0 · DEMO DATA**")
    st.divider()
    st.markdown("### About")
    st.markdown(
        "Nairobi floods repeatedly. The policies to address this largely exist. "
        "This platform makes the **enforcement gap** visible and measurable."
    )
    st.divider()
    st.markdown("### Data")
    st.markdown(f"- **{len(incidents)}** sampled incidents")
    st.markdown(f"- **{len(policies)}** policies tracked")
    st.markdown(f"- **{total_deaths}** deaths in sample")
    st.markdown(f"- **{total_displaced:,}** displaced in sample")
    st.divider()
    st.markdown("### Design principle")
    st.markdown(
        "*The enforcement gap is the story. Every feature should connect back "
        "to the distance between policy existence and policy implementation.*"
    )
    st.divider()
    st.caption("Part of the [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack) ecosystem")
    st.caption("Maintained by [Gabriel Mahia](https://github.com/gabrielmahia)")
