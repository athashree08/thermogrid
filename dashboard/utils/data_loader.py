"""
ThermoGrid — Centralized Data Loader Utility
Provides cached, resilient access to processed weather datasets,
Parquet storage, data quality reports, and pipeline metadata.
"""

import json
import logging
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pyarrow.parquet as pq
import streamlit as st

logger = logging.getLogger(__name__)

# Base project directory resolved relative to this module
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATA_REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
CONFIG_DIR = PROJECT_ROOT / "config"

CATALOG_PATH = DATA_PROCESSED_DIR / "weather_catalog.csv"
GEOSPATIAL_PATH = DATA_PROCESSED_DIR / "weather_geospatial.csv"
AGGREGATED_PATH = DATA_PROCESSED_DIR / "weather_aggregated.csv"
PARQUET_DIR = DATA_PROCESSED_DIR / "parquet"
QUALITY_REPORT_PATH = DATA_REPORTS_DIR / "data_quality_report.json"
LOCATIONS_PATH = CONFIG_DIR / "locations.json"


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT


@st.cache_data(show_spinner=False)
def load_weather_catalog() -> pd.DataFrame:
    """
    Load data/processed/weather_catalog.csv.
    Standardizes timestamps to UTC datetime.
    """
    if not CATALOG_PATH.exists():
        logger.warning("Catalog dataset not found at %s", CATALOG_PATH)
        return pd.DataFrame()

    df = pd.read_csv(CATALOG_PATH)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    if "ingested_at" in df.columns:
        df["ingested_at"] = pd.to_datetime(df["ingested_at"], utc=True)
    return df


@st.cache_data(show_spinner=False)
def load_weather_geospatial() -> pd.DataFrame:
    """
    Load data/processed/weather_geospatial.csv containing Geohashes.
    Standardizes timestamps to UTC datetime.
    """
    if not GEOSPATIAL_PATH.exists():
        logger.warning("Geospatial dataset not found at %s", GEOSPATIAL_PATH)
        return pd.DataFrame()

    df = pd.read_csv(GEOSPATIAL_PATH)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    if "ingested_at" in df.columns:
        df["ingested_at"] = pd.to_datetime(df["ingested_at"], utc=True)
    return df


@st.cache_data(show_spinner=False)
def load_weather_aggregated() -> pd.DataFrame:
    """
    Load data/processed/weather_aggregated.csv.
    Enriches with city name from geospatial dataset if available.
    """
    if not AGGREGATED_PATH.exists():
        logger.warning("Aggregated dataset not found at %s", AGGREGATED_PATH)
        return pd.DataFrame()

    df = pd.read_csv(AGGREGATED_PATH)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # Enrich with city if geospatial mapping is available
    geo_df = load_weather_geospatial()
    if not geo_df.empty and "geohash" in geo_df.columns and "city" in geo_df.columns:
        city_map = geo_df[["geohash", "city"]].drop_duplicates().set_index("geohash")["city"].to_dict()
        df["city"] = df["geohash"].map(city_map)

    return df


@st.cache_data(show_spinner=False)
def load_parquet_dataset() -> pd.DataFrame:
    """
    Load partitioned Parquet dataset from data/processed/parquet.
    """
    if not PARQUET_DIR.exists() or not any(PARQUET_DIR.rglob("*.parquet")):
        logger.warning("No parquet files found in %s", PARQUET_DIR)
        return pd.DataFrame()

    table = pq.read_table(str(PARQUET_DIR))
    df = table.to_pandas()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # Enrich with city if missing
    if "city" not in df.columns and "geohash" in df.columns:
        geo_df = load_weather_geospatial()
        if not geo_df.empty:
            city_map = geo_df[["geohash", "city"]].drop_duplicates().set_index("geohash")["city"].to_dict()
            df["city"] = df["geohash"].map(city_map)

    return df


@st.cache_data(show_spinner=False)
def load_data_quality_report() -> Dict[str, Any]:
    """
    Load validation results from data/reports/data_quality_report.json.
    """
    if not QUALITY_REPORT_PATH.exists():
        return {
            "passed": False,
            "error": "Report file not found",
            "total_records": 0,
            "null_counts": {},
            "duplicate_records": 0,
            "invalid_temperature": 0,
            "invalid_humidity": 0,
            "negative_precipitation": 0,
            "negative_wind_speed": 0,
            "invalid_coordinates": 0,
            "missing_columns": []
        }

    try:
        with open(QUALITY_REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to read data quality report: %s", e)
        return {"passed": False, "error": str(e)}


@st.cache_data(show_spinner=False)
def load_locations_config() -> List[Dict[str, Any]]:
    """
    Load city coordinates configuration from config/locations.json.
    """
    if not LOCATIONS_PATH.exists():
        return []

    try:
        with open(LOCATIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to read locations config: %s", e)
        return []


def get_city_geohash_map() -> Dict[str, str]:
    """
    Return bidirectional mapping between City names and Geohash IDs.
    """
    df = load_weather_geospatial()
    if df.empty or "city" not in df.columns or "geohash" not in df.columns:
        return {}
    return df[["city", "geohash"]].drop_duplicates().set_index("city")["geohash"].to_dict()


def get_dataset_summary() -> Dict[str, Any]:
    """
    Calculate summary metadata across the active dataset.
    """
    df = load_weather_geospatial()
    if df.empty:
        return {
            "total_records": 0,
            "cities": [],
            "geohashes": [],
            "min_timestamp": None,
            "max_timestamp": None,
            "date_range_str": "No data available",
            "is_prototype": True
        }

    min_ts = df["timestamp"].min()
    max_ts = df["timestamp"].max()

    date_str = f"{min_ts.strftime('%Y-%m-%d %H:%M UTC')} to {max_ts.strftime('%Y-%m-%d %H:%M UTC')}"

    return {
        "total_records": len(df),
        "cities": sorted(df["city"].dropna().unique().tolist()),
        "geohashes": sorted(df["geohash"].dropna().unique().tolist()),
        "min_timestamp": min_ts,
        "max_timestamp": max_ts,
        "date_range_str": date_str,
        "is_prototype": True
    }


def get_pipeline_artifacts_status() -> List[Dict[str, Any]]:
    """
    Inspect the file system for actual pipeline artifacts generated at each stage.
    """
    stages = [
        {
            "stage_id": 1,
            "task_id": "weather_ingestion",
            "name": "Weather Ingestion",
            "source_module": "src/ingestion/weather_ingestion.py",
            "artifact_path": DATA_RAW_DIR,
            "artifact_type": "directory",
            "description": "Hourly API payloads fetched from Open-Meteo"
        },
        {
            "stage_id": 2,
            "task_id": "transform_weather",
            "name": "Data Transformation",
            "source_module": "src/processing/transform.py",
            "artifact_path": CATALOG_PATH,
            "artifact_type": "csv",
            "description": "Standardized tabular weather observations catalog"
        },
        {
            "stage_id": 3,
            "task_id": "generate_geohash",
            "name": "Geospatial Indexing",
            "source_module": "src/processing/geospatial.py",
            "artifact_path": GEOSPATIAL_PATH,
            "artifact_type": "csv",
            "description": "Enriched records with 6-char precision geohash identifiers"
        },
        {
            "stage_id": 4,
            "task_id": "aggregate_weather",
            "name": "Geospatial Aggregation",
            "source_module": "src/processing/aggregation.py",
            "artifact_path": AGGREGATED_PATH,
            "artifact_type": "csv",
            "description": "Grouped metrics by (geohash, timestamp) with averaged values"
        },
        {
            "stage_id": 5,
            "task_id": "store_parquet",
            "name": "Parquet Storage",
            "source_module": "src/storage/parquet_storage.py",
            "artifact_path": PARQUET_DIR,
            "artifact_type": "parquet",
            "description": "Snappy-compressed partitioned columnar storage"
        },
        {
            "stage_id": 6,
            "task_id": "validate_data",
            "name": "Data Quality Validation",
            "source_module": "src/validation/data_quality.py",
            "artifact_path": QUALITY_REPORT_PATH,
            "artifact_type": "json",
            "description": "Automated data quality verification report"
        }
    ]

    status_list = []
    for stage in stages:
        path: Path = stage["artifact_path"]
        exists = path.exists()
        size_bytes = 0
        last_modified = None
        item_count = 0

        if exists:
            if path.is_dir():
                files = list(path.rglob("*"))
                real_files = [f for f in files if f.is_file()]
                item_count = len(real_files)
                size_bytes = sum(f.stat().st_size for f in real_files)
                if real_files:
                    last_mod_ts = max(f.stat().st_mtime for f in real_files)
                    last_modified = datetime.fromtimestamp(last_mod_ts, timezone.utc)
            else:
                stat = path.stat()
                size_bytes = stat.st_size
                last_modified = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
                if path.suffix == ".csv":
                    try:
                        # Fast line count
                        with open(path, "rb") as f:
                            item_count = max(0, sum(1 for _ in f) - 1)
                    except Exception:
                        item_count = 0
                elif path.suffix == ".json":
                    item_count = 1

        status_list.append({
            **stage,
            "exists": exists,
            "size_kb": round(size_bytes / 1024, 2),
            "last_modified": last_modified.strftime("%Y-%m-%d %H:%M:%S UTC") if last_modified else "N/A",
            "item_count": item_count
        })

    return status_list


def check_airflow_status() -> Dict[str, Any]:
    """
    Check if the local Apache Airflow server / Execution API is reachable.
    """
    url = "http://localhost:8081/execution/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ThermoGrid-Dashboard/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            return {
                "available": True,
                "status_code": response.status,
                "url": url,
                "message": "Airflow API is responding"
            }
    except Exception as e:
        return {
            "available": False,
            "status_code": None,
            "url": url,
            "message": f"Airflow service offline or port 8081 unreachable ({type(e).__name__})"
        }

