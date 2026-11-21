import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

GROUP_COLUMNS = ["geohash", "timestamp"]

AGGREGATIONS = {
    "temperature_c": "mean",
    "humidity_percent": "mean",
    "precipitation_mm": "mean",
    "wind_speed_kmh": "mean",
    "grid_latitude": "mean",
    "grid_longitude": "mean",
    "elevation_m": "mean"
}


def aggregate_weather(df: pd.DataFrame) -> pd.DataFrame:
    required = GROUP_COLUMNS + list(AGGREGATIONS.keys())

    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    result = (
        df.groupby(GROUP_COLUMNS, as_index=False)
        .agg(AGGREGATIONS)
    )

    result["timestamp"] = pd.to_datetime(
        result["timestamp"], utc=True
    )

    result = result.sort_values(
        ["geohash", "timestamp"]
    ).reset_index(drop=True)

    logger.info("Aggregation completed")
    logger.info("Input records: %d", len(df))
    logger.info("Aggregated records: %d", len(result))

    return result


if __name__ == "__main__":
    input_path = "data/processed/weather_geospatial.csv"
    output_path = "data/processed/weather_aggregated.csv"

    df = pd.read_csv(input_path)

    aggregated = aggregate_weather(df)

    aggregated.to_csv(output_path, index=False)

    print("\nAggregated dataset preview:")
    print(aggregated.head())

    print("\nDataset shape:", aggregated.shape)
    print("\nRecords per geohash:")
    print(aggregated.groupby("geohash").size())

    print(f"\nSaved to: {output_path}")
