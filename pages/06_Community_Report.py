"""Page 6 — Community Report: citizen incident and infrastructure failure submission."""
import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(page_title="Community Report · FloodWatch NBI", page_icon="📣", layout="wide")
st.markdown("# 📣 Community Report")
st.markdown(
    "Submit a flood incident or infrastructure failure. "
    "Reports are reviewed before being added to the main incident map."
)
st.info(
    "**Privacy notice:** Location data you submit will be stored locally. "
    "Community reports are excluded from the public GitHub repository. "
    "This form requires web access — SMS gateway coming in a future release (see README § 6.5).",
)

tab1, tab2 = st.tabs(["Submit report", "View submitted reports"])

with tab1:
    st.markdown("### New incident report")
    with st.form("community_report"):
        col1, col2 = st.columns(2)
        with col1:
            r_date     = st.date_input("Date of incident", value=date.today())
            r_location = st.text_input("Location (estate / street name)", placeholder="e.g. Mathare Valley, near school")
            r_zone     = st.selectbox("Zone", ["Mathare","Kibera","Mukuru","Kasarani","Eastlands",
                                                "Westlands","Langata","Kajiado North","Other"])
            r_severity = st.selectbox("Severity", ["Critical","High","Medium","Low"])
            r_cause    = st.selectbox("Primary cause",
                                       ["River overflow","Flash flood","Drainage failure",
                                        "Blocked drain","Infrastructure failure","Other"])
        with col2:
            r_deaths     = st.number_input("Estimated deaths", min_value=0, value=0)
            r_displaced  = st.number_input("Estimated displaced persons", min_value=0, value=0)
            r_damage_ksh = st.number_input("Estimated damage (KSh millions, 0 if unknown)", min_value=0.0, value=0.0, step=0.5)
            r_infra      = st.selectbox("Infrastructure failure type",
                                         ["None","Blocked drain","Collapsed culvert","Overflowing manhole",
                                          "Eroded road","Burst pipe","Other"])
            r_policy     = st.selectbox("Was a relevant policy / restriction in place?",
                                         ["Unknown","Yes — not being enforced","Yes — being enforced","No relevant policy"])
        r_description = st.text_area("Description (optional)", height=100,
                                      placeholder="What happened? What infrastructure failed? What response did you observe?")
        r_reporter    = st.text_input("Your name or organisation (optional — for follow-up only)")
        submitted = st.form_submit_button("Submit report", type="primary")

    if submitted:
        if not r_location.strip():
            st.error("Location is required.")
        else:
            report = {
                "submitted_at": pd.Timestamp.now().isoformat(),
                "date": r_date.isoformat(),
                "location": r_location.strip(),
                "zone": r_zone,
                "severity": r_severity,
                "cause": r_cause,
                "deaths": int(r_deaths),
                "displaced": int(r_displaced),
                "infra_damage_ksh_m": float(r_damage_ksh),
                "infra_failure": r_infra,
                "policy_status": r_policy,
                "description": r_description.strip(),
                "reporter": r_reporter.strip(),
                "verified": False,
            }
            os.makedirs("data", exist_ok=True)
            reports_path = "data/community_reports.csv"
            if os.path.exists(reports_path):
                existing = pd.read_csv(reports_path)
                updated = pd.concat([existing, pd.DataFrame([report])], ignore_index=True)
            else:
                updated = pd.DataFrame([report])
            updated.to_csv(reports_path, index=False)
            st.success(
                f"Report submitted for **{r_location}** ({r_date}). "
                "Thank you. Reports are reviewed before appearing on the incident map."
            )

with tab2:
    reports_path = "data/community_reports.csv"
    if os.path.exists(reports_path):
        df = pd.read_csv(reports_path)
        if len(df) == 0:
            st.info("No community reports submitted yet.")
        else:
            st.metric("Total reports submitted", len(df))
            st.metric("Pending review", len(df[df["verified"] == False]))
            st.dataframe(
                df[["date","location","zone","severity","cause","deaths","displaced","verified"]]
                .sort_values("date", ascending=False).reset_index(drop=True),
                use_container_width=True,
                column_config={"verified": st.column_config.CheckboxColumn("Verified")}
            )
            st.caption("Verified reports will appear on the incident map in a future release (see README § 6.4).")
    else:
        st.info("No community reports submitted yet in this session.")

st.divider()
st.markdown("### SMS reporting (coming soon)")
st.markdown("""
The next version will accept reports via SMS using Africa's Talking:
```
FLOOD [LOCATION] [SEVERITY]
Send to: XXXXX
```
This removes the web access requirement for reporters in Mathare, Kibera, and Mukuru
where mobile data is metered. See [README § 6.5](https://github.com/gabrielmahia/floodwatch-nbi#65-sms--whatsapp-gateway-for-community-reports) for implementation plan.
""")
