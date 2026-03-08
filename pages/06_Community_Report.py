"""FloodWatch NBI - Page 06: Community Report."""
from pathlib import Path
from datetime import datetime
import csv
import streamlit as st

st.set_page_config(page_title="Community Report - FloodWatch NBI", page_icon="report", layout="wide")
st.title("Report a Flood Incident")
st.markdown(
    "Submit a flood incident or infrastructure failure observation. "
    "Community reports supplement structural incident data — they are not automatically "
    "added to the main incident log without admin review."
)
st.caption(
    "Reports are stored in data/community_reports.csv (excluded from git). "
    "SMS gateway for offline submission planned — see HANDOFF.md section 6.5."
)

ROOT = Path(__file__).parent.parent
REPORTS_FILE = ROOT / "data" / "community_reports.csv"
FIELDNAMES = [
    "submitted_at", "reporter_type", "location", "lat_approx",
    "lon_approx", "severity_estimate", "incident_type",
    "description", "infra_failure", "contact_optional", "verified",
]

with st.form("report_form"):
    st.markdown("### Incident details")
    col1, col2 = st.columns(2)
    with col1:
        reporter_type = st.selectbox(
            "I am reporting as",
            ["Resident", "Community organiser", "NGO / CBO worker",
             "Journalist", "Local official", "Other"],
        )
        location = st.text_input("Location (estate, road, landmark)", placeholder="e.g. Mathare 4A near the bridge")
        severity = st.selectbox("Estimated severity",
            ["Critical — deaths or life threat", "High — major displacement",
             "Medium — property damage", "Low — minor flooding"])
    with col2:
        incident_type = st.selectbox(
            "Incident type",
            ["River overflow", "Flash flood", "Drainage failure",
             "Culvert blockage", "Riparian encroachment", "Other"],
        )
        infra_failure = st.multiselect(
            "Infrastructure failure observed",
            ["Blocked drainage", "Collapsed road", "Damaged bridge",
             "Flooded buildings", "No early warning", "No emergency response"],
        )
        contact = st.text_input("Contact (optional — for follow-up only)", placeholder="Phone or email")

    st.markdown("### Description")
    description = st.text_area(
        "What happened? Include time, approximate number of people affected, and any official response you observed.",
        height=120,
        placeholder="e.g. At approximately 3pm on Saturday the river burst banks near the footbridge. "
                    "About 200 people had to move. County vehicles arrived after 5 days."
    )

    st.markdown("### Approximate location (optional)")
    st.caption("Enter decimal degrees if known. Used to place report on the map after verification.")
    col3, col4 = st.columns(2)
    lat = col3.text_input("Latitude (decimal degrees)", placeholder="-1.259")
    lon = col4.text_input("Longitude (decimal degrees)", placeholder="36.860")

    submitted = st.form_submit_button("Submit report", type="primary")

if submitted:
    if not location or not description:
        st.error("Location and description are required.")
    else:
        row = {
            "submitted_at":    datetime.utcnow().isoformat(),
            "reporter_type":   reporter_type,
            "location":        location,
            "lat_approx":      lat or "",
            "lon_approx":      lon or "",
            "severity_estimate": severity,
            "incident_type":   incident_type,
            "description":     description,
            "infra_failure":   "; ".join(infra_failure),
            "contact_optional": contact,
            "verified":        "false",
        }
        write_header = not REPORTS_FILE.exists()
        REPORTS_FILE.parent.mkdir(exist_ok=True)
        with open(REPORTS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        st.success(
            "Report submitted. Thank you. "
            "It will be reviewed by the FloodWatch admin team before appearing on the map."
        )
        st.info(
            "**What happens next:** An admin will verify your report against other sources. "
            "If confirmed, it will be added to the incident map with source labelled 'Community'. "
            "Your contact details (if provided) will only be used for follow-up."
        )

st.divider()
st.markdown("### Cannot access the web form?")
st.markdown(
    "An SMS gateway for reporting via basic mobile is planned. "
    "Proposed keyword protocol: `FLOOD [LOCATION] [SEVERITY]` → send to shortcode. "
    "See HANDOFF.md section 6.5 for implementation notes."
)
