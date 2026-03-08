# FloodWatch NBI

**Urban flood resilience intelligence for Nairobi — incident tracking, policy accountability, city benchmarks.**

[![CI](https://github.com/gabrielmahia/floodwatch-nbi/actions/workflows/ci.yml/badge.svg)](https://github.com/gabrielmahia/floodwatch-nbi/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://floodwatch-nbi.streamlit.app)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey)](LICENSE)

⚠️ **DEMO DATA** — All incident and policy records are representative samples drawn from public documentation. See § 12 for real data sources.

---

## What this is

Nairobi floods repeatedly. The policy instruments to address this largely exist. The problem is an **enforcement and accountability gap**, not a knowledge gap. This platform makes that gap visible and measurable.

The design deliberately centres political economy over hydrology — tracking *who failed to act* and *what blocked them*, not just *where water went*.

---

## Quick start

```bash
git clone https://github.com/gabrielmahia/floodwatch-nbi
cd floodwatch-nbi
pip install -r requirements.txt
streamlit run app.py
```

Or deploy directly: [share.streamlit.io](https://share.streamlit.io) → New app → point to `app.py`.

---

## Pages

| Page | What it shows |
|------|--------------|
| **Landing** | Alert banner, KPI summary, enforcement gap overview |
| **Incident Map** | Folium dark map — severity markers, river corridors, risk heatmap |
| **Impact Analysis** | Timeline, zone breakdowns, seasonal patterns, enforcement gap charts |
| **Policy Tracker** | 10 policies — budget utilisation, blocking factors, lives at risk |
| **City Benchmarks** | Radar + scatter: Nairobi vs Medellin, Rotterdam, Jakarta, Dhaka, Singapore |
| **Risk Calculator** | Site-level composite flood risk scorer (0–100) |
| **Community Report** | Citizen incident submission form with CSV persistence |

---

## Risk calculator

Composite score formula (component weights):

| Component | Weight | Notes |
|-----------|--------|-------|
| Population density | 25% | Per hectare, 0–500 normalised |
| Drainage gap | 20% | (100 - coverage%) |
| River proximity | 25% | 0–500m band |
| Riparian violation | 15% | Non-compliant adds full weight |
| Flat terrain | 10% | Slope < 10% |
| Soil impermeability | 5% | Clay = 1.0, sandy = 0.0 |

Weights are indicative. Calibrate against actual Nairobi hydrology data (JKUAT/UoN civil engineering partnership recommended).

---

## Extension priorities

### 6.1 Real-time rainfall
Replace the hardcoded alert banner with live KMD API or OpenWeatherMap data:
```python
def get_rainfall_alert():
    # Call api.meteo.go.ke or OpenWeatherMap Nairobi basin
    # Return: None | "watch" | "warning" | "emergency"
    pass
```

### 6.2 WRMA river level alerts
Add gauge data from Nairobi River, Mathare, Ngong, Athi. Threshold: gauge > 80% of flood stage = orange; > 100% = red.

### 6.3 Ward-level choropleth
Nairobi has 85 wards, each with a sitting MCA. Ward-level data makes political accountability concrete.
GeoJSON: Kenya Open Data Portal, Humanitarian Data Exchange (HDX).

### 6.4 Community report → map pipeline
Close the loop: verified community reports appear on the incident map with a different marker style.

### 6.5 SMS gateway for community reports
Remove the web access barrier for Mathare/Kibera/Mukuru reporters:
- Africa's Talking SMS API (free tier, Kenyan numbers)
- Keyword protocol: `FLOOD [LOCATION] [SEVERITY]`
- Uses [kenya-sms](https://github.com/gabrielmahia/kenya-sms) library

### 6.6 Policy status notifications
Add `last_updated` to policies.csv + subscriber email alerts when policy status changes.

### 6.7 Developer impact assessment
Connect risk calculator to NCC planning approval database — flag approved developments with high risk scores.

---

## Data sources

| Source | What it provides | Access |
|--------|-----------------|--------|
| Kenya Meteorological Department | Rainfall, forecasts | api.meteo.go.ke |
| WRMA | River gauge levels | Email / open data |
| Nairobi City County | Incident reports, drainage maps | FOIA / open data |
| NDOC | Disaster declarations, response logs | Public reports |
| Kenya Open Data Portal | Ward boundaries, census | opendata.go.ke |
| HDX | Settlement boundaries, vulnerability | data.humdata.org |
| UNHABITAT Nairobi | Informal settlement profiles | unhabitat.org |
| Akiba Mashinani Trust | Mukuru-specific community data | Direct partnership |

---

## Design principles

**The enforcement gap is the story.** Every feature should connect back to the distance between policy existence and policy implementation.

**Name the blockers, not just the outcomes.** A chart showing flood deaths is less useful than a chart showing which decisions and which actors produced those deaths.

**Medellin is the analogue, not Rotterdam.** A messy, under-resourced city that made progress through political will and community ownership — not a wealthy country with 70 years of consensus.

---

## Database migration path

Current: flat CSV files (works to ~500 community reports).
Recommended migration: **Supabase** (PostgreSQL, free tier, row-level security).

```python
from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)
incidents = client.table("incidents").select("*").execute().data
```

Store credentials in `.streamlit/secrets.toml`.

---

*Part of the [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack) East Africa engineering ecosystem.*
*Inspired by OpenResilience Kenya, Rotterdam Delta Programme, 100 Resilient Cities.*
*Maintained by [Gabriel Mahia](https://github.com/gabrielmahia). Kenya × USA.*
