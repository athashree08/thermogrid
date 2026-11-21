"""
ThermoGrid — Weather Explorer Page
Interactive Map of India & City Deep-Dive Analytics
"""

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from dashboard.utils.data_loader import (
    load_weather_geospatial,
    load_locations_config
)
from dashboard.utils.map_utils import (
    build_pydeck_weather_map,
    build_folium_weather_map
)
from dashboard.utils.charts import (
    apply_dark_layout,
    CITY_COLORS
)
import plotly.graph_objects as go


def render_weather_explorer():
    st.markdown('<div class="tg-brand-subtitle">Geographic Observation Station</div>', unsafe_allow_html=True)
    st.title("Weather Explorer")

    df = load_weather_geospatial()
    locations_cfg = load_locations_config()

    if df.empty:
        st.error("No geospatial weather records loaded.")
        return

    all_cities = sorted(df["city"].unique().tolist())

    # Explorer Controls
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.5, 1.5, 1.2])

    with col_ctrl1:
        selected_city = st.selectbox(
            "Select City to Inspect:",
            options=["All Cities"] + all_cities,
            index=0,
            help="Zoom into a specific city node or inspect all 5 nodes concurrently."
        )

    with col_ctrl2:
        selected_metric = st.selectbox(
            "Focus Weather Variable:",
            options=[
                ("temperature_c", "Temperature (°C)"),
                ("humidity_percent", "Relative Humidity (%)"),
                ("wind_speed_kmh", "Wind Speed (km/h)"),
                ("precipitation_mm", "Precipitation (mm)"),
            ],
            format_func=lambda x: x[1],
            index=0
        )
        metric_col, metric_label = selected_metric

    with col_ctrl3:
        map_engine = st.radio(
            "Map Visualization Engine:",
            options=["PyDeck (3D)", "Folium (2D)"],
            horizontal=True
        )

    st.write("")

    # Map Rendering
    target_city = None if selected_city == "All Cities" else selected_city

    st.markdown("### Interactive Geospatial Station Map")
    st.caption("City markers sized and shaded by atmospheric values. Elevation shown via 3D columns.")

    if "PyDeck" in map_engine:
        deck_map = build_pydeck_weather_map(
            df=df,
            metric=metric_col,
            selected_city=target_city,
            map_style="dark"
        )
        st.pydeck_chart(deck_map, use_container_width=True)
    else:
        folium_map = build_folium_weather_map(
            df=df,
            selected_city=target_city
        )
        st_folium(folium_map, width="100%", height=450)

    st.markdown("---")

    # City-Specific Deep Dive Section
    if target_city:
        city_df = df[df["city"] == target_city].sort_values("timestamp")
        latest = city_df.iloc[-1]
        mean_val = city_df[metric_col].mean()
        min_val = city_df[metric_col].min()
        max_val = city_df[metric_col].max()
        std_val = city_df[metric_col].std()

        st.markdown(f"### {target_city} Weather Analysis Node")

        # Stat Cards for selected city
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(
                f"""
                <div class="tg-metric-box">
                    <div class="tg-metric-label">Latest {metric_label}</div>
                    <div class="tg-metric-value">{latest[metric_col]}</div>
                    <div class="tg-metric-delta">{latest['timestamp'].strftime('%H:%M UTC')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="tg-metric-box">
                    <div class="tg-metric-label">24h Mean</div>
                    <div class="tg-metric-value">{mean_val:.1f}</div>
                    <div class="tg-metric-delta">Daily Average</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f"""
                <div class="tg-metric-box">
                    <div class="tg-metric-label">24h Min / Max</div>
                    <div class="tg-metric-value" style="font-size: 1.3rem;">{min_val} / {max_val}</div>
                    <div class="tg-metric-delta">Diurnal Spread</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                f"""
                <div class="tg-metric-box">
                    <div class="tg-metric-label">Elevation & Geohash</div>
                    <div class="tg-metric-value" style="font-size: 1.2rem;">{latest['elevation_m']}m</div>
                    <div class="tg-metric-delta">Geohash: {latest['geohash']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c5:
            st.markdown(
                f"""
                <div class="tg-metric-box">
                    <div class="tg-metric-label">Grid Coordinates</div>
                    <div class="tg-metric-value" style="font-size: 1.05rem;">{latest['grid_latitude']:.2f}, {latest['grid_longitude']:.2f}</div>
                    <div class="tg-metric-delta">Snapping Offset Validated</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Time series chart for selected city vs national average
        national_avg = df.groupby("timestamp")[metric_col].mean().reset_index()

        fig = go.Figure()
        city_color = CITY_COLORS.get(target_city, "#38BDF8")

        fig.add_trace(go.Scatter(
            x=city_df["timestamp"],
            y=city_df[metric_col],
            mode="lines+markers",
            name=f"{target_city}",
            line={"color": city_color, "width": 3, "shape": "spline"},
            marker={"size": 6, "color": city_color},
            hovertemplate=f"<b>{target_city}</b><br>Time: %{{x|%H:%M UTC}}<br>{metric_label}: <b>%{{y}}</b><extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=national_avg["timestamp"],
            y=national_avg[metric_col],
            mode="lines",
            name="5-City Average",
            line={"color": "rgba(255, 255, 255, 0.4)", "width": 2, "dash": "dot"},
            hovertemplate=f"<b>National Avg</b><br>Time: %{{x|%H:%M UTC}}<br>{metric_label}: <b>%{{y:.1f}}</b><extra></extra>"
        ))

        fig.update_xaxes(title="Observation Time (UTC)", tickformat="%H:%M")
        fig.update_yaxes(title=metric_label)
        fig = apply_dark_layout(fig, f"{target_city} Hourly {metric_label} vs National Mean")
        st.plotly_chart(fig, use_container_width=True)

        # Tabular hourly log for selected city
        st.markdown(f"#### Complete 24-Hour Observation Log for {target_city}")
        log_cols = ["timestamp", "temperature_c", "humidity_percent", "precipitation_mm", "wind_speed_kmh", "elevation_m", "geohash"]
        st.dataframe(
            city_df[log_cols].rename(columns={
                "timestamp": "Timestamp (UTC)",
                "temperature_c": "Temperature (°C)",
                "humidity_percent": "Humidity (%)",
                "precipitation_mm": "Precipitation (mm)",
                "wind_speed_kmh": "Wind Speed (km/h)",
                "elevation_m": "Elevation (m)",
                "geohash": "Geohash"
            }),
            use_container_width=True,
            hide_index=True
        )

    else:
        # Overview across all cities
        st.markdown("### All Monitored Cities Metric Matrix")
        summary_pivot = df.pivot(index="timestamp", columns="city", values=metric_col)
        summary_pivot.index = summary_pivot.index.strftime("%H:%M UTC")
        st.dataframe(summary_pivot, use_container_width=True)


if __name__ == "__main__":
    render_weather_explorer()

