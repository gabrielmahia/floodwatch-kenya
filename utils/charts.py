"""
FloodWatch NBI — Plotly chart builders and risk calculator.

All figures use a shared dark theme via dark_layout().
No global state — every function takes its data as arguments.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Shared theme ────────────────────────────────────────────────

BG        = "#0F172A"
CARD_BG   = "#1E293B"
TEXT      = "#F1F5F9"
MUTED     = "#94A3B8"
RED       = "#EF4444"
ORANGE    = "#F97316"
YELLOW    = "#EAB308"
GREEN     = "#22C55E"
BLUE      = "#3B82F6"
PURPLE    = "#A855F7"

SEVERITY_COLORS = {
    "Critical": RED,
    "High":     ORANGE,
    "Medium":   YELLOW,
    "Low":      GREEN,
}

STATUS_COLORS = {
    "Completed":               GREEN,
    "Partially Implemented":   BLUE,
    "Stalled":                 YELLOW,
    "Not Enforced":            ORANGE,
    "Not Started":             RED,
    "Draft Only":              PURPLE,
}


def dark_layout(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    """Apply consistent dark theme to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(color=TEXT, size=14), x=0),
        paper_bgcolor=BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="monospace"),
        height=height,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor=BG, bordercolor=CARD_BG),
        xaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        yaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
    )
    return fig


# ── Risk calculator ─────────────────────────────────────────────

def calculate_risk_score(
    population_density: float,      # persons/hectare
    drainage_coverage: float,       # % 0–100
    distance_from_river_m: float,   # metres
    riparian_compliant: bool,       # True = compliant = lower risk
    slope_pct: float,               # % gradient
    soil_permeability: float,       # 0.0 (clay) to 1.0 (sandy)
) -> float:
    """Compute composite flood risk score (0–100).

    Component weights (sum = 100):
      Density penalty     25 — high density increases exposure
      Drainage gap        20 — low coverage increases inundation risk
      River proximity     25 — distance decay from flood corridor
      Riparian violation  15 — direct riparian encroachment
      Terrain flatness    10 — flat terrain reduces runoff speed
      Soil impermeability  5 — clay soils increase surface water

    Returns: float in [0, 100] where 100 = maximum risk.
    """
    # Density (0–25): scale 0–500 persons/ha → 0–25
    density_score = min(population_density / 500, 1.0) * 25

    # Drainage gap (0–20): gap = 100 - coverage
    drainage_score = (1 - min(drainage_coverage, 100) / 100) * 20

    # River proximity (0–25): decay from 0m (max risk) to 500m+ (zero)
    proximity_score = max(0, 1 - distance_from_river_m / 500) * 25

    # Riparian violation (0–15): non-compliant = full penalty
    riparian_score = 15 if riparian_compliant else 0

    # Terrain flatness (0–10): flat (0% slope) = max penalty
    terrain_score = max(0, 1 - slope_pct / 20) * 10

    # Soil (0–5): clay (0.0) = max impermeability penalty
    soil_score = (1 - min(soil_permeability, 1.0)) * 5

    raw = density_score + drainage_score + proximity_score + riparian_score + terrain_score + soil_score
    return round(min(max(raw, 0), 100), 1)


def risk_gauge(score: float) -> go.Figure:
    """Gauge chart for a single risk score."""
    if score >= 70:
        color = RED
        label = "CRITICAL"
    elif score >= 50:
        color = ORANGE
        label = "HIGH"
    elif score >= 30:
        color = YELLOW
        label = "MEDIUM"
    else:
        color = GREEN
        label = "LOW"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"color": color, "size": 36, "family": "monospace"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": MUTED, "tickfont": {"color": MUTED}},
            "bar":  {"color": color},
            "bgcolor": CARD_BG,
            "steps": [
                {"range": [0,  30], "color": "#14532D"},
                {"range": [30, 50], "color": "#713F12"},
                {"range": [50, 70], "color": "#7C2D12"},
                {"range": [70, 100], "color": "#450A0A"},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "value": score},
        },
        title={"text": f"Composite Risk Score — {label}", "font": {"color": TEXT, "size": 13}},
    ))
    fig.update_layout(paper_bgcolor=BG, font={"color": TEXT}, height=300,
                      margin=dict(l=20, r=20, t=40, b=10))
    return fig


# ── Incident charts ─────────────────────────────────────────────

def flood_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """Scatter: time × displaced, bubble size = deaths, colour = severity."""
    fig = px.scatter(
        df,
        x="date", y="displaced",
        size="deaths", color="severity",
        color_discrete_map=SEVERITY_COLORS,
        hover_data=["location", "cause", "response_days", "policy_enforced"],
        labels={"displaced": "Persons Displaced", "date": ""},
        size_max=40,
    )
    dark_layout(fig, "Flood Timeline — Displacement & Deaths", 380)
    return fig


def zone_impact_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: displaced + deaths by zone."""
    zone = df.groupby("zone").agg(
        total_displaced=("displaced", "sum"),
        total_deaths=("deaths", "sum"),
        incidents=("date", "count"),
    ).reset_index().sort_values("total_displaced", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=zone["zone"], x=zone["total_displaced"],
        name="Displaced", orientation="h",
        marker_color=ORANGE, opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        y=zone["zone"], x=zone["total_deaths"] * 100,
        name="Deaths ×100", orientation="h",
        marker_color=RED, opacity=0.85,
    ))
    dark_layout(fig, "Impact by Zone", 380)
    fig.update_layout(barmode="overlay")
    return fig


def enforcement_gap_chart(df: pd.DataFrame) -> go.Figure:
    """Bar: incidents grouped by policy_existed × policy_enforced."""
    df = df.copy()
    df["status"] = df.apply(lambda r: (
        "Policy enforced" if r["policy_existed"] and r["policy_enforced"] else
        "Policy existed, not enforced" if r["policy_existed"] else
        "No policy existed"
    ), axis=1)
    counts = df.groupby("status").agg(
        incidents=("date", "count"),
        deaths=("deaths", "sum"),
        displaced=("displaced", "sum"),
    ).reset_index()

    COLOR_MAP = {
        "Policy enforced":             GREEN,
        "Policy existed, not enforced": ORANGE,
        "No policy existed":            RED,
    }
    fig = px.bar(counts, x="status", y="incidents",
                 color="status", color_discrete_map=COLOR_MAP,
                 text="deaths",
                 labels={"incidents": "Incidents", "status": ""},
                 hover_data=["displaced"])
    fig.update_traces(texttemplate="%{text} deaths", textposition="outside")
    dark_layout(fig, "The Enforcement Gap — Policy vs Reality", 360)
    fig.update_layout(showlegend=False)
    return fig


def seasonality_chart(df: pd.DataFrame) -> go.Figure:
    """Bar: incident count + deaths by month."""
    df = df.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%b")
    df["month_num"] = pd.to_datetime(df["date"]).dt.month
    monthly = df.groupby(["month", "month_num"]).agg(
        incidents=("date", "count"),
        deaths=("deaths", "sum"),
    ).reset_index().sort_values("month_num")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly["month"], y=monthly["incidents"],
        name="Incidents", marker_color=BLUE, opacity=0.7,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly["month"], y=monthly["deaths"],
        name="Deaths", mode="lines+markers",
        line=dict(color=RED, width=2),
        marker=dict(size=8),
    ), secondary_y=True)
    dark_layout(fig, "Seasonality — Long Rains (Mar–May) and Short Rains (Oct–Dec)", 360)
    fig.update_yaxes(title_text="Incidents", secondary_y=False, gridcolor="#334155")
    fig.update_yaxes(title_text="Deaths", secondary_y=True, gridcolor="#334155")
    return fig


def cause_treemap(df: pd.DataFrame) -> go.Figure:
    """Treemap: cause → severity → displaced."""
    fig = px.treemap(
        df, path=["cause", "severity"],
        values="displaced", color="deaths",
        color_continuous_scale=["#1E293B", RED],
        labels={"displaced": "Displaced", "deaths": "Deaths"},
    )
    fig.update_layout(paper_bgcolor=BG, font=dict(color=TEXT), height=380,
                      margin=dict(l=0, r=0, t=30, b=0))
    return fig


# ── Policy charts ───────────────────────────────────────────────

def policy_status_donut(df: pd.DataFrame) -> go.Figure:
    """Donut: policy status distribution."""
    counts = df["status"].value_counts().reset_index()
    counts.columns = ["status", "count"]
    colors = [STATUS_COLORS.get(s, MUTED) for s in counts["status"]]

    fig = go.Figure(go.Pie(
        labels=counts["status"], values=counts["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=BG, width=2)),
        textinfo="label+value",
        textfont=dict(color=TEXT, size=11),
    ))
    implemented = df[df["status"] == "Completed"].shape[0]
    fig.add_annotation(
        text=f"{implemented}/{len(df)}<br><span style='font-size:10px'>Completed</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color=GREEN if implemented > 2 else RED),
    )
    dark_layout(fig, "Policy Implementation Status", 360)
    fig.update_layout(showlegend=False)
    return fig


def budget_gap_chart(df: pd.DataFrame) -> go.Figure:
    """Stacked bar: allocated vs utilised budget per policy."""
    df = df.sort_values("budget_allocated_ksh_m", ascending=True)
    utilized = df["budget_allocated_ksh_m"] * df["budget_utilized_pct"] / 100
    gap       = df["budget_allocated_ksh_m"] - utilized

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["name"].str[:40], x=utilized,
        name="Utilised", orientation="h",
        marker_color=GREEN, opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        y=df["name"].str[:40], x=gap,
        name="Unspent", orientation="h",
        marker_color=RED, opacity=0.6,
    ))
    dark_layout(fig, "Budget Allocation vs Utilisation (KSh M)", 480)
    fig.update_layout(barmode="stack")
    return fig


def blocking_factor_bar(df: pd.DataFrame) -> go.Figure:
    """Bar: blocker taxonomy frequency."""
    # Extract primary blocker category (first phrase before em-dash)
    df = df[df["status"] != "Completed"].copy()
    df["blocker_short"] = df["blocking_factor"].str.split(" — ").str[0].str.strip()
    counts = df["blocker_short"].value_counts().reset_index()
    counts.columns = ["blocker", "count"]

    fig = px.bar(counts, x="count", y="blocker", orientation="h",
                 color="count", color_continuous_scale=[BLUE, RED],
                 labels={"count": "Policies blocked", "blocker": ""})
    dark_layout(fig, "What Is Blocking Implementation?", 320)
    fig.update_layout(coloraxis_showscale=False)
    return fig


def lives_at_risk_bar(df: pd.DataFrame) -> go.Figure:
    """Bar: lives saved estimate by policy, coloured by status."""
    df = df[df["status"] != "Completed"].sort_values("lives_saved_estimate", ascending=True)
    colors = [STATUS_COLORS.get(s, MUTED) for s in df["status"]]

    fig = go.Figure(go.Bar(
        y=df["name"].str[:38], x=df["lives_saved_estimate"],
        orientation="h",
        marker_color=colors,
        text=df["status"],
        textposition="outside",
    ))
    dark_layout(fig, "Lives Saved if Fully Implemented — Unimplemented Policies", 480)
    return fig


# ── City benchmark charts ───────────────────────────────────────

def resilience_radar(cities: list[dict], selected: list[str]) -> go.Figure:
    """Polar radar comparing selected cities across 5 resilience dimensions."""
    DIMS = [
        ("riparian_compliance_pct", "Riparian
Compliance %"),
        ("drainage_coverage_pct",   "Drainage
Coverage %"),
        ("early_warning_hours",     "Early Warning
(hrs, capped 72)"),
        ("flood_budget_usd_per_capita", "Budget
USD/capita"),
        ("resilience_score",        "Overall
Score"),
    ]

    # Normalise each dimension to 0–100
    def norm(cities_data, key, cap=None):
        vals = [c[key] for c in cities_data]
        mx = cap if cap else max(vals)
        return {c["name"]: min(c[key] / mx * 100, 100) for c in cities_data}

    norms = {
        "riparian_compliance_pct":    norm(cities, "riparian_compliance_pct"),
        "drainage_coverage_pct":      norm(cities, "drainage_coverage_pct"),
        "early_warning_hours":        norm(cities, "early_warning_hours", cap=72),
        "flood_budget_usd_per_capita":norm(cities, "flood_budget_usd_per_capita"),
        "resilience_score":           norm(cities, "resilience_score"),
    }

    COLORS = [RED, BLUE, GREEN, ORANGE, PURPLE, YELLOW]
    labels = [d[1] for d in DIMS]

    fig = go.Figure()
    for i, city in enumerate([c for c in cities if c["name"] in selected]):
        vals = [norms[d[0]][city["name"]] for d in DIMS]
        vals.append(vals[0])  # close the polygon
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=labels + [labels[0]],
            name=city["name"],
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            fill="toself",
            fillcolor=COLORS[i % len(COLORS)],
            opacity=0.15,
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=CARD_BG,
            radialaxis=dict(visible=True, range=[0, 100], color=MUTED, gridcolor="#334155"),
            angularaxis=dict(color=TEXT, gridcolor="#334155"),
        ),
        paper_bgcolor=BG,
        font=dict(color=TEXT, family="monospace"),
        height=420,
        legend=dict(bgcolor=BG),
        margin=dict(l=40, r=40, t=40, b=40),
        title=dict(text="City Resilience Radar (normalised dimensions)", font=dict(color=TEXT, size=13)),
    )
    return fig


def resilience_scatter(cities: list[dict]) -> go.Figure:
    """Scatter: budget per capita × deaths per event, size = population."""
    fig = px.scatter(
        cities,
        x="flood_budget_usd_per_capita",
        y="deaths_per_event_avg",
        size="population_m",
        color="resilience_score",
        color_continuous_scale=["#450A0A", YELLOW, GREEN],
        hover_name="name",
        hover_data=["country", "resilience_score", "key_intervention"],
        labels={
            "flood_budget_usd_per_capita": "Flood Budget (USD/capita)",
            "deaths_per_event_avg":        "Deaths per Flood Event (avg)",
            "resilience_score":            "Resilience Score",
        },
        size_max=50,
        text="name",
    )
    fig.update_traces(textposition="top center")
    dark_layout(fig, "Budget vs Deaths — The Investment Curve", 420)
    fig.update_layout(coloraxis_colorbar=dict(title="Resilience<br>Score", tickfont=dict(color=TEXT)))
    return fig
