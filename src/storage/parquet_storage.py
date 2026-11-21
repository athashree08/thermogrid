import logging
from pathlib import Path
import shutil
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

INPUT_PATH = Path("data/processed/weather_aggregated.csv")
OUTPUT_DIR = Path("data/processed/parquet")


def store_parquet(df: pd.DataFrame, output_dir: Path) -> None:
    required = ["timestamp", "geohash"]

    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True
    )

    df["year"] = df["timestamp"].dt.year.astype(str)
    df["month"] = df["timestamp"].dt.month.astype(str).str.zfill(2)
    df["day"] = df["timestamp"].dt.day.astype(str).str.zfill(2)

    table = pa.Table.from_pandas(
        df,
        preserve_index=False
    )
    # Rebuild the output dataset to prevent stale files accumulating.
    if output_dir.exists():
    	shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
	
    pq.write_to_dataset(
        table,
        root_path=str(output_dir),
        partition_cols=["year", "month", "day"],
        compression="snappy"
    )

    logger.info("Parquet storage completed")
    logger.info("Output directory: %s", output_dir)


if __name__ == "__main__":
    df = pd.read_csv(INPUT_PATH)

    store_parquet(df, OUTPUT_DIR)

    dataset = pq.ParquetDataset(str(OUTPUT_DIR))

    print("\nParquet schema:")
    print(dataset.schema)

    print("\nParquet files:")
    for path in OUTPUT_DIR.rglob("*.parquet"):
        print(path)

    print("\nTotal Parquet files:", len(list(OUTPUT_DIR.rglob("*.parquet"))))
