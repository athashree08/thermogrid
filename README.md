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
Partitioned Parquet Storage & Quality Validation
      |
      v
ThermoGrid Streamlit Intelligence Dashboard
(Overview | Weather Explorer | Geospatial Analytics | Quality | Pipeline Monitor)
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
| Frontend Dashboard | Streamlit 1.67+ |
| Data Visualization | Plotly |
| Geospatial Mapping | PyDeck / Folium |
| Testing | Pytest |

## Project Structure

```text
thermogrid/
│
├── .streamlit/
│   └── config.toml
│
├── config/
│   └── locations.json
│
├── dags/
│   └── thermogrid_pipeline.py
│
├── dashboard/
│   ├── app.py
│   ├── assets/
│   │   └── styles.css
│   ├── pages/
│   │   ├── 1_Overview.py
│   │   ├── 2_Weather_Explorer.py
│   │   ├── 3_Geospatial_Analytics.py
│   │   ├── 4_Data_Quality.py
│   │   └── 5_Pipeline_Monitor.py
│   └── utils/
│       ├── __init__.py
│       ├── charts.py
│       ├── data_loader.py
│       ├── map_utils.py
│       └── metrics.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   ├── parquet/
│   │   ├── weather_aggregated.csv
│   │   ├── weather_catalog.csv
│   │   └── weather_geospatial.csv
│   └── reports/
│       └── data_quality_report.json
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
│   ├── test_dashboard.py
│   └── test_processing.py
│
├── streamlit_app.py
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

### 6. Launch the ThermoGrid Dashboard

Launch the interactive dashboard locally:

```bash
streamlit run streamlit_app.py
```

The platform will open automatically at `http://localhost:8501`.

## ThermoGrid Dashboard

*Geospatial Weather Intelligence Platform*

ThermoGrid includes a multi-page interactive analytics platform built with Streamlit, Plotly, PyDeck, and Folium. It connects directly to the processed datasets (`weather_catalog.csv`, `weather_geospatial.csv`, `weather_aggregated.csv`), Parquet lake partitions, and data quality validation reports.

### Dashboard Sections

1. **Overview (`1_Overview.py`):**
   - Live dynamic KPI cards: Total Observations (120), Monitored Cities (5), Latest Timestamp (UTC), Validation Status (PASSED 100%), Mean Temperature, Humidity, Precipitation, Wind Speed.
   - 24-hour multi-city temperature trajectories and diurnal cycles.
   - City min/avg/max temperature comparison and humidity variation charts.
   - Diurnal atmospheric matrix heatmap across monitored cities.
   - Raw observation catalog explorer with text search and real-time filtering.
   - Prominent notice documenting the historical 24-hour prototype nature of the dataset.

2. **Weather Explorer (`2_Weather_Explorer.py`):**
   - High-performance interactive map of India with actual model grid coordinates.
   - Dual map engines: 3D PyDeck DeckGL with elevation extrusion columns, or 2D OpenStreetMap Folium.
   - Marker color-coding based on temperature gradients (cyan to crimson).
   - City node selector (Pune, Mumbai, Bengaluru, Hyderabad, Delhi) with deep-dive stats.
   - Time-series comparison comparing individual city metrics against the 5-city national baseline.
   - Complete 24-hour tabular observation log.

3. **Geospatial Analytics (`3_Geospatial_Analytics.py`):**
   - Precision-6 Geohash distribution analysis (~±0.61 km spatial resolution).
   - Numerical Weather Model Grid Snapping: Detailed comparison of requested user coordinates vs API numerical grid points and approximate distance offsets.
   - Weather metric distribution by Geohash cell using box plots.
   - Verification of geospatial aggregation logic (`weather_aggregated.csv` vs `weather_geospatial.csv`).
   - Interactive individual Geohash inspector.
   - Architecture explainer detailing base-32 spatial indexing principles and prototype grid constraints.

4. **Data Quality & Governance (`4_Data_Quality.py`):**
   - Dynamic ingestion of `data/reports/data_quality_report.json`.
   - Comprehensive audit summary: Schema completeness, null counts, duplicate key checks, physical temperature/humidity bounds, and non-negativity checks.
   - "Execute Live Quality Audit" button to trigger `src/validation/data_quality.py` validation logic live on active records.
   - Full column-level missing value breakdown and raw JSON payload inspector.

5. **Pipeline Monitor (`5_Pipeline_Monitor.py`):**
   - Complete architecture overview of the `thermogrid_weather_pipeline` Apache Airflow DAG.
   - Real-time Airflow API connectivity detector (runs in decoupled data-lake mode if Airflow is offline).
   - Live filesystem verification of stage artifacts: checks existence, file size, last modified time, and record count for each of the 6 pipeline tasks.
   - Detailed task specifications for Ingestion, Transformation, Geospatial Indexing, Aggregation, Storage, and Validation.
   - Apache Parquet storage inspector with Arrow schema viewer and Snappy partition metadata.

### Deployment on Streamlit Community Cloud

The dashboard is designed for zero-config public deployment on **Streamlit Community Cloud**:

1. Push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Select **New App** and configure:
   - **Repository:** `<YOUR_GITHUB_USERNAME>/thermogrid`
   - **Branch:** `main` (or active branch)
   - **Main file path:** `streamlit_app.py`
4. Click **Deploy**. The app will automatically install dependencies from `requirements.txt` and launch without requiring external database connections, active Airflow instances, or private API keys.

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
