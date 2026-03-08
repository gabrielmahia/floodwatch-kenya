# FloodWatch Kenya

**Flood resilience intelligence across Kenya — incident tracking, policy accountability, enforcement gap analysis.**

[![CI](https://github.com/gabrielmahia/floodwatch-kenya/actions/workflows/ci.yml/badge.svg)](https://github.com/gabrielmahia/floodwatch-kenya/actions)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://floodwatch-kenya.streamlit.app)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey)](LICENSE)

⚠️ **DEMO DATA** — Nairobi incident and policy records are representative samples. See § 12 for real data sources.

**Active:** Nairobi · **In development:** Kisumu · Mombasa · Nakuru · Garissa

---

## The problem this addresses

Kenya's flood deaths are not primarily a knowledge problem or a funding problem. They are an **enforcement and accountability gap**. The policies exist. The responsible bodies are named. The budgets, in many cases, have been allocated. The gap is between what has been decided and what has been done — and that gap has specific actors, specific blocking factors, and specific political economy explanations.

This platform makes that gap visible, measurable, and attributable.

---

## Kenya flood typology map

Each city faces a structurally different flood problem requiring a different institutional response:

| City | Typology | Core gap | Status |
|------|----------|----------|--------|
| **Nairobi** | Urban drainage + riparian encroachment | Enforcement — riparian land has commercial value, NCC avoids pre-election evictions | 🟢 Active |
| **Kisumu** | Lake Victoria basin rise + riverine | Monitoring — early warning must key to lake gauge levels, not local rainfall | ⚪ Coming soon |
| **Mombasa** | Coastal storm surge + urban drainage | Climate — sea level rise trajectory makes parts of Mombasa Island permanently uninsurable by 2060 | ⚪ Coming soon |
| **Nakuru** | Endorheic lake level rise (no outlet) | Policy — no managed retreat framework exists; conventional flood management does not apply | ⚪ Coming soon |
| **Garissa** | Tana River riverine + pastoral | Last-mile — early warning exists but cannot reach dispersed pastoral settlements | ⚪ Coming soon |

The typology diversity is analytically important. A drainage infrastructure solution correct for Nairobi is irrelevant for Nakuru (endorheic basin, no outlet). An early warning system designed for Mombasa's coastal exposure fails in Garissa where the flood is driven by distant upstream rainfall on Mt Kenya. The platform captures this variation rather than flattening it.

---

## Quick start

```bash
git clone https://github.com/gabrielmahia/floodwatch-kenya
cd floodwatch-kenya
pip install -r requirements.txt
streamlit run app.py
```

Deploy: [share.streamlit.io](https://share.streamlit.io) → New app → `app.py`

---

## Architecture

```
data/
  cities.json          ← City registry: typology, map config, institutional context
  incidents.csv        ← Nairobi flood events (active)
  policies.csv         ← Nairobi policy tracker (active)
  city_benchmarks.json ← 6-city international comparison
  nairobi/             ← Future: city-scoped data as others activate
  kisumu/              ← Placeholder: add incidents.csv + policies.csv to activate
  mombasa/             ← Placeholder
  nakuru/              ← Placeholder
  garissa/             ← Placeholder

app.py                 ← Landing page: city map, typology explainer, Nairobi KPIs
pages/
  01_Incident_Map.py   ← Folium dark map, filters, incident log
  02_Impact_Analysis.py ← Timeline, zones, enforcement gap charts
  03_Policy_Tracker.py  ← Budget, blockers, lives at risk
  04_City_Benchmarks.py ← International radar + scatter
  05_Risk_Calculator.py ← Composite site-level risk score
  06_Community_Report.py ← Citizen submission form

utils/
  charts.py            ← All Plotly figures + calculate_risk_score()
  map_utils.py         ← Folium builders (city-configurable)
```

**Adding a new city** when data becomes available:
1. Add `data/{city_id}/incidents.csv` and `data/{city_id}/policies.csv`
2. Set `"data_available": true` and `"status": "active"` in `data/cities.json`
3. Update `map_utils.py` with city-specific river corridors and vulnerable zones
4. Update `"incidents_file"` and `"policies_file"` paths in cities.json

---

## Pages

| Page | What it shows |
|------|--------------|
| **Landing** | Kenya city typology map, alert banner, Nairobi KPI summary |
| **Incident Map** | Folium dark map — severity markers, river corridors, risk heatmap |
| **Impact Analysis** | Timeline, zone breakdowns, seasonal patterns, enforcement gap |
| **Policy Tracker** | Budget utilisation, blocking factors, lives at risk from stalled policies |
| **City Benchmarks** | Nairobi vs Medellin, Rotterdam, Jakarta, Dhaka, Singapore |
| **Risk Calculator** | Site-level composite flood risk scorer (0–100) |
| **Community Report** | Citizen incident submission with CSV persistence |

---

## Risk calculator

Composite score (0–100) with documented weights:

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Population density | 25% | More people in path = higher risk |
| Drainage gap | 20% | (100 - coverage%) |
| River proximity | 25% | 0–500m band |
| Riparian violation | 15% | Non-compliance adds full weight |
| Flat terrain | 10% | Low slope = water pools |
| Soil impermeability | 5% | Clay soils increase runoff |

Weights are indicative — not calibrated to Nairobi hydrology. Calibration path: JKUAT or University of Nairobi civil engineering department.

---

## Extension priorities

### Real-time rainfall (§ 6.1)
Replace hardcoded alert banner with live KMD API or OpenWeatherMap:
```python
def get_rainfall_alert():
    # api.meteo.go.ke — registration required
    # Returns: None | "watch" | "warning" | "emergency"
    pass
```

### Lake gauge alerts for Kisumu (§ 6.2)
WRMA monitors Lake Victoria levels. Threshold: gauge > 80% of flood stage = orange, > 100% = red. Different architecture from rainfall-based warnings — requires gauge polling, not weather API.

### Ward-level choropleth (§ 6.3)
Nairobi has 85 wards, each with a sitting MCA. Ward-level data makes accountability concrete and nameable. GeoJSON: Kenya Open Data Portal, HDX.

### SMS gateway for community reports (§ 6.5)
Remove the web access barrier for Mathare, Kibera, Mukuru reporters. Uses [kenya-sms](https://github.com/gabrielmahia/kenya-sms):
```
FLOOD [LOCATION] [SEVERITY]
Send to: XXXXX (Africa's Talking shortcode)
```

### Kisumu activation
Priority next city. Data requirements:
- WRMA Lake Victoria gauge history (2019–present)
- Kisumu County flood incident reports
- Nyando River Authority drainage records
Contact: Kisumu County Disaster Management Unit, WRMA Nyanza Region office

### Garissa SMS early warning integration
Garissa is the test case for the hardest problem: last-mile early warning to pastoral communities without smartphones. Kenya-sms + Africa's Talking + a simple keyword protocol (`FLOOD BURA HIGH`) could reach community leaders who relay alerts on foot.

---

## Data sources

| Source | What it provides | Access |
|--------|-----------------|--------|
| Kenya Meteorological Department | Rainfall, forecasts | api.meteo.go.ke |
| WRMA | River/lake gauge levels, basin data | Email request |
| Nairobi City County | Incident reports, drainage maps | FOIA / open data |
| NDOC | Disaster declarations, response logs | Public reports |
| Kenya Open Data Portal | Ward boundaries, census | opendata.go.ke |
| HDX (Humanitarian Data Exchange) | Settlement boundaries, vulnerability | data.humdata.org |
| UNHABITAT Nairobi | Informal settlement profiles | unhabitat.org |
| Akiba Mashinani Trust | Mukuru-specific community data | Direct partnership |
| Kisumu County DMU | Kisumu incident records | Direct request |
| TANA Water Works | Tana River gauge data | Direct request |
| Kenya Red Cross | Situation reports by county | krcs.or.ke |

---

## Design principles

**The enforcement gap is the story.** Every feature connects back to the distance between policy existence and policy implementation. Resist adding features that aestheticise the problem without naming accountability.

**Each city's flood typology is distinct.** Do not generalise a Nairobi drainage solution to Nakuru (endorheic) or Garissa (riverine/pastoral). The platform captures variation rather than flattening it.

**Medellin is the analogue, not Rotterdam.** A messy, under-resourced city that made progress through political will and community ownership. Keep Dhaka as the warning.

**Community data supplements structural analysis.** The report form creates accountability pressure — it is not a replacement for rigorous incident data from NCC and NDOC.

**Name the blockers, not just the outcomes.** A chart of flood deaths is less useful than a chart showing which decisions produced them.

---

## Database migration path

Current: flat CSV files (suitable to ~500 community reports, single concurrent user).
Next: **Supabase** (PostgreSQL, free tier, row-level security per county).

```python
from supabase import create_client
client = create_client(SUPABASE_URL, SUPABASE_KEY)
incidents = client.table("nairobi_incidents").select("*").execute().data
```

Secrets in `.streamlit/secrets.toml` (Streamlit Cloud native secret management).

---

## Known limitations

| Limitation | Impact | Fix |
|-----------|--------|-----|
| 15 Nairobi incidents (sampled) | Understates true scale | Integrate NCC/NDOC incident logs |
| Nairobi only (4 cities placeholder) | Platform claim not yet matched by data | Activate Kisumu next |
| Risk weights not calibrated | Score is indicative | JKUAT/UoN civil engineering partnership |
| Folium river geometry approximate | Riparian corridors not precise | Load actual WRMA GIS data |
| Community reports unverified | Noise risk | Add admin review queue |

---

*Part of the [nairobi-stack](https://github.com/gabrielmahia/nairobi-stack) East Africa engineering ecosystem.*
*Inspired by OpenResilience Kenya, Rotterdam Delta Programme, 100 Resilient Cities, Medellin urban acupuncture.*
*Maintained by [Gabriel Mahia](https://github.com/gabrielmahia). Kenya × USA.*
