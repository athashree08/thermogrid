
import json
import logging
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def transform_weather_data():

    records = []

    json_files = list(RAW_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError("No raw JSON files found.")

    for file_path in json_files:

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        city = data["city"]

        requested_latitude = data["latitude"]
        requested_longitude = data["longitude"]

        weather = data["weather_data"]
        hourly = weather["hourly"]

        df = pd.DataFrame(hourly)

        df["city"] = city
        df["requested_latitude"] = requested_latitude
        df["requested_longitude"] = requested_longitude

        df["grid_latitude"] = weather["latitude"]
        df["grid_longitude"] = weather["longitude"]
        df["elevation_m"] = weather["elevation"]

        df["source"] = data["source"]
        df["ingested_at"] = data["ingested_at"]

        records.append(df)

        logger.info(
            "Transformed %s: %s hourly records",
            city,
            len(df)
        )

    final_df = pd.concat(records, ignore_index=True)

    # Keep the latest version of each city's hourly observation.
    final_df = final_df.sort_values("ingested_at")

    records_before = len(final_df)

    final_df = final_df.drop_duplicates(
        subset=["city", "time"],
        keep="last"
    ).reset_index(drop=True)

    records_after = len(final_df)

    logger.info(
        "Deduplication: %d records removed",
        records_before - records_after
    )

    final_df["time"] = pd.to_datetime(
        final_df["time"],
        utc=True
    )

    final_df = final_df.rename(
        columns={
            "time": "timestamp",
            "temperature_2m": "temperature_c",
            "relative_humidity_2m": "humidity_percent",
            "precipitation": "precipitation_mm",
            "wind_speed_10m": "wind_speed_kmh"
        }
    )

    output_path = PROCESSED_DIR / "weather_catalog.csv"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    final_df.to_csv(output_path, index=False)

    logger.info("Transformation completed")
    logger.info("Total records: %d", len(final_df))
    logger.info("Total columns: %d", len(final_df.columns))
    logger.info("Saved: %s", output_path)

    print("\nDataset preview:")
    print(final_df.head())

    print("\nDataset information:")
    print(final_df.info())

    return final_df


if __name__ == "__main__":
    transform_weather_data()

