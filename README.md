# ThermoGrid

### Geospatial Weather Data Pipeline

ThermoGrid is a Python-based data engineering project that collects hourly weather observations for selected Indian cities, transforms them into structured datasets, enriches them with geospatial identifiers, aggregates observations, stores the results in partitioned Parquet format, and validates data quality.

The pipeline is orchestrated using Apache Airflow.

## Project Overview

The current prototype processes weather data for five cities:

- Pune
- Mumbai
- Bengaluru
- Hyderabad
- Delhi

Weather data is collected through the Open-Meteo API.

## Architecture

```text
Open-Meteo API
      |
      v
Weather Ingestion
      |
      v
Raw JSON Storage
      |
      v
Data Transformation
      |
      v
Geohash Generation
      |
      v
Geospatial Aggregation
      |
      v
Partitioned Parquet Storage
      |
      v
Data Quality Validation
```

Apache Airflow orchestrates the workflow.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Weather Data Source | Open-Meteo API |
| Data Processing | Pandas |
| Geospatial Indexing | Geohash |
| Storage Format | Apache Parquet |
| Compression | Snappy |
| Workflow Orchestration | Apache Airflow 3.3.2 |
| Testing | Pytest |

## Project Structure

```text
thermogrid/
│
├── config/
│   └── locations.json
│
├── dags/
│   └── thermogrid_pipeline.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── reports/
│
├── src/
│   ├── ingestion/
│   │   └── weather_ingestion.py
│   │
│   ├── processing/
│   │   ├── transform.py
│   │   ├── geospatial.py
│   │   └── aggregation.py
│   │
│   ├── storage/
│   │   └── parquet_storage.py
│   │
│   └── validation/
│       └── data_quality.py
│
├── tests/
│   └── test_processing.py
│
├── scripts/
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## Pipeline Workflow

### 1. Weather Ingestion

- Fetches hourly weather observations from Open-Meteo.
- Collects temperature, relative humidity, precipitation, and wind speed.
- Uses retry logic for failed API requests.
- Saves raw API responses as JSON files.

### 2. Data Transformation

- Reads raw JSON files.
- Converts nested hourly observations into tabular records.
- Standardizes column names.
- Removes duplicate city and timestamp records.
- Saves the weather catalog as CSV.

### 3. Geospatial Processing

- Generates Geohash identifiers using API-returned grid coordinates.
- Adds geospatial identifiers to weather observations.

### 4. Aggregation

- Groups observations by Geohash and timestamp.
- Calculates average weather measurements and associated spatial attributes.

### 5. Parquet Storage

- Stores processed observations in Apache Parquet format.
- Uses Snappy compression.
- Partitions output by year, month, and day.

### 6. Data Quality Validation

Checks include:

- Required columns
- Missing values
- Duplicate records
- Temperature range
- Humidity range
- Negative precipitation
- Negative wind speed
- Coordinate validity

A JSON report is generated with validation results.

## Airflow Orchestration

The DAG is named:

`thermogrid_weather_pipeline`

It contains six sequential tasks:

1. `weather_ingestion`
2. `transform_weather`
3. `generate_geohash`
4. `aggregate_weather`
5. `store_parquet`
6. `validate_data`

Each task executes its corresponding Python module.

## Installation and Setup

### Prerequisites

- Ubuntu or another Linux environment
- Python 3.12
- pip or uv
- Apache Airflow 3.3.2

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd thermogrid
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Alternatively, use uv:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the pipeline manually

Execute the modules in sequence from the project root:

```bash
python src/ingestion/weather_ingestion.py
python src/processing/transform.py
python src/processing/geospatial.py
python src/processing/aggregation.py
python src/storage/parquet_storage.py
python src/validation/data_quality.py
```

### 5. Run tests

```bash
pytest -v
```

## Airflow Setup

Airflow is installed separately from the project's Python virtual environment.

Activate the Airflow environment:

```bash
source ~/airflow_venv/bin/activate
```

Configure the Airflow home and DAG directory:

```bash
export AIRFLOW_HOME=~/airflow
export AIRFLOW__CORE__DAGS_FOLDER="$HOME/projects/thermogrid/dags"
export AIRFLOW__API__PORT=8081
export AIRFLOW__CORE__EXECUTION_API_SERVER_URL="http://localhost:8081/execution/"
```

Start Airflow:

```bash
airflow standalone
```

Open the Airflow UI:

http://127.0.0.1:8081/

Unpause `thermogrid_weather_pipeline` and trigger a DAG run.

**Note:** The execution API URL must match the API server port configured above.

## Current Prototype Results

The current five-city test run produced:

| Metric | Result |
|---|---:|
| Cities processed | 5 |
| Weather observations | 120 |
| Duplicate records removed during transformation | 120 |
| Final records | 120 |
| Missing values | 0 |
| Duplicate records after aggregation | 0 |
| Data quality validation | Passed |

The current dataset represents a single day's observations for five city-level API grid points.

## Limitations

- The current prototype covers five cities.
- Each city is represented by one API-returned weather grid point.
- The current test dataset covers one date.
- Aggregation currently operates on a small number of spatial points.
- Storage currently performs a full rebuild rather than incremental upserts.
- Historical weather trends and forecasting are not implemented.

## Future Improvements

- Expand geographic coverage.
- Integrate additional weather and environmental datasets.
- Implement incremental ingestion and storage.
- Add historical data processing.
- Improve spatial aggregation using multiple grid points.
- Add monitoring, logging, and automated failure alerts.
- Explore scalable storage and processing architectures.

## Data Source

Weather data: [Open-Meteo](https://open-meteo.com/)

## Disclaimer

ThermoGrid is an educational data engineering prototype. It is not intended for operational weather forecasting or safety-critical applications.
