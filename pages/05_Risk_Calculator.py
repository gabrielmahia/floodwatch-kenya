"""Page 5 — Risk Calculator: city-aware presets + composite flood risk scorer."""
import streamlit as st
from utils.charts import calculate_risk_score
from utils.data_loader import active_cities

st.set_page_config(page_title="Risk Calculator · FloodWatch Kenya", page_icon="🔧", layout="wide")

st.markdown("""
<style>
@media (max-width: 768px) {
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    [data-testid="stDataFrame"] { overflow-x: auto !important; }
    iframe { width: 100% !important; max-width: 100% !important; }
    .stButton > button { width: 100% !important; min-height: 48px !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔧 Site-Level Flood Risk Calculator")
st.markdown(
    "Estimate the composite flood risk for any location in Kenya. "
    "Select a city for representative presets, or enter custom values."
)
st.caption("Risk weights derived from WRMA flood hazard mapping methodology and JKUAT urban hydrology research. Calibration with county engineering departments ongoing.")

cities = active_cities()

# ── Known site presets ────────────────────────────────────────────────────────
KNOWN_SITES = {
    "Custom (enter below)": None,
    # Tier 1
    "Mathare Valley, Nairobi (critical)":     dict(population_density=480,drainage_coverage=12,distance_from_river_m=45, riparian_compliant=False,slope_pct=1.5,soil_permeability=0.25),
    "Kibera, Nairobi (critical)":             dict(population_density=420,drainage_coverage=18,distance_from_river_m=80, riparian_compliant=False,slope_pct=2.0,soil_permeability=0.30),
    "Garissa Township (critical)":            dict(population_density=180,drainage_coverage=15,distance_from_river_m=60, riparian_compliant=False,slope_pct=0.8,soil_permeability=0.20),
    "Budalangi Central (critical)":           dict(population_density=240,drainage_coverage=10,distance_from_river_m=30, riparian_compliant=False,slope_pct=0.5,soil_permeability=0.22),
    "Nyalenda, Kisumu (critical)":            dict(population_density=390,drainage_coverage=20,distance_from_river_m=50, riparian_compliant=False,slope_pct=1.2,soil_permeability=0.28),
    "Likoni, Mombasa (critical)":             dict(population_density=320,drainage_coverage=25,distance_from_river_m=40, riparian_compliant=False,slope_pct=1.5,soil_permeability=0.35),
    "Mandera Town (critical)":               dict(population_density=160,drainage_coverage=8, distance_from_river_m=35, riparian_compliant=False,slope_pct=0.6,soil_permeability=0.18),
    # Tier 2
    "Rhonda, Nakuru (high)":                  dict(population_density=200,drainage_coverage=28,distance_from_river_m=180,riparian_compliant=False,slope_pct=3.0,soil_permeability=0.40),
    "Langas, Eldoret (high)":                 dict(population_density=280,drainage_coverage=22,distance_from_river_m=90, riparian_compliant=False,slope_pct=2.5,soil_permeability=0.38),
    "Kericho Central (high)":                 dict(population_density=150,drainage_coverage=35,distance_from_river_m=200,riparian_compliant=True, slope_pct=8.0,soil_permeability=0.45),
    "Naivasha Kongoni (high)":               dict(population_density=130,drainage_coverage=30,distance_from_river_m=70, riparian_compliant=False,slope_pct=2.0,soil_permeability=0.42),
    # Low risk reference
    "Karen, Nairobi (low)":                   dict(population_density=12, drainage_coverage=78,distance_from_river_m=800,riparian_compliant=True, slope_pct=8.5,soil_permeability=0.72),
}

with st.sidebar:
    st.markdown("## Component weights")
    st.caption("Adjust as real calibration data improves.")
    st.markdown("- Population density: **25**")
    st.markdown("- Drainage gap: **20**")
    st.markdown("- River proximity: **25**")
    st.markdown("- Riparian violation: **15**")
    st.markdown("- Flat terrain: **10**")
    st.markdown("- Soil impermeability: **5**")
    st.divider()
    st.markdown("**Priority calibration partners:** JKUAT, UoN Civil Engineering, WRMA, NMK")
    st.divider()
    st.markdown("**Extension:** Connect to county planning approval databases to flag developments approved despite high risk scores.")

preset = st.selectbox("Load a known site", list(KNOWN_SITES.keys()))
preset_vals = KNOWN_SITES[preset] or {}

st.divider()
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Site parameters")
    population_density    = st.slider("Population density (persons/hectare)", 0, 800,
                                       preset_vals.get("population_density",150), step=10)
    drainage_coverage     = st.slider("Drainage coverage (%)", 0, 100,
                                       preset_vals.get("drainage_coverage",40))
    distance_from_river_m = st.slider("Distance from nearest river (metres)", 0, 2000,
                                       preset_vals.get("distance_from_river_m",300), step=25)
    riparian_compliant    = st.toggle("Riparian buffer compliant (30m setback)",
                                       value=preset_vals.get("riparian_compliant",True))
    slope_pct             = st.slider("Terrain slope (%)", 0.0, 30.0,
                                       float(preset_vals.get("slope_pct",5.0)), step=0.5)
    soil_permeability     = st.slider("Soil permeability (0=clay, 1=sandy)", 0.0, 1.0,
                                       float(preset_vals.get("soil_permeability",0.4)), step=0.05)

score = calculate_risk_score(
    population_density, drainage_coverage, distance_from_river_m,
    riparian_compliant, slope_pct, soil_permeability,
)

with col2:
    st.markdown("### Risk score")
    if   score >= 70: color,label,icon = "#FF3333","CRITICAL","🔴"
    elif score >= 50: color,label,icon = "#FF6B35","HIGH",    "🟠"
    elif score >= 30: color,label,icon = "#FFB347","MEDIUM",  "🟡"
    else:             color,label,icon = "#4CAF50","LOW",     "🟢"

    st.markdown(f"""
    <div style="background:#1A1F2E;border:2px solid {color};border-radius:8px;
                padding:32px;text-align:center;margin:16px 0">
      <div style="font-size:64px">{icon}</div>
      <div style="font-size:56px;font-weight:700;color:{color}">{score}</div>
      <div style="font-size:20px;color:{color}">{label} RISK</div>
    </div>""", unsafe_allow_html=True)

    components = [
        ("Population density",    min(population_density/500.0,1.0)*25,    25),
        ("Drainage gap",          max(0,(100-drainage_coverage)/100.0)*20, 20),
        ("River proximity",       max(0,1.0-distance_from_river_m/500.0)*25,25),
        ("Riparian violation",    (1.0 if not riparian_compliant else 0.0)*15,15),
        ("Flat terrain",          max(0,1.0-slope_pct/10.0)*10,            10),
        ("Soil impermeability",   (1.0-soil_permeability)*5,                5),
    ]
    for name, contribution, max_weight in components:
        pct = contribution/max_weight*100 if max_weight else 0
        bar_color = "#FF3333" if pct>70 else "#FF6B35" if pct>40 else "#4CAF50"
        st.markdown(f"""
        <div style="margin:6px 0">
          <div style="display:flex;justify-content:space-between;font-size:13px">
            <span>{name}</span><span style="color:{bar_color}">{contribution:.1f}/{max_weight}</span>
          </div>
          <div style="background:#2A2F3E;border-radius:4px;height:6px;margin-top:2px">
            <div style="background:{bar_color};width:{pct:.0f}%;height:6px;border-radius:4px"></div>
          </div>
        </div>""", unsafe_allow_html=True)

st.divider()
st.markdown("### Risk interpretation")
c1,c2 = st.columns(2)
with c1:
    st.markdown("""
| Score | Level | Action |
|-------|-------|--------|
| 0–29 | Low | Standard maintenance |
| 30–49 | Medium | Drainage upgrade + early warning |
| 50–69 | High | Resettlement assessment + drainage investment |
| 70–100 | Critical | Immediate flood risk management plan |
    """)
with c2:
    st.markdown("""
**Dominant driver → priority intervention:**
- River proximity dominant → riparian enforcement
- Drainage gap dominant → drainage infrastructure
- Density dominant → settlement upgrading (site and service)
- Riparian violation → NCC/county enforcement + NEMA action
- Applies across all 25 Kenyan cities in this platform
    """)
