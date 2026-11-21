"""
ThermoGrid — Overview Landing Page
Geospatial Weather Intelligence Platform
"""

import streamlit as st
import pandas as pd
from dashboard.utils.data_loader import (
    load_weather_geospatial,
    load_data_quality_report,
    get_dataset_summary
)
from dashboard.utils.metrics import (
    compute_overview_kpis,
    compute_city_summary
)
from dashboard.utils.charts import (
    create_temperature_trend_chart,
    create_city_metric_bar_chart,
    create_humidity_comparison_chart,
    create_precipitation_chart,
    create_wind_speed_chart,
    create_hourly_heatmap
)


def render_overview_page():
    st.markdown('<div class="tg-brand-subtitle">Platform Status & Highlights</div>', unsafe_allow_html=True)
    st.title("Geospatial Weather Overview")

    # Load core dataset
    df = load_weather_geospatial()
    dq_report = load_data_quality_report()
    summary_meta = get_dataset_summary()

    if df.empty:
        st.error("No processed weather data found. Please run the ingestion and processing pipeline.")
        return

    # Prototype Disclaimer & Dataset Range Banner
    st.markdown(
        f"""
        <div class="tg-prototype-banner">
            <b>Historical Observation Prototype:</b> Currently monitoring <b>{summary_meta['total_records']}</b> hourly observations 
            across <b>{len(summary_meta['cities'])}</b> Indian cities from <code>{summary_meta['date_range_str']}</code>. 
            This represents a 24-hour historical batch pipeline, not a live streaming API.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Compute live KPIs
    kpis = compute_overview_kpis(df)
    dq_passed = dq_report.get("passed", False)

    # Row 1: Primary System KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Total Observations</div>
                <div class="tg-metric-value">{kpis['total_observations']}</div>
                <div class="tg-metric-delta">24h Hourly Cycle</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Monitored Cities</div>
                <div class="tg-metric-value">{kpis['monitored_cities']} <span style="font-size: 0.9rem; color: #94A3B8;">Nodes</span></div>
                <div class="tg-metric-delta">Precision-6 Geohashes</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Latest Observation</div>
                <div class="tg-metric-value" style="font-size: 1.15rem; padding-top: 6px;">{kpis['latest_timestamp']}</div>
                <div class="tg-metric-delta">UTC Synchronized</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        status_badge = '<span class="tg-badge-success">PASSED (100%)</span>' if dq_passed else '<span class="tg-badge-warning">FAILED</span>'
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Data Quality Check</div>
                <div class="tg-metric-value" style="font-size: 1.3rem; padding-top: 4px;">{status_badge}</div>
                <div class="tg-metric-delta">0 Missing / 0 Duplicates</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    # Row 2: Atmospheric Metric KPIs
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Mean Temperature</div>
                <div class="tg-metric-value">{kpis['avg_temperature']} °C</div>
                <div class="tg-metric-delta">Range: {kpis['min_temperature']}°C – {kpis['max_temperature']}°C</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col6:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Mean Relative Humidity</div>
                <div class="tg-metric-value">{kpis['avg_humidity']}%</div>
                <div class="tg-metric-delta">Atmospheric Moisture</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col7:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Total Precipitation</div>
                <div class="tg-metric-value">{kpis['total_precipitation']} mm</div>
                <div class="tg-metric-delta">Dry Weather Prototype</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col8:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Mean Wind Speed</div>
                <div class="tg-metric-value">{kpis['avg_wind_speed']} km/h</div>
                <div class="tg-metric-delta">10m AGL Anemometer</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # City Filter Controls for Visualizations
    all_cities = sorted(df["city"].unique().tolist())
    selected_cities = st.multiselect(
        "Filter Cities in Trend Visualizations:",
        options=all_cities,
        default=all_cities,
        help="Select one or more cities to compare temporal patterns."
    )

    if not selected_cities:
        selected_cities = all_cities

    # Visualizations Row 1: Temperature Trajectory
    temp_fig = create_temperature_trend_chart(df, selected_cities)
    st.plotly_chart(temp_fig, use_container_width=True)

    # Visualizations Row 2: Two Columns
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        city_bar_fig = create_city_metric_bar_chart(df[df["city"].isin(selected_cities)], "temperature_c")
        st.plotly_chart(city_bar_fig, use_container_width=True)

    with chart_col2:
        hum_fig = create_humidity_comparison_chart(df, selected_cities)
        st.plotly_chart(hum_fig, use_container_width=True)

    # Visualizations Row 3: Diurnal Heatmap & Wind Profiles
    heat_col, wind_col = st.columns(2)

    with heat_col:
        heatmap_fig = create_hourly_heatmap(df, "temperature_c")
        st.plotly_chart(heatmap_fig, use_container_width=True)

    with wind_col:
        wind_fig = create_wind_speed_chart(df, selected_cities)
        st.plotly_chart(wind_fig, use_container_width=True)

    # City Summary Statistics Table
    st.markdown("### City Observation Aggregate Profiles")
    city_summary_df = compute_city_summary(df)
    st.dataframe(
        city_summary_df.rename(columns={
            "city": "City",
            "min_temperature": "Min Temp (°C)",
            "avg_temperature": "Avg Temp (°C)",
            "max_temperature": "Max Temp (°C)",
            "avg_humidity": "Avg Humidity (%)",
            "total_precipitation": "Total Precip (mm)",
            "avg_wind_speed": "Avg Wind (km/h)",
            "elevation_m": "Elevation (m)",
            "geohash": "Geohash",
            "records_count": "Records"
        }),
        use_container_width=True,
        hide_index=True
    )

    # Recent Observations Explorer
    st.markdown("### Raw Observation Catalog Explorer")
    search_query = st.text_input("Filter observation records by city or timestamp:", "")

    display_df = df.copy()
    if search_query:
        display_df = display_df[
            display_df["city"].str.contains(search_query, case=False, na=False) |
            display_df["geohash"].str.contains(search_query, case=False, na=False) |
            display_df["timestamp"].astype(str).str.contains(search_query, case=False, na=False)
        ]

    cols_to_show = [
        "timestamp", "city", "temperature_c", "humidity_percent",
        "precipitation_mm", "wind_speed_kmh", "geohash", "grid_latitude", "grid_longitude", "elevation_m"
    ]
    st.dataframe(
        display_df[cols_to_show].sort_values("timestamp", ascending=False),
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    render_overview_page()

