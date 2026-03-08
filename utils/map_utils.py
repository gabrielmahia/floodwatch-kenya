"""Folium map builders for FloodWatch Kenya — multi-city aware."""
from __future__ import annotations
import folium
from folium.plugins import HeatMap
import pandas as pd

NAIROBI_CENTER = [-1.2921, 36.8219]
KENYA_CENTER   = [-0.5, 37.5]

# Riparian corridors per city — extend as real GIS data arrives
RIPARIAN_ZONES_BY_CITY = {
    "nairobi": {
        "Nairobi River":   [[-1.2631,36.7819],[-1.2678,36.7992],[-1.2714,36.8156],[-1.2745,36.8312],[-1.2789,36.8489],[-1.2823,36.8634],[-1.2856,36.8778]],
        "Mathare River":   [[-1.2456,36.8623],[-1.2534,36.8712],[-1.2601,36.8801],[-1.2638,36.8889],[-1.2689,36.8967]],
        "Ngong River":     [[-1.3156,36.7534],[-1.3189,36.7712],[-1.3212,36.7889],[-1.3245,36.8067],[-1.3267,36.8245]],
        "Gitathuru River": [[-1.2245,36.8834],[-1.2312,36.8901],[-1.2389,36.8967],[-1.2445,36.9034]],
    },
    "kisumu": {
        "Nyando River": [[-0.1400,34.7200],[-0.1200,34.7400],[-0.1000,34.7600],[-0.0800,34.7800]],
    },
    "mombasa": {
        "Tudor Creek": [[-4.0300,39.6600],[-4.0400,39.6700],[-4.0500,39.6800],[-4.0600,39.6900]],
    },
    "garissa": {
        "Tana River": [[-0.3000,39.5000],[-0.4000,39.6000],[-0.5000,39.7000],[-0.6000,39.8000],[-0.8000,39.9000],[-1.0000,40.0000]],
    },
    "budalangi": {
        "Nzoia River": [[0.2000,33.9000],[0.1800,33.9500],[0.1600,34.0000],[0.1400,34.0500],[0.1200,34.1000]],
    },
}

SEVERITY_ICON_COLORS = {
    "Critical":"red","High":"orange","Medium":"beige","Low":"green",
}

def _base_map(center=None, zoom=12, nation_view=False) -> folium.Map:
    if nation_view:
        center = KENYA_CENTER
        zoom   = 6
    elif center is None:
        center = NAIROBI_CENTER
    return folium.Map(
        location=center, zoom_start=zoom,
        tiles="CartoDB dark_matter", prefer_canvas=True,
    )

def _add_riparian(m, city_id=None):
    zones = RIPARIAN_ZONES_BY_CITY.get(city_id, {}) if city_id else {}
    if city_id is None:
        for city_zones in RIPARIAN_ZONES_BY_CITY.values():
            zones = {**zones, **city_zones}
    for river_name, coords in zones.items():
        folium.PolyLine(locations=coords, color="#4FC3F7", weight=3,
                        opacity=0.7, tooltip=f"{river_name} (riparian corridor)",
                        dash_array="8 4").add_to(m)

def build_incident_map(incidents_df: pd.DataFrame,
                       center=None, zoom=12,
                       city_id: str | None = None) -> folium.Map:
    nation_view = center == [-0.5, 37.5] or (len(incidents_df["city_id"].unique()) > 1
                                              if "city_id" in incidents_df.columns else False)
    m = _base_map(center=center, zoom=zoom, nation_view=nation_view)
    _add_riparian(m, city_id=None if nation_view else city_id)

    for _, row in incidents_df.iterrows():
        color = SEVERITY_ICON_COLORS.get(row["severity"], "gray")
        enforced_str = "✅ Enforced" if str(row.get("policy_enforced","")).lower()=="true" else "❌ Not enforced"
        existed_str  = "✅ Existed"  if str(row.get("policy_existed","")).lower()=="true"  else "❌ None"
        city_str = f"<br><span style='color:#888'>{row.get('city_name','')}</span>" if nation_view and "city_name" in row else ""

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:220px;color:#111">
          <b style="font-size:14px">{row["location"]}</b>{city_str}<br>
          <span style="color:#888">{row["date"] if hasattr(row["date"],"strftime") else row["date"]} · {row["zone"]}</span>
          <hr style="margin:4px 0">
          <b>Severity:</b> {row["severity"]}<br>
          <b>Deaths:</b> {row["deaths"]} · <b>Displaced:</b> {int(row["displaced"]):,}<br>
          <b>Cause:</b> {row["cause"]}<br>
          <b>Damage:</b> KSh {row["infra_damage_ksh_m"]}M · <b>Response:</b> {row["response_days"]}d<br>
          <hr style="margin:4px 0">
          <b>Policy existed:</b> {existed_str}<br>
          <b>Policy enforced:</b> {enforced_str}
        </div>"""

        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{row.get('city_name','') + ' · ' if nation_view and 'city_name' in row else ''}{row['severity']}: {row['location']}",
            icon=folium.Icon(color=color, icon="tint", prefix="fa"),
        ).add_to(m)
    return m


def build_risk_heatmap(incidents_df: pd.DataFrame,
                       center=None, zoom=12) -> folium.Map:
    nation_view = center == [-0.5, 37.5] or (len(incidents_df["city_id"].unique()) > 1
                                              if "city_id" in incidents_df.columns else False)
    m = _base_map(center=center, zoom=zoom, nation_view=nation_view)
    heat_data = []
    for _, row in incidents_df.iterrows():
        weight = row["deaths"] * 10 + row["displaced"] / 50
        heat_data.append([row["lat"], row["lon"], weight])
    HeatMap(heat_data, radius=25 if not nation_view else 18,
            blur=20, min_opacity=0.4,
            gradient={0.2:"#4FC3F7",0.5:"#FF6B35",0.8:"#FF3333",1.0:"#FFFFFF"}).add_to(m)
    return m
