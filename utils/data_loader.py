"""
Multi-city data loader for FloodWatch Kenya.

All pages load data through this module. Adding a new city requires only:
  1. Add entry to data/cities.json
  2. Create data/{city_id}/incidents.csv and policies.csv
  No code changes to this file or any page.
"""
from __future__ import annotations
import json
import pandas as pd
import streamlit as st
from pathlib import Path


@st.cache_data
def load_cities() -> list[dict]:
    with open("data/cities.json") as f:
        return json.load(f)["cities"]


def get_city(city_id: str) -> dict | None:
    return next((c for c in load_cities() if c["id"] == city_id), None)


@st.cache_data
def load_incidents(city_id: str) -> pd.DataFrame:
    city = get_city(city_id)
    if not city or not city.get("incidents_file"):
        return pd.DataFrame()
    path = Path(city["incidents_file"])
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, on_bad_lines='skip')
    # Coerce numeric columns — guards against string bleed after CSV requoting
    numeric_cols = ['deaths','displaced','infra_damage_ksh_m','response_days',
                    'budget_allocated_ksh_m','budget_utilized_pct','lives_saved_estimate']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df["city_id"]   = city_id
    df["city_name"] = city["name"]
    df["county"]    = city["county"]
    df["date"]      = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_policies(city_id: str) -> pd.DataFrame:
    city = get_city(city_id)
    if not city or not city.get("policies_file"):
        return pd.DataFrame()
    path = Path(city["policies_file"])
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, on_bad_lines='skip')
    # Coerce numeric columns — guards against string bleed after CSV requoting
    numeric_cols = ['deaths','displaced','infra_damage_ksh_m','response_days',
                    'budget_allocated_ksh_m','budget_utilized_pct','lives_saved_estimate']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df["city_id"]   = city_id
    df["city_name"] = city["name"]
    return df


@st.cache_data
def load_all_incidents() -> pd.DataFrame:
    """Load and concatenate incidents from all active cities."""
    frames = []
    for city in load_cities():
        if city["status"] == "active" and city.get("incidents_file"):
            df = load_incidents(city["id"])
            if not df.empty:
                frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


@st.cache_data
def load_all_policies() -> pd.DataFrame:
    """Load and concatenate policies from all active cities."""
    frames = []
    for city in load_cities():
        if city["status"] == "active" and city.get("policies_file"):
            df = load_policies(city["id"])
            if not df.empty:
                frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def active_cities() -> list[dict]:
    return [c for c in load_cities() if c["status"] == "active"]


def city_selector(label: str = "Select city", include_all: bool = True) -> str | None:
    """Streamlit selectbox returning city_id or 'all'."""
    cities = active_cities()
    options = (["all — Kenya overview"] if include_all else []) + [
        f"{c['name']} ({c['county']})" for c in cities
    ]
    selected = st.selectbox(label, options)
    if selected.startswith("all"):
        return "all"
    name = selected.split(" (")[0]
    city = next((c for c in cities if c["name"] == name), None)
    return city["id"] if city else None
