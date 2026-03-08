"""Page 3 — Policy Tracker: 10 policies, budget utilisation, blocker taxonomy."""
import streamlit as st
import pandas as pd
from utils.charts import policy_status_sunburst, budget_gap_chart, blocker_treemap

st.set_page_config(page_title="Policy Tracker · FloodWatch NBI", page_icon="📋", layout="wide")
st.markdown("# 📋 Policy Tracker")
st.caption("⚠️ DEMO DATA — policies drawn from public NCC, NEMA, and World Bank documentation.")

@st.cache_data
def load(): return pd.read_csv("data/policies.csv")
df = load()

STATUS_COLORS = {
    "Completed": "#4CAF50", "Partially Implemented": "#FFB347",
    "Stalled": "#FF6B35", "Not Enforced": "#FF3333",
    "Not Started": "#9E9E9E", "Draft Only": "#607D8B",
}

with st.sidebar:
    st.markdown("## Filters")
    statuses = st.multiselect("Status", df["status"].unique().tolist(),
                               default=df["status"].unique().tolist())
    filt = df[df["status"].isin(statuses)]

lives_at_risk    = df[df["status"] != "Completed"]["lives_saved_estimate"].sum()
budget_allocated = df["budget_allocated_ksh_m"].sum()
budget_utilized  = (df["budget_allocated_ksh_m"] * df["budget_utilized_pct"] / 100).sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Policies tracked", len(df))
col2.metric("Not on track", len(df[df["status"].isin(["Stalled","Not Enforced","Not Started","Draft Only"])]))
col3.metric("Lives at risk (policy gap)", f"{lives_at_risk:,}")
col4.metric("Budget idle", f"KSh {budget_allocated - budget_utilized:.0f}M",
            delta=f"{round((1-budget_utilized/budget_allocated)*100,1)}% unspent",
            delta_color="inverse")

st.divider()
tab1, tab2, tab3 = st.tabs(["Policy Table", "Budget Analysis", "Blocker Taxonomy"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.plotly_chart(policy_status_sunburst(df), use_container_width=True)
    with col2:
        st.markdown("**What each status means**")
        for status, color in STATUS_COLORS.items():
            count = len(df[df["status"] == status])
            st.markdown(
                f'<span style="display:inline-block;width:12px;height:12px;'
                f'background:{color};border-radius:2px;margin-right:8px"></span>'
                f'**{status}** — {count} policies',
                unsafe_allow_html=True
            )

    st.divider()
    st.dataframe(
        filt[["policy_id","name","status","implementing_body","year_recommended",
              "budget_allocated_ksh_m","budget_utilized_pct","blocking_factor","lives_saved_estimate"
             ]].reset_index(drop=True),
        use_container_width=True,
        column_config={
            "budget_allocated_ksh_m": st.column_config.NumberColumn("Budget (KSh M)", format="%.0f"),
            "budget_utilized_pct":    st.column_config.ProgressColumn("Utilised %", min_value=0, max_value=100),
            "lives_saved_estimate":   st.column_config.NumberColumn("Lives at risk", format="%d"),
        }
    )

    selected_id = st.selectbox("View policy detail", filt["policy_id"].tolist())
    if selected_id:
        row = filt[filt["policy_id"] == selected_id].iloc[0]
        color = STATUS_COLORS.get(row["status"], "#888")
        st.markdown(f"""
        <div style="background:#1A1F2E;border-left:4px solid {color};padding:16px;border-radius:4px">
          <h4 style="margin:0 0 8px 0">{row["name"]}</h4>
          <p><b>Status:</b> <span style="color:{color}">{row["status"]}</span> &nbsp;|&nbsp;
             <b>Since:</b> {row["year_recommended"]} &nbsp;|&nbsp;
             <b>Implementing body:</b> {row["implementing_body"]}</p>
          <p><b>Budget:</b> KSh {row["budget_allocated_ksh_m"]:.0f}M allocated,
             {row["budget_utilized_pct"]:.0f}% utilised</p>
          <p><b>Primary blocker:</b> {row["blocking_factor"]}</p>
          <p><b>Lives at risk if unresolved:</b> {int(row["lives_saved_estimate"]):,}</p>
          <p style="color:#aaa"><b>Source:</b> {row["source"]}</p>
          <p style="color:#ccc">{row["notes"]}</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.plotly_chart(budget_gap_chart(df), use_container_width=True)
    st.markdown("""
    **Key insight:** Budget absorption is a critical failure mode distinct from budget allocation.
    Several policies have been allocated significant funds but demonstrate <15% utilisation.
    This reflects contracting delays, resettlement cost shortfalls, and inter-agency coordination
    failures — not funding scarcity.
    """)

with tab3:
    st.plotly_chart(blocker_treemap(df), use_container_width=True)
    blocker_df = df[df["status"] != "Completed"].copy()
    blocker_df["short_blocker"] = blocker_df["blocking_factor"].str.split(" and ").str[0].str.split(",").str[0]
    blocker_summary = blocker_df.groupby("short_blocker").agg(
        policies=("policy_id","count"), lives_at_risk=("lives_saved_estimate","sum")
    ).sort_values("lives_at_risk", ascending=False).reset_index()
    st.markdown("**Blocking factor summary**")
    st.dataframe(blocker_summary, use_container_width=True,
                 column_config={"lives_at_risk": st.column_config.NumberColumn("Lives at risk", format="%d")})
