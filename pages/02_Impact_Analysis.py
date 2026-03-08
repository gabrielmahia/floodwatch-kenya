"""Page 2 — Impact Analysis: zone breakdowns, seasonality, enforcement gap."""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.charts import (flood_timeline_chart, zone_impact_bar,
                           enforcement_gap_chart, dark_layout)

st.set_page_config(page_title="Impact Analysis · FloodWatch NBI", page_icon="📊", layout="wide")
st.markdown("# 📊 Impact Analysis")
st.caption("⚠️ DEMO DATA — representative samples only.")

@st.cache_data
def load(): return pd.read_csv("data/incidents.csv")
df = load()
df["date"] = pd.to_datetime(df["date"])

tab1, tab2, tab3 = st.tabs(["Timeline", "Zone Breakdown", "Enforcement Gap"])

with tab1:
    st.markdown("#### Flood Incidents Over Time")
    st.markdown("Bubble size = deaths. Colour = severity. Hover for details.")
    st.plotly_chart(flood_timeline_chart(df), use_container_width=True)

    st.markdown("#### Seasonal Pattern")
    monthly = df.groupby(df["date"].dt.month).agg(
        incidents=("date","count"), deaths=("deaths","sum"), displaced=("displaced","sum")
    ).reset_index()
    monthly.columns = ["month_num","incidents","deaths","displaced"]
    monthly["month_name"] = pd.to_datetime(monthly["month_num"], format="%m").dt.strftime("%b")
    fig_monthly = px.bar(monthly, x="month_name", y="displaced", color="deaths",
                         color_continuous_scale=["#1A1F2E","#FF6B35","#FF3333"],
                         labels={"displaced":"Displaced","month_name":"Month","deaths":"Deaths"})
    st.plotly_chart(dark_layout(fig_monthly, "Monthly Displacement — All Years", 360),
                    use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(zone_impact_bar(df), use_container_width=True)
    with col2:
        cause_counts = df.groupby("cause").agg(
            incidents=("date","count"), deaths=("deaths","sum")
        ).reset_index()
        fig_cause = px.bar(cause_counts, x="cause", y="incidents", color="deaths",
                           color_continuous_scale=["#1A1F2E","#FF6B35","#FF3333"])
        st.plotly_chart(dark_layout(fig_cause, "Incidents by Cause", 360), use_container_width=True)

    dmg = df.groupby("zone")["infra_damage_ksh_m"].sum().sort_values(ascending=True).reset_index()
    fig_dmg = px.bar(dmg, x="infra_damage_ksh_m", y="zone", orientation="h",
                     color="infra_damage_ksh_m",
                     color_continuous_scale=["#1A1F2E","#FF6B35","#FF3333"])
    st.plotly_chart(dark_layout(fig_dmg, "Infrastructure Damage by Zone (KSh M)", 340),
                    use_container_width=True)

with tab3:
    existed  = int(df["policy_existed"].sum())
    enforced = int(df["policy_enforced"].sum())
    gap      = existed - enforced
    st.markdown(
        f"Of **{existed} incidents** where a relevant policy existed, only **{enforced}** "
        f"were in areas where that policy was being enforced — a gap of **{gap} incidents** "
        f"(**{round(gap/max(existed,1)*100):.0f}%**)."
    )
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(enforcement_gap_chart(df), use_container_width=True)
    with col2:
        gap_df = df.groupby("policy_enforced").agg(
            deaths=("deaths","sum"), displaced=("displaced","sum")
        ).reset_index()
        gap_df["label"] = gap_df["policy_enforced"].map({True:"Enforced", False:"Not enforced"})
        fig_gap = px.bar(gap_df, x="label", y="deaths", color="label",
                         color_discrete_map={"Enforced":"#4CAF50","Not enforced":"#FF3333"},
                         text="deaths")
        fig_gap.update_traces(textposition="outside")
        st.plotly_chart(dark_layout(fig_gap, "Deaths by Enforcement Status", 360),
                        use_container_width=True)

    fig_resp = px.box(df, x="severity", y="response_days", color="severity",
                      color_discrete_map={"Critical":"#FF3333","High":"#FF6B35",
                                          "Medium":"#FFB347","Low":"#4CAF50"},
                      category_orders={"severity":["Critical","High","Medium","Low"]})
    st.plotly_chart(dark_layout(fig_resp, "Response Days by Severity", 360),
                    use_container_width=True)
