import json
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "geohash",
    "timestamp",
    "temperature_c",
    "humidity_percent",
    "precipitation_mm",
    "wind_speed_kmh",
    "grid_latitude",
    "grid_longitude",
    "elevation_m"
]


def validate_weather_data(df: pd.DataFrame) -> dict:
    checks = {}

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    checks["missing_columns"] = missing_columns
    checks["null_counts"] = df.isnull().sum().to_dict()

    checks["duplicate_records"] = int(
        df.duplicated(
            subset=["geohash", "timestamp"]
        ).sum()
    )

    checks["invalid_temperature"] = int(
        (~df["temperature_c"].between(-90, 65)).sum()
    )

    checks["invalid_humidity"] = int(
        (~df["humidity_percent"].between(0, 100)).sum()
    )

    checks["negative_precipitation"] = int(
        (df["precipitation_mm"] < 0).sum()
    )

    checks["negative_wind_speed"] = int(
        (df["wind_speed_kmh"] < 0).sum()
    )

    checks["invalid_coordinates"] = int(
        (
            ~df["grid_latitude"].between(-90, 90)
            | ~df["grid_longitude"].between(-180, 180)
        ).sum()
    )

    checks["total_records"] = len(df)

    checks["passed"] = (
        not missing_columns
        and all(value == 0 for key, value in checks.items()
                if key in [
                    "duplicate_records",
                    "invalid_temperature",
                    "invalid_humidity",
                    "negative_precipitation",
                    "negative_wind_speed",
                    "invalid_coordinates"
                ])
        and all(value == 0 for value in checks["null_counts"].values())
    )

    return checks


if __name__ == "__main__":
    input_path = Path("data/processed/weather_aggregated.csv")
    report_path = Path("data/reports/data_quality_report.json")

    report_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)

    report = validate_weather_data(df)

    with open(report_path, "w") as file:
        json.dump(report, file, indent=4, default=str)

    print(json.dumps(report, indent=4, default=str))

    if not report["passed"]:
        raise SystemExit("Data quality validation FAILED")

    logger.info("Data quality validation PASSED")
