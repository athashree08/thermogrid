"""
ThermoGrid — Pipeline Monitor & Orchestration View
Displays Apache Airflow DAG architecture, stage definitions, artifact status, and Parquet storage.
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import pyarrow.parquet as pq

from dashboard.utils.data_loader import (
    get_pipeline_artifacts_status,
    check_airflow_status,
    get_project_root
)


def render_pipeline_monitor():
    st.markdown('<div class="tg-brand-subtitle">Workflow Orchestration & Lineage</div>', unsafe_allow_html=True)
    st.title("Airflow Pipeline Monitor")

    project_root = get_project_root()
    airflow_info = check_airflow_status()
    artifacts_status = get_pipeline_artifacts_status()

    # Airflow Live Status Indicator
    if airflow_info["available"]:
        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;">
                <span class="tg-badge-success">AIRFLOW API ONLINE</span>
                <span style="margin-left: 10px; color: #E2E8F0;">Connected to Apache Airflow server at <code>{airflow_info['url']}</code> (HTTP {airflow_info['status_code']})</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(255, 255, 255, 0.1); border-left: 4px solid #94A3B8; border-radius: 6px; padding: 14px 18px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <b style="color: #F8FAFC;">Orchestrator Execution API Status:</b>
                        <span style="color: #94A3B8; margin-left: 8px;">Airflow standalone server is not currently running locally.</span>
                    </div>
                    <span class="tg-badge-info">DECOUPLED DATA LAKE MODE</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.82rem; margin-top: 6px;">
                    The dashboard operates completely independently from the Airflow daemon, reading static processed datasets directly from storage artifacts.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # DAG Metadata Overview
    st.markdown("### DAG Architecture: `thermogrid_weather_pipeline`")
    st.caption("Configured in `dags/thermogrid_pipeline.py`. Sequential execution graph of 6 data engineering tasks.")

    dag_c1, dag_c2, dag_c3, dag_c4 = st.columns(4)
    with dag_c1:
        st.markdown(
            """
            <div class="tg-metric-box">
                <div class="tg-metric-label">DAG Identifier</div>
                <div class="tg-metric-value" style="font-size: 1.05rem;">thermogrid_weather_pipeline</div>
                <div class="tg-metric-delta">Sequential DAG</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with dag_c2:
        st.markdown(
            """
            <div class="tg-metric-box">
                <div class="tg-metric-label">Schedule Interval</div>
                <div class="tg-metric-value" style="font-size: 1.2rem;">None (Manual)</div>
                <div class="tg-metric-delta">Triggered on-demand</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with dag_c3:
        st.markdown(
            """
            <div class="tg-metric-box">
                <div class="tg-metric-label">Pipeline Tasks</div>
                <div class="tg-metric-value">6 Stages</div>
                <div class="tg-metric-delta">BashOperator Tasks</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with dag_c4:
        st.markdown(
            """
            <div class="tg-metric-box">
                <div class="tg-metric-label">Storage Engine</div>
                <div class="tg-metric-value" style="font-size: 1.2rem;">Apache Parquet</div>
                <div class="tg-metric-delta">Snappy Partitioned</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Visual Workflow Representation
    st.markdown("#### Sequential Pipeline Execution Graph")
    st.markdown(
        """
        <div style="background: rgba(17, 24, 39, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 18px; margin-bottom: 24px; text-align: center; overflow-x: auto;">
            <div style="display: inline-flex; align-items: center; gap: 8px; font-size: 0.82rem; font-family: monospace;">
                <span style="background: #1E293B; border: 1px solid #38BDF8; color: #38BDF8; padding: 6px 12px; border-radius: 4px;">1. weather_ingestion</span>
                <span style="color: #64748B;">➔</span>
                <span style="background: #1E293B; border: 1px solid #38BDF8; color: #38BDF8; padding: 6px 12px; border-radius: 4px;">2. transform_weather</span>
                <span style="color: #64748B;">➔</span>
                <span style="background: #1E293B; border: 1px solid #38BDF8; color: #38BDF8; padding: 6px 12px; border-radius: 4px;">3. generate_geohash</span>
                <span style="color: #64748B;">➔</span>
                <span style="background: #1E293B; border: 1px solid #38BDF8; color: #38BDF8; padding: 6px 12px; border-radius: 4px;">4. aggregate_weather</span>
                <span style="color: #64748B;">➔</span>
                <span style="background: #1E293B; border: 1px solid #38BDF8; color: #38BDF8; padding: 6px 12px; border-radius: 4px;">5. store_parquet</span>
                <span style="color: #64748B;">➔</span>
                <span style="background: #1E293B; border: 1px solid #10B981; color: #34D399; padding: 6px 12px; border-radius: 4px;">6. validate_data</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Artifact Verification Table
    st.markdown("### Stage Execution Details & Actual Artifact Verification")
    st.caption("Inspects actual file outputs generated on the filesystem for each pipeline task.")

    artifact_display_data = []
    for item in artifacts_status:
        artifact_display_data.append({
            "Stage #": item["stage_id"],
            "Task ID": item["task_id"],
            "Stage Name": item["name"],
            "Source Module": item["source_module"],
            "Artifact Path": str(item["artifact_path"].relative_to(project_root)),
            "Status": "✓ Present" if item["exists"] else "✕ Missing",
            "Artifact Size": f"{item['size_kb']} KB" if item["exists"] else "N/A",
            "Item / Record Count": item["item_count"] if item["exists"] else "N/A",
            "Last Modified": item["last_modified"] if item["exists"] else "N/A"
        })

    st.dataframe(pd.DataFrame(artifact_display_data), use_container_width=True, hide_index=True)

    # Detailed Explanations for Each Stage
    st.markdown("### Task Logic & Architectural Specification")

    stages_spec = [
        ("1. weather_ingestion (`src/ingestion/weather_ingestion.py`)",
         "Queries the Open-Meteo REST API for 5 configured cities (Pune, Mumbai, Bengaluru, Hyderabad, Delhi). Uses an exponential backoff retry mechanism (up to 3 attempts). Saves raw JSON payloads with ingestion metadata to `data/raw/`."),

        ("2. transform_weather (`src/processing/transform.py`)",
         "Parses raw JSON responses, flattens nested hourly measurements into tabular format, standardizes column nomenclature (`temperature_c`, `humidity_percent`, etc.), parses UTC timestamps, and deduplicates records on `(city, time)`, preserving the latest ingestion. Output is saved to `data/processed/weather_catalog.csv`."),

        ("3. generate_geohash (`src/processing/geospatial.py`)",
         "Encodes model grid coordinates `(grid_latitude, grid_longitude)` into precision-6 Geohashes using the base-32 `geohash2` algorithm (~±0.61 km spatial resolution). Appends `geohash` and `geohash_precision` columns. Output is written to `data/processed/weather_geospatial.csv`."),

        ("4. aggregate_weather (`src/processing/aggregation.py`)",
         "Executes geospatial aggregation grouping by `(geohash, timestamp)`. Calculates arithmetic mean for weather observations, spatial coordinates, and elevation. Output is saved to `data/processed/weather_aggregated.csv`."),

        ("5. store_parquet (`src/storage/parquet_storage.py`)",
         "Transforms aggregated records into Apache Arrow Tables. Partitions observations hierarchically by `year`, `month`, and `day` using Snappy compression under `data/processed/parquet/`."),

        ("6. validate_data (`src/validation/data_quality.py`)",
         "Executes 8 automated data quality verification checks: required columns, null counts, key uniqueness, physical temperature bounds (-90 to 65 °C), relative humidity bounds (0 to 100%), non-negative precipitation, non-negative wind speed, and coordinate limits. Exports audit report to `data/reports/data_quality_report.json`.")
    ]

    for title, desc in stages_spec:
        with st.expander(title, expanded=False):
            st.write(desc)

    # Parquet Storage Deep-Dive
    st.markdown("### Parquet Columnar Storage Inspector")
    parquet_dir = project_root / "data" / "processed" / "parquet"

    if parquet_dir.exists():
        parquet_files = list(parquet_dir.rglob("*.parquet"))
        st.write(f"Found **{len(parquet_files)}** Parquet partition file(s) in `{parquet_dir.relative_to(project_root)}`.")

        if parquet_files:
            sample_file = parquet_files[0]
            pq_meta = pq.read_metadata(str(sample_file))
            pq_schema = pq.read_schema(str(sample_file))

            c_pq1, c_pq2 = st.columns(2)
            with c_pq1:
                st.markdown("#### Parquet Schema & Types")
                schema_df = pd.DataFrame([
                    {"Column": name, "Arrow Data Type": str(pq_schema.field(name).type)}
                    for name in pq_schema.names
                ])
                st.dataframe(schema_df, use_container_width=True, hide_index=True)

            with c_pq2:
                st.markdown("#### Storage Metadata")
                meta_info = {
                    "File Path": str(sample_file.relative_to(project_root)),
                    "Row Count": pq_meta.num_rows,
                    "Column Count": pq_meta.num_columns,
                    "Compression": "SNAPPY",
                    "Partition Hierarchy": "year=2026 / month=11 / day=21",
                    "Serialized Size": f"{round(sample_file.stat().st_size / 1024, 2)} KB"
                }
                for k, v in meta_info.items():
                    st.write(f"**{k}:** `{v}`")


if __name__ == "__main__":
    render_pipeline_monitor()

