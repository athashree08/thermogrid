import pandas as pd
import pytest

from src.processing.aggregation import aggregate_weather
from src.processing.geospatial import add_geohash
from src.validation.data_quality import validate_weather_data


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "geohash": ["tek92u", "tek92u"],
        "timestamp": [
            "2026-11-21T10:00:00Z",
            "2026-11-21T10:00:00Z"
        ],
        "temperature_c": [25.0, 27.0],
        "humidity_percent": [60, 70],
        "precipitation_mm": [0.0, 2.0],
        "wind_speed_kmh": [5.0, 7.0],
        "grid_latitude": [18.5237, 18.5237],
        "grid_longitude": [73.8687, 73.8687],
        "elevation_m": [561.0, 561.0]
    })


def test_geohash_generation():
    df = pd.DataFrame({
        "grid_latitude": [18.5237],
        "grid_longitude": [73.8687]
    })

    result = add_geohash(df)

    assert "geohash" in result.columns
    assert len(result.iloc[0]["geohash"]) == 6


def test_aggregation(sample_data):
    result = aggregate_weather(sample_data)

    assert len(result) == 1
    assert result.iloc[0]["temperature_c"] == 26.0
    assert result.iloc[0]["humidity_percent"] == 65.0


def test_data_quality_passes(sample_data):
    # Give the second observation a different timestamp.
    sample_data.loc[1, "timestamp"] = "2026-11-21T11:00:00Z"

    result = validate_weather_data(sample_data)

    assert result["passed"] is True
    assert result["duplicate_records"] == 0
def test_data_quality_detects_invalid_humidity(sample_data):
    sample_data.loc[0, "humidity_percent"] = 150

    result = validate_weather_data(sample_data)

    assert result["passed"] is False
    assert result["invalid_humidity"] == 1


def test_aggregation_rejects_missing_columns(sample_data):
    sample_data = sample_data.drop(columns=["temperature_c"])

    with pytest.raises(ValueError):
        aggregate_weather(sample_data)
