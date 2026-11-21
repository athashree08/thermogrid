"""
ThermoGrid — Metrics Calculation Engine
Computes dynamic summary statistics, city aggregations, and geohash KPIs
directly from processed weather datasets.
"""

from typing import Any, Dict
import pandas as pd


def compute_overview_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate high-level KPI metrics across the active observation dataset.
    """
    if df.empty:
        return {
            "total_observations": 0,
            "monitored_cities": 0,
            "latest_timestamp": "N/A",
            "avg_temperature": 0.0,
            "min_temperature": 0.0,
            "max_temperature": 0.0,
            "avg_humidity": 0.0,
            "total_precipitation": 0.0,
            "avg_wind_speed": 0.0,
        }

    total_obs = len(df)
    cities_count = df["city"].nunique() if "city" in df.columns else (df["geohash"].nunique() if "geohash" in df.columns else 0)

    latest_ts = df["timestamp"].max()
    latest_ts_str = latest_ts.strftime("%Y-%m-%d %H:%M UTC") if pd.notnull(latest_ts) else "N/A"

    avg_temp = float(df["temperature_c"].mean()) if "temperature_c" in df.columns else 0.0
    min_temp = float(df["temperature_c"].min()) if "temperature_c" in df.columns else 0.0
    max_temp = float(df["temperature_c"].max()) if "temperature_c" in df.columns else 0.0

    avg_hum = float(df["humidity_percent"].mean()) if "humidity_percent" in df.columns else 0.0
    total_precip = float(df["precipitation_mm"].sum()) if "precipitation_mm" in df.columns else 0.0
    avg_wind = float(df["wind_speed_kmh"].mean()) if "wind_speed_kmh" in df.columns else 0.0

    return {
        "total_observations": total_obs,
        "monitored_cities": cities_count,
        "latest_timestamp": latest_ts_str,
        "avg_temperature": round(avg_temp, 1),
        "min_temperature": round(min_temp, 1),
        "max_temperature": round(max_temp, 1),
        "avg_humidity": round(avg_hum, 1),
        "total_precipitation": round(total_precip, 2),
        "avg_wind_speed": round(avg_wind, 1),
    }


def compute_city_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-city summary metrics.
    """
    if df.empty or "city" not in df.columns:
        return pd.DataFrame()

    summary = (
        df.groupby("city")
        .agg(
            min_temperature=("temperature_c", "min"),
            avg_temperature=("temperature_c", "mean"),
            max_temperature=("temperature_c", "max"),
            avg_humidity=("humidity_percent", "mean"),
            total_precipitation=("precipitation_mm", "sum"),
            avg_wind_speed=("wind_speed_kmh", "mean"),
            elevation_m=("elevation_m", "first"),
            geohash=("geohash", "first") if "geohash" in df.columns else ("city", "count"),
            records_count=("temperature_c", "count"),
        )
        .reset_index()
    )

    summary["avg_temperature"] = summary["avg_temperature"].round(1)
    summary["min_temperature"] = summary["min_temperature"].round(1)
    summary["max_temperature"] = summary["max_temperature"].round(1)
    summary["avg_humidity"] = summary["avg_humidity"].round(1)
    summary["total_precipitation"] = summary["total_precipitation"].round(2)
    summary["avg_wind_speed"] = summary["avg_wind_speed"].round(1)

    return summary


def compute_geohash_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-geohash spatial summary metrics.
    """
    if df.empty or "geohash" not in df.columns:
        return pd.DataFrame()

    agg_dict = {
        "temperature_c": ["mean", "min", "max"],
        "humidity_percent": "mean",
        "precipitation_mm": "sum",
        "wind_speed_kmh": "mean",
        "grid_latitude": "first",
        "grid_longitude": "first",
        "elevation_m": "first",
    }
    if "city" in df.columns:
        agg_dict["city"] = "first"

    grouped = df.groupby("geohash").agg(agg_dict)

    # Flatten multi-level columns
    flat_cols = []
    for col in grouped.columns:
        if isinstance(col, tuple):
            if col[1] in ["mean", "min", "max", "sum", "first"]:
                if col[1] == "first":
                    flat_cols.append(col[0])
                else:
                    flat_cols.append(f"{col[1]}_{col[0]}")
            else:
                flat_cols.append(f"{col[0]}_{col[1]}")
        else:
            flat_cols.append(col)
    grouped.columns = flat_cols
    summary = grouped.reset_index()

    # Clean up column names and round
    if "mean_temperature_c" in summary.columns:
        summary["avg_temperature"] = summary["mean_temperature_c"].round(1)
    if "min_temperature_c" in summary.columns:
        summary["min_temperature"] = summary["min_temperature_c"].round(1)
    if "max_temperature_c" in summary.columns:
        summary["max_temperature"] = summary["max_temperature_c"].round(1)
    if "mean_humidity_percent" in summary.columns:
        summary["avg_humidity"] = summary["mean_humidity_percent"].round(1)
    if "sum_precipitation_mm" in summary.columns:
        summary["total_precipitation"] = summary["sum_precipitation_mm"].round(2)
    if "mean_wind_speed_kmh" in summary.columns:
        summary["avg_wind_speed"] = summary["mean_wind_speed_kmh"].round(1)

    return summary


def compute_hourly_trajectory(df: pd.DataFrame, metric: str = "temperature_c") -> pd.DataFrame:
    """
    Pivots hourly observation dataset for time-series visualization.
    """
    if df.empty or metric not in df.columns:
        return pd.DataFrame()

    pivot = df.pivot(index="timestamp", columns="city", values=metric)
    pivot["National_Average"] = pivot.mean(axis=1).round(2)
    return pivot.reset_index()

