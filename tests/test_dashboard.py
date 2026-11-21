"""
Unit & Integration Tests for ThermoGrid Dashboard Utilities
"""

import pytest
import pandas as pd
from dashboard.utils.data_loader import (
    load_weather_catalog,
    load_weather_geospatial,
    load_weather_aggregated,
    load_parquet_dataset,
    load_data_quality_report,
    load_locations_config,
    get_dataset_summary,
    get_pipeline_artifacts_status,
    check_airflow_status,
)
from dashboard.utils.metrics import (
    compute_overview_kpis,
    compute_city_summary,
    compute_geohash_summary,
    compute_hourly_trajectory,
)
from dashboard.utils.charts import (
    create_temperature_trend_chart,
    create_city_metric_bar_chart,
    create_humidity_comparison_chart,
    create_precipitation_chart,
    create_wind_speed_chart,
    create_geohash_boxplot,
    create_hourly_heatmap,
)
from dashboard.utils.map_utils import (
    build_pydeck_weather_map,
    build_folium_weather_map,
    get_temperature_color,
)


def test_data_loader_catalog():
    df = load_weather_catalog()
    assert not df.empty
    assert len(df) == 120
    assert "timestamp" in df.columns
    assert "city" in df.columns
    assert "temperature_c" in df.columns


def test_data_loader_geospatial():
    df = load_weather_geospatial()
    assert not df.empty
    assert len(df) == 120
    assert "geohash" in df.columns
    assert df["geohash_precision"].iloc[0] == 6
    assert df["city"].nunique() == 5
    assert df["geohash"].nunique() == 5


def test_data_loader_aggregated():
    df = load_weather_aggregated()
    assert not df.empty
    assert len(df) == 120
    assert "geohash" in df.columns
    assert "temperature_c" in df.columns
    assert "city" in df.columns


def test_data_loader_parquet():
    df = load_parquet_dataset()
    assert not df.empty
    assert len(df) == 120
    assert "geohash" in df.columns
    assert "year" in df.columns
    assert "month" in df.columns
    assert "day" in df.columns


def test_data_loader_quality_report():
    report = load_data_quality_report()
    assert report.get("passed") is True
    assert report.get("total_records") == 120
    assert report.get("duplicate_records") == 0


def test_data_loader_locations():
    locations = load_locations_config()
    assert len(locations) == 5
    city_names = [loc["city"] for loc in locations]
    assert "Pune" in city_names
    assert "Mumbai" in city_names
    assert "Bengaluru" in city_names
    assert "Hyderabad" in city_names
    assert "Delhi" in city_names


def test_dataset_summary():
    summary = get_dataset_summary()
    assert summary["total_records"] == 120
    assert len(summary["cities"]) == 5
    assert len(summary["geohashes"]) == 5
    assert summary["is_prototype"] is True


def test_pipeline_artifacts_status():
    status = get_pipeline_artifacts_status()
    assert len(status) == 6
    for stage in status:
        assert stage["exists"] is True


def test_check_airflow_status():
    status = check_airflow_status()
    assert "available" in status
    assert "url" in status


def test_compute_overview_kpis():
    df = load_weather_geospatial()
    kpis = compute_overview_kpis(df)
    assert kpis["total_observations"] == 120
    assert kpis["monitored_cities"] == 5
    assert kpis["avg_temperature"] > 0
    assert kpis["avg_humidity"] > 0
    assert kpis["latest_timestamp"] != "N/A"


def test_compute_city_summary():
    df = load_weather_geospatial()
    summary = compute_city_summary(df)
    assert len(summary) == 5
    assert "min_temperature" in summary.columns
    assert "avg_temperature" in summary.columns
    assert "max_temperature" in summary.columns


def test_compute_geohash_summary():
    df = load_weather_geospatial()
    summary = compute_geohash_summary(df)
    assert len(summary) == 5
    assert "avg_temperature" in summary.columns


def test_compute_hourly_trajectory():
    df = load_weather_geospatial()
    trajectory = compute_hourly_trajectory(df, "temperature_c")
    assert not trajectory.empty
    assert "National_Average" in trajectory.columns


def test_charts_generation():
    df = load_weather_geospatial()
    fig1 = create_temperature_trend_chart(df)
    assert fig1 is not None

    fig2 = create_city_metric_bar_chart(df, "temperature_c")
    assert fig2 is not None

    fig3 = create_humidity_comparison_chart(df)
    assert fig3 is not None

    fig4 = create_precipitation_chart(df)
    assert fig4 is not None

    fig5 = create_wind_speed_chart(df)
    assert fig5 is not None

    fig6 = create_geohash_boxplot(df, "temperature_c")
    assert fig6 is not None

    fig7 = create_hourly_heatmap(df, "temperature_c")
    assert fig7 is not None


def test_map_generation():
    df = load_weather_geospatial()
    deck = build_pydeck_weather_map(df, selected_city="Pune")
    assert deck is not None
    assert len(deck.layers) == 3

    folium_map = build_folium_weather_map(df, selected_city="Mumbai")
    assert folium_map is not None


def test_get_temperature_color():
    color_cool = get_temperature_color(15.0, 10.0, 35.0)
    color_warm = get_temperature_color(32.0, 10.0, 35.0)
    assert len(color_cool) == 4
    assert len(color_warm) == 4
    assert color_cool[3] == 220

