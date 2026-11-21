import logging
import pandas as pd
import geohash2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

GEOHASH_PRECISION = 6


def add_geohash(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ["grid_latitude", "grid_longitude"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    df = df.copy()

    df["geohash"] = df.apply(
        lambda row: geohash2.encode(
            row["grid_latitude"],
            row["grid_longitude"],
            precision=GEOHASH_PRECISION
        ),
        axis=1
    )

    df["geohash_precision"] = GEOHASH_PRECISION

    logger.info("Geohash generation completed")
    logger.info("Unique geohash cells: %s", df["geohash"].nunique())

    return df


if __name__ == "__main__":
    input_path = "data/processed/weather_catalog.csv"
    output_path = "data/processed/weather_geospatial.csv"

    df = pd.read_csv(input_path)

    df = add_geohash(df)

    df.to_csv(output_path, index=False)

    print("\nGeospatial dataset preview:")
    print(df[[
        "city",
        "grid_latitude",
        "grid_longitude",
        "geohash",
        "geohash_precision"
    ]].drop_duplicates().to_string(index=False))

    print(f"\nSaved to: {output_path}")
