"""
ThermoGrid — Geospatial Analytics Page
Spatial Indexing, Geohash Distribution & Numerical Weather Grid Snapping
"""

import streamlit as st
import pandas as pd
from dashboard.utils.data_loader import (
    load_weather_geospatial,
    load_weather_aggregated,
    load_locations_config
)
from dashboard.utils.metrics import (
    compute_geohash_summary
)
from dashboard.utils.charts import (
    create_geohash_boxplot,
    apply_dark_layout
)
import plotly.graph_objects as go


def render_geospatial_analytics():
    st.markdown('<div class="tg-brand-subtitle">Spatial Indexing & Aggregation Engine</div>', unsafe_allow_html=True)
    st.title("Geospatial Analytics")

    df_geo = load_weather_geospatial()
    df_agg = load_weather_aggregated()
    cfg_locations = load_locations_config()

    if df_geo.empty:
        st.error("No geospatial records available.")
        return

    # Prototype Disclaimer on Spatial Density
    st.markdown(
        """
        <div class="tg-prototype-banner">
            <b>Geospatial Prototype Architecture Notice:</b> In this current iteration, ThermoGrid uses 
            <b>one Open-Meteo numerical weather grid point per monitored city</b>. 
            Spatial aggregation in <code>src/processing/aggregation.py</code> groups by <code>(geohash, timestamp)</code>. 
            This validates the end-to-end geospatial indexing and partitioning pipeline without fabricating 
            multi-sensor spatial interpolations where only single-grid observations currently exist.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Educational Card: What is a Geohash?
    with st.expander("📘 Technical Architecture: What is a Geohash and Why Does ThermoGrid Use It?", expanded=False):
        st.markdown(
            """
            ### Understanding Geohash Spatial Encoding
            
            **Geohash** is a hierarchical spatial data structure invented by Gustavo Niemeyer in 2008. 
            It recursively subdivides the Earth's surface into a grid of bounding boxes, encoding the latitude 
            and longitude into a compact alphanumeric string using a base-32 character set (`0-9`, `b-z`, excluding `a`, `i`, `l`, `o`).
            
            #### Key Architectural Benefits in ThermoGrid:
            1. **High-Performance Spatial Indexing:** Geohashes convert 2D coordinates `(lat, lon)` into a 1D string. This enables standard B-Tree indexing, partition pruning, and fast key-value lookups in analytical storage.
            2. **Prefix Locality Property:** Two coordinates that share a common prefix (e.g., `te...`) are geographically proximate. This allows fast bounding-box queries with simple string prefix matching (`LIKE 'tek%'`).
            3. **Precision Level 6:** ThermoGrid uses precision 6, which delineates a bounding box of approximately **±0.61 km** (roughly 1.2 km × 0.6 km). This cell size corresponds well with urban weather modeling resolutions.
            4. **Grid Snapping Resolution:** Open-Meteo maps requested city centroids to its underlying numerical forecast model grid points. Geohashes index these true model coordinates, ensuring reproducible spatial join keys.
            """
        )

    # Spatial Grid Snapping Comparison Table
    st.markdown("### Numerical Grid Snapping: Requested vs Model Grid Points")
    st.caption("Illustrates the transformation from nominal city coordinates to API model grid coordinates and resulting precision-6 Geohashes.")

    grid_comparison = df_geo[[
        "city", "requested_latitude", "requested_longitude",
        "grid_latitude", "grid_longitude", "elevation_m", "geohash", "geohash_precision"
    ]].drop_duplicates().copy()

    # Calculate distance offset in km (approximate)
    grid_comparison["lat_delta"] = (grid_comparison["grid_latitude"] - grid_comparison["requested_latitude"]).abs()
    grid_comparison["lon_delta"] = (grid_comparison["grid_longitude"] - grid_comparison["requested_longitude"]).abs()
    # Approx distance formula
    grid_comparison["approx_offset_km"] = (
        ((grid_comparison["lat_delta"] * 111.0)**2 + (grid_comparison["lon_delta"] * 111.0 * 0.95)**2)**0.5
    ).round(2)

    st.dataframe(
        grid_comparison[[
            "city", "geohash", "requested_latitude", "requested_longitude",
            "grid_latitude", "grid_longitude", "approx_offset_km", "elevation_m"
        ]].rename(columns={
            "city": "City",
            "geohash": "Geohash (Prec 6)",
            "requested_latitude": "Requested Lat",
            "requested_longitude": "Requested Lon",
            "grid_latitude": "Model Grid Lat",
            "grid_longitude": "Model Grid Lon",
            "approx_offset_km": "Grid Snap Offset (km)",
            "elevation_m": "Elevation (m)"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Geohash Metric Distribution
    st.markdown("### Weather Metric Distribution by Geohash")
    
    col_dist1, col_dist2 = st.columns([1.5, 2.5])
    with col_dist1:
        metric_choice = st.selectbox(
            "Select Variable for Spatial Distribution:",
            options=[
                ("temperature_c", "Temperature (°C)"),
                ("humidity_percent", "Relative Humidity (%)"),
                ("wind_speed_kmh", "Wind Speed (km/h)"),
            ],
            format_func=lambda x: x[1],
            index=0
        )
        metric_k, metric_lbl = metric_choice

    box_fig = create_geohash_boxplot(df_geo, metric_k)
    st.plotly_chart(box_fig, use_container_width=True)

    # Geospatial Aggregation Inspector
    st.markdown("### Geospatial Aggregation Verification (`weather_aggregated.csv`)")
    st.caption("Verifies output from `src/processing/aggregation.py`, grouping by `(geohash, timestamp)`.")

    c_agg1, c_agg2, c_agg3 = st.columns(3)
    with c_agg1:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Input Geospatial Records</div>
                <div class="tg-metric-value">{len(df_geo)}</div>
                <div class="tg-metric-delta"><code>weather_geospatial.csv</code></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_agg2:
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Aggregated Output Records</div>
                <div class="tg-metric-value">{len(df_agg)}</div>
                <div class="tg-metric-delta"><code>weather_aggregated.csv</code></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_agg3:
        unique_gh = df_agg["geohash"].nunique()
        st.markdown(
            f"""
            <div class="tg-metric-box">
                <div class="tg-metric-label">Distinct Geohash Cells</div>
                <div class="tg-metric-value">{unique_gh} Cells</div>
                <div class="tg-metric-delta">24 Hourly Timesteps Each</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Interactive Geohash Inspector
    st.write("")
    st.markdown("#### Inspect Individual Geohash Cell")
    all_geohashes = sorted(df_geo["geohash"].unique().tolist())
    selected_gh = st.selectbox(
        "Select Geohash Identifier:",
        options=all_geohashes,
        format_func=lambda gh: f"{gh} ({df_geo[df_geo['geohash'] == gh]['city'].iloc[0]})"
    )

    gh_filtered = df_geo[df_geo["geohash"] == selected_gh].sort_values("timestamp")
    associated_city = gh_filtered["city"].iloc[0]

    st.markdown(f"**Selected Geohash:** `{selected_gh}` | **City Node:** **{associated_city}** | **Elevation:** {gh_filtered['elevation_m'].iloc[0]}m")

    # Line chart of the geohash's 24h temperature and humidity
    fig_gh = go.Figure()
    fig_gh.add_trace(go.Scatter(
        x=gh_filtered["timestamp"],
        y=gh_filtered["temperature_c"],
        name="Temperature (°C)",
        line={"color": "#38BDF8", "width": 2.5},
        yaxis="y1"
    ))
    fig_gh.add_trace(go.Scatter(
        x=gh_filtered["timestamp"],
        y=gh_filtered["humidity_percent"],
        name="Humidity (%)",
        line={"color": "#818CF8", "width": 2, "dash": "dash"},
        yaxis="y2"
    ))

    fig_gh.update_layout(
        title=f"Geohash {selected_gh} ({associated_city}) — Combined Temperature & Humidity Trend",
        yaxis={
            "title": "Temperature (°C)",
            "title_font": {"color": "#38BDF8"},
            "tickfont": {"color": "#38BDF8"},
        },
        yaxis2={
            "title": "Relative Humidity (%)",
            "title_font": {"color": "#818CF8"},
            "tickfont": {"color": "#818CF8"},
            "overlaying": "y",
            "side": "right",
            "range": [0, 100]
        }
    )
    fig_gh = apply_dark_layout(fig_gh, f"Geohash {selected_gh} ({associated_city}) Diurnal Curve")
    st.plotly_chart(fig_gh, use_container_width=True)


if __name__ == "__main__":
    render_geospatial_analytics()
