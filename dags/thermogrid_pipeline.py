from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

PROJECT_DIR = Path.home() / "projects" / "thermogrid"
PYTHON = PROJECT_DIR / ".venv" / "bin" / "python"

default_args = {
    "owner": "thermogrid",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="thermogrid_weather_pipeline",
    description="Weather ingestion, geospatial processing and Parquet storage",
    default_args=default_args,
    start_date=datetime(2026, 11, 21),
    schedule=None,
    catchup=False,
    tags=["thermogrid", "weather", "geospatial"],
) as dag:

    ingestion = BashOperator(
        task_id="weather_ingestion",
        bash_command=f"'{PYTHON}' src/ingestion/weather_ingestion.py",
        cwd=str(PROJECT_DIR),
    )

    transformation = BashOperator(
        task_id="transform_weather",
        bash_command=f"'{PYTHON}' src/processing/transform.py",
        cwd=str(PROJECT_DIR),
    )

    geospatial = BashOperator(
        task_id="generate_geohash",
        bash_command=f"'{PYTHON}' src/processing/geospatial.py",
        cwd=str(PROJECT_DIR),
    )

    aggregation = BashOperator(
        task_id="aggregate_weather",
        bash_command=f"'{PYTHON}' src/processing/aggregation.py",
        cwd=str(PROJECT_DIR),
    )

    storage = BashOperator(
        task_id="store_parquet",
        bash_command=f"'{PYTHON}' src/storage/parquet_storage.py",
        cwd=str(PROJECT_DIR),
    )

    validation = BashOperator(
        task_id="validate_data",
        bash_command=f"'{PYTHON}' src/validation/data_quality.py",
        cwd=str(PROJECT_DIR),
    )

    ingestion >> transformation >> geospatial >> aggregation >> storage >> validation
