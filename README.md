# ThermoGrid
### Geospatial Weather Intelligence Platform

**ThermoGrid** is a Python-based geospatial weather data engineering project that collects, processes, enriches, aggregates, and validates hourly weather observations for selected Indian cities.

The project combines an automated data processing pipeline with an interactive Streamlit dashboard to explore weather observations, visualize geospatial data, and inspect data quality.

**Live Dashboard:** https://thermogrid.streamlit.app/

---

## Overview

ThermoGrid currently processes weather observations for five Indian cities:

- Pune
- Mumbai
- Bengaluru
- Hyderabad
- Delhi

Weather data is collected through the [Open-Meteo API](https://open-meteo.com/).

The pipeline transforms raw weather responses into structured datasets, generates geohash identifiers using API-returned grid coordinates, performs geospatial aggregation, stores processed data in CSV and partitioned Parquet formats, and validates data quality.

An interactive Streamlit application provides a visual interface for exploring the processed datasets.

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
                Partitioned Parquet
                         |
                         v
                 Data Quality Checks
                         |
                         v
                 Processed Datasets
                         |
                         v
                Streamlit Dashboard
```

Apache Airflow orchestrates the data processing workflow.

## Interactive Dashboard

**Live application:** https://thermogrid.streamlit.app/

The dashboard provides an interactive interface for exploring the processed weather datasets.

Its intended capabilities include:

- **Weather Overview:** Summary metrics and weather trends across monitored cities.
- **Weather Explorer:** City-wise weather observations and interactive geographic visualization.
- **Geospatial Analytics:** Exploration of geohashes, grid coordinates, and aggregated weather observations.
- **Data Quality:** Inspection of missing values, duplicates, invalid records, and validation results.
- **Pipeline Monitor:** Overview of the Airflow pipeline stages and execution information where available.

The dashboard uses processed datasets rather than requiring a continuously running local pipeline.

## Technology Stack

| Component | Technologies |
|---|---|
| Programming Language | Python |
| Data Ingestion | Open-Meteo API, Requests |
| Data Processing | Pandas |
| Geospatial Processing | Geohash |
| Data Storage | CSV, Apache Parquet, PyArrow |
| Workflow Orchestration | Apache Airflow |
| Dashboard | Streamlit |
| Data Visualization | Plotly, PyDeck |
| Testing | Pytest |
| Development Environment | WSL Ubuntu |

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
├── dashboard/
│   ├── app.py
│   ├── pages/
│   ├── utils/
│   └── assets/
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   ├── weather_catalog.csv
│   │   ├── weather_geospatial.csv
│   │   ├── weather_aggregated.csv
│   │   └── parquet/
│   │
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
│   └── test_processing.py
│
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

*The dashboard directory and entry-point filenames should reflect the final implementation in the repository.*

## Data Pipeline

The pipeline consists of six sequential stages orchestrated using Apache Airflow.

### 1. Weather Ingestion

- Retrieves hourly weather observations from Open-Meteo.
- Collects temperature, relative humidity, precipitation, and wind speed.
- Stores raw API responses as JSON files.
- Implements retry handling for API requests.

### 2. Data Transformation

- Reads raw JSON responses.
- Flattens hourly observations into structured records.
- Standardizes weather column names and units.
- Removes duplicate city-time observations.

### 3. Geospatial Enrichment

- Uses API-returned grid coordinates.
- Generates geohash identifiers at precision 6.
- Enriches weather observations with spatial identifiers.

### 4. Geospatial Aggregation

- Groups observations by geohash and timestamp.
- Calculates aggregated weather measurements and coordinate values.

### 5. Parquet Storage

- Stores processed observations in Snappy-compressed Parquet format.
- Partitions output by year, month, and day.

### 6. Data Quality Validation

Checks for:
- Missing required columns.
- Null values.
- Duplicate records.
- Invalid temperature values.
- Humidity outside the valid range.
- Negative precipitation and wind speed.
- Invalid geographic coordinates.

The validation results are saved as a JSON report.

## Airflow Orchestration

The pipeline is orchestrated through the following Airflow DAG:

`thermogrid_weather_pipeline`

| Task | Description |
|---|---|
| weather_ingestion | Collects weather observations |
| transform_weather | Transforms raw JSON data |
| generate_geohash | Generates geospatial identifiers |
| aggregate_weather | Aggregates weather observations |
| store_parquet | Writes partitioned Parquet files |
| validate_data | Runs data quality checks |

Tasks execute sequentially, with retry handling configured for failures.

## Prototype Results

The current prototype was tested using weather observations from five cities.

| Metric | Result |
|---|---:|
| Cities monitored | 5 |
| Final weather records | 120 |
| Duplicate records removed during transformation | 120 |
| Final duplicate records | 0 |
| Missing values in validated fields | 0 |
| Data quality validation | Passed |

The dataset represents one day of hourly observations for five API grid points.

## Getting Started

### Prerequisites

- Python 3.12
- Git
- pip
- Ubuntu / WSL or another compatible Linux environment

### 1. Clone the repository

```bash
git clone https://github.com/athashree08/thermogrid.git

cd thermogrid
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv

source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the data pipeline

Execute the pipeline modules sequentially:

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

### 6. Launch the dashboard

If the Streamlit entry point is `streamlit_app.py`:

```bash
streamlit run streamlit_app.py
```

The application will be available locally at:

```text
http://localhost:8501
```

## Deployment

ThermoGrid's interactive dashboard is deployed using **Streamlit Community Cloud**.

Live application:

https://thermogrid.streamlit.app/

The deployed application uses the processed datasets committed to the repository.

The dashboard does not require a continuously running local Airflow scheduler to display the existing processed results.

## Current Limitations

This is an experimental prototype, not a production-scale weather intelligence system.

Current limitations include:

- Coverage is restricted to five Indian cities.
- Each city currently uses one API-returned grid point.
- The current dataset covers one day of observations.
- Geospatial aggregation is limited by the available grid-point coverage.
- Parquet storage currently performs a full rebuild rather than incremental upserts.
- The deployed dashboard displays available processed observations; it should not be interpreted as a continuously updating live weather service.
- Airflow orchestration and dashboard deployment operate separately.

## Future Improvements

- Expand geographic coverage across India.
- Integrate historical rainfall datasets.
- Implement incremental data ingestion and storage.
- Introduce more extensive geospatial aggregation.
- Improve automated data quality monitoring.
- Add longer-term weather trend analysis.
- Integrate scheduled pipeline execution with the deployed application.

## Data Source

Weather observations are obtained from:

[Open-Meteo Weather API](https://open-meteo.com/)

## Author

**Athashree Badokar**

B.Tech — Data Science

GitHub: [@athashree08](https://github.com/athashree08)

Project Repository: [ThermoGrid](https://github.com/athashree08/thermogrid)

---

*ThermoGrid — Turning weather observations into structured geospatial intelligence.*
