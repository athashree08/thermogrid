"""
ThermoGrid — Geospatial Mapping Utility
Builds high-performance interactive 2D and 3D maps using PyDeck and Folium.
"""

from typing import Any, Dict, List, Optional
import folium
import numpy as np
import pandas as pd
import pydeck as pdk

# Map Styling Defaults
INDIA_CENTER_LAT = 20.5937
INDIA_CENTER_LON = 78.9629
DEFAULT_ZOOM = 4.2


def get_temperature_color(temp: float, min_temp: float = 12.0, max_temp: float = 35.0) -> List[int]:
    """
    Map temperature value to an RGB color ramp:
    Cool Cyan/Blue -> Teal -> Green -> Yellow -> Orange -> Crimson Red
    """
    # Normalize between 0 and 1
    norm = np.clip((temp - min_temp) / (max_temp - min_temp + 1e-5), 0.0, 1.0)

    # Color stops
    # 0.0: [56, 189, 248] (Cyan)
    # 0.33: [52, 211, 153] (Emerald)
    # 0.66: [251, 191, 36] (Amber)
    # 1.0: [239, 68, 68] (Crimson)
    if norm < 0.33:
        t = norm / 0.33
        r = int(56 + t * (52 - 56))
        g = int(189 + t * (211 - 189))
        b = int(248 + t * (153 - 248))
    elif norm < 0.66:
        t = (norm - 0.33) / 0.33
        r = int(52 + t * (251 - 52))
        g = int(211 + t * (191 - 211))
        b = int(153 + t * (36 - 153))
    else:
        t = (norm - 0.66) / 0.34
        r = int(251 + t * (239 - 251))
        g = int(191 + t * (68 - 191))
        b = int(36 + t * (68 - 36))

    return [r, g, b, 220]


def build_pydeck_weather_map(
    df: pd.DataFrame,
    metric: str = "temperature_c",
    selected_city: Optional[str] = None,
    map_style: str = "dark"
) -> pdk.Deck:
    """
    Build an interactive PyDeck map with Scatterplot and 3D Column layers.
    """
    if df.empty:
        return pdk.Deck()

    # Aggregate latest or average metrics per city
    city_map_data = (
        df.groupby(["city", "grid_latitude", "grid_longitude", "geohash", "elevation_m"])
        .agg(
            latest_temp=("temperature_c", "last"),
            avg_temp=("temperature_c", "mean"),
            latest_humidity=("humidity_percent", "last"),
            latest_wind=("wind_speed_kmh", "last"),
            total_precip=("precipitation_mm", "sum"),
        )
        .reset_index()
    )

    min_t = city_map_data["avg_temp"].min()
    max_t = city_map_data["avg_temp"].max()

    city_map_data["color"] = city_map_data["avg_temp"].apply(
        lambda t: get_temperature_color(t, min_t, max_t)
    )

    # Marker radius: highlight selected city
    city_map_data["radius"] = city_map_data["city"].apply(
        lambda c: 65000 if c == selected_city else 45000
    )
    city_map_data["elevation"] = city_map_data["elevation_m"] * 250

    # If a city is selected, center map on that city
    if selected_city and selected_city in city_map_data["city"].values:
        row = city_map_data[city_map_data["city"] == selected_city].iloc[0]
        view_lat = float(row["grid_latitude"])
        view_lon = float(row["grid_longitude"])
        zoom = 6.8
    else:
        view_lat = INDIA_CENTER_LAT
        view_lon = INDIA_CENTER_LON
        zoom = DEFAULT_ZOOM

    view_state = pdk.ViewState(
        latitude=view_lat,
        longitude=view_lon,
        zoom=zoom,
        pitch=35 if selected_city else 20,
        bearing=0
    )

    # Outer glow ring layer
    glow_data = city_map_data.copy()
    glow_data["glow_radius"] = glow_data["radius"] * 1.6
    glow_data["glow_color"] = glow_data["color"].apply(lambda c: [c[0], c[1], c[2], 75])

    glow_layer = pdk.Layer(
        "ScatterplotLayer",
        glow_data,
        get_position=["grid_longitude", "grid_latitude"],
        get_color="glow_color",
        get_radius="glow_radius",
        pickable=False,
    )

    # Core point scatter layer
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        city_map_data,
        get_position=["grid_longitude", "grid_latitude"],
        get_color="color",
        get_radius="radius",
        pickable=True,
        auto_highlight=True,
    )

    # 3D Elevation Column Layer
    column_layer = pdk.Layer(
        "ColumnLayer",
        city_map_data,
        get_position=["grid_longitude", "grid_latitude"],
        get_elevation="elevation",
        elevation_scale=1,
        radius=15000,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
    )

    tooltip = {
        "html": """
        <div style="background-color: #0F172A; padding: 10px 14px; border-radius: 6px; border: 1px solid #38BDF8; color: #F8FAFC; font-family: sans-serif; font-size: 12px; line-height: 1.5;">
            <b style="font-size: 14px; color: #38BDF8;">{city}</b><br/>
            <b>Geohash:</b> <span style="color: #34D399;">{geohash}</span><br/>
            <b>Grid Coordinates:</b> {grid_latitude}, {grid_longitude}<br/>
            <b>Elevation:</b> {elevation_m} m<br/>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 6px 0;" />
            <b>Latest Temp:</b> <span style="color: #FBBF24;">{latest_temp} °C</span> (Avg: {avg_temp} °C)<br/>
            <b>Humidity:</b> {latest_humidity}%<br/>
            <b>Wind Speed:</b> {latest_wind} km/h<br/>
            <b>Precipitation:</b> {total_precip} mm
        </div>
        """,
        "style": {"color": "white"}
    }

    style_url = "mapbox://styles/mapbox/dark-v11" if map_style == "dark" else "mapbox://styles/mapbox/light-v10"

    deck = pdk.Deck(
        layers=[glow_layer, column_layer, scatter_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=style_url
    )
    return deck


def build_folium_weather_map(
    df: pd.DataFrame,
    selected_city: Optional[str] = None
) -> folium.Map:
    """
    Build an alternative Folium map with OpenStreetMap CartoDB Dark basemap.
    """
    center_lat = INDIA_CENTER_LAT
    center_lon = INDIA_CENTER_LON
    zoom = 5

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True
    )

    if df.empty:
        return m

    city_summary = (
        df.groupby(["city", "grid_latitude", "grid_longitude", "geohash", "elevation_m"])
        .agg(
            avg_temp=("temperature_c", "mean"),
            avg_hum=("humidity_percent", "mean"),
            avg_wind=("wind_speed_kmh", "mean"),
            total_precip=("precipitation_mm", "sum"),
        )
        .reset_index()
    )

    for _, row in city_summary.iterrows():
        city = row["city"]
        lat = row["grid_latitude"]
        lon = row["grid_longitude"]
        gh = row["geohash"]
        temp = round(row["avg_temp"], 1)
        hum = round(row["avg_hum"], 1)
        wind = round(row["avg_wind"], 1)
        elev = row["elevation_m"]

        is_selected = (city == selected_city)
        color = "#38BDF8" if is_selected else "#0284C7"
        radius = 16 if is_selected else 11

        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px; color: #0F172A;">
            <h4 style="margin: 0 0 6px 0; color: #0284C7;">{city}</h4>
            <b>Geohash:</b> {gh}<br/>
            <b>Grid Coords:</b> ({lat:.4f}, {lon:.4f})<br/>
            <b>Elevation:</b> {elev} m<br/>
            <b>Avg Temp:</b> {temp} °C<br/>
            <b>Avg Humidity:</b> {hum}%<br/>
            <b>Avg Wind:</b> {wind} km/h
        </div>
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color="#38BDF8" if is_selected else "#60A5FA",
            weight=3 if is_selected else 1.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{city} ({gh}): {temp}°C | {hum}% Hum"
        ).add_to(m)

    return m
