"""
ThermoGrid — Plotly Visualization Engine
Generates consistent, dark-themed geospatial weather analytics visualizations.
"""

from typing import List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Design Palette
DARK_BG = "#0B0F19"
CARD_BG = "#111827"
GRID_COLOR = "rgba(255, 255, 255, 0.07)"
TEXT_COLOR = "#F3F4F6"
SUBTEXT_COLOR = "#94A3B8"

CITY_COLORS = {
    "Pune": "#38BDF8",       # Sky cyan
    "Mumbai": "#818CF8",     # Indigo
    "Bengaluru": "#34D399",  # Emerald
    "Hyderabad": "#FBBF24",  # Amber
    "Delhi": "#F87171",      # Coral Red
    "National_Average": "#E2E8F0"
}


def apply_dark_layout(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    """Apply unified dark styling to any Plotly figure."""
    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 15, "color": TEXT_COLOR, "family": "sans-serif"},
            "x": 0.01,
            "xanchor": "left"
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17, 24, 39, 0.5)",
        height=height,
        margin={"l": 45, "r": 25, "t": 50, "b": 40},
        legend={
            "font": {"color": SUBTEXT_COLOR, "size": 11},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1.0,
            "bgcolor": "rgba(0,0,0,0)"
        },
        hoverlabel={
            "bgcolor": "#1F2937",
            "font_size": 12,
            "font_family": "sans-serif",
            "font_color": "#F9FAFB",
            "bordercolor": "rgba(255,255,255,0.15)"
        },
        xaxis={
            "gridcolor": GRID_COLOR,
            "tickfont": {"color": SUBTEXT_COLOR, "size": 10},
            "title_font": {"color": SUBTEXT_COLOR, "size": 11},
            "showline": True,
            "linecolor": GRID_COLOR,
        },
        yaxis={
            "gridcolor": GRID_COLOR,
            "tickfont": {"color": SUBTEXT_COLOR, "size": 10},
            "title_font": {"color": SUBTEXT_COLOR, "size": 11},
            "showline": True,
            "linecolor": GRID_COLOR,
        }
    )
    return fig


def create_temperature_trend_chart(df: pd.DataFrame, selected_cities: Optional[List[str]] = None) -> go.Figure:
    """
    Render 24-hour temperature trend lines for selected cities.
    """
    fig = go.Figure()

    if df.empty or "temperature_c" not in df.columns:
        return apply_dark_layout(fig, "No Temperature Data")

    cities = selected_cities or df["city"].unique().tolist()

    for city in cities:
        city_df = df[df["city"] == city].sort_values("timestamp")
        color = CITY_COLORS.get(city, "#38BDF8")

        fig.add_trace(go.Scatter(
            x=city_df["timestamp"],
            y=city_df["temperature_c"],
            mode="lines+markers",
            name=city,
            line={"color": color, "width": 2.2, "shape": "spline"},
            marker={"size": 4, "color": color},
            hovertemplate=f"<b>{city}</b><br>Time: %{{x|%H:%M UTC}}<br>Temp: <b>%{{y:.1f}} °C</b><extra></extra>"
        ))

    fig.update_xaxes(title="Observation Time (UTC)", tickformat="%H:%M")
    fig.update_yaxes(title="Temperature (°C)")
    return apply_dark_layout(fig, "24-Hour Temperature Trajectory Across Monitored Cities")


def create_city_metric_bar_chart(df: pd.DataFrame, metric: str = "temperature_c") -> go.Figure:
    """
    Render comparative bar chart showing Min, Avg, and Max for a given metric.
    """
    fig = go.Figure()

    if df.empty or metric not in df.columns:
        return apply_dark_layout(fig, f"No Data for {metric}")

    labels = {
        "temperature_c": ("Temperature (°C)", "City Temperature Profile (Min / Avg / Max)"),
        "humidity_percent": ("Relative Humidity (%)", "City Humidity Profile (Min / Avg / Max)"),
        "wind_speed_kmh": ("Wind Speed (km/h)", "City Wind Speed Profile (Min / Avg / Max)"),
        "precipitation_mm": ("Precipitation (mm)", "City Precipitation Summary")
    }
    unit, title = labels.get(metric, (metric, f"City Comparison ({metric})"))

    city_stats = df.groupby("city")[metric].agg(["min", "mean", "max"]).reset_index()

    fig.add_trace(go.Bar(
        x=city_stats["city"],
        y=city_stats["min"].round(1),
        name="Minimum",
        marker_color="rgba(56, 189, 248, 0.4)",
        hovertemplate="%{x}<br>Min: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=city_stats["city"],
        y=city_stats["mean"].round(1),
        name="Average",
        marker_color="#0284C7",
        hovertemplate="%{x}<br>Avg: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=city_stats["city"],
        y=city_stats["max"].round(1),
        name="Maximum",
        marker_color="#38BDF8",
        hovertemplate="%{x}<br>Max: %{y}<extra></extra>"
    ))

    fig.update_layout(barmode="group")
    fig.update_xaxes(title="City")
    fig.update_yaxes(title=unit)
    return apply_dark_layout(fig, title)


def create_humidity_comparison_chart(df: pd.DataFrame, selected_cities: Optional[List[str]] = None) -> go.Figure:
    """
    Render 24-hour humidity lines for selected cities.
    """
    fig = go.Figure()
    if df.empty or "humidity_percent" not in df.columns:
        return apply_dark_layout(fig, "No Humidity Data")

    cities = selected_cities or df["city"].unique().tolist()
    for city in cities:
        city_df = df[df["city"] == city].sort_values("timestamp")
        color = CITY_COLORS.get(city, "#818CF8")
        fig.add_trace(go.Scatter(
            x=city_df["timestamp"],
            y=city_df["humidity_percent"],
            mode="lines",
            name=city,
            line={"color": color, "width": 2, "dash": "solid"},
            hovertemplate=f"<b>{city}</b><br>Time: %{{x|%H:%M UTC}}<br>Humidity: <b>%{{y}}%</b><extra></extra>"
        ))

    fig.update_xaxes(title="Observation Time (UTC)", tickformat="%H:%M")
    fig.update_yaxes(title="Relative Humidity (%)", range=[0, 105])
    return apply_dark_layout(fig, "Relative Humidity Diurnal Cycle (%)")


def create_precipitation_chart(df: pd.DataFrame, selected_cities: Optional[List[str]] = None) -> go.Figure:
    """
    Render precipitation bar comparison.
    """
    fig = go.Figure()
    if df.empty or "precipitation_mm" not in df.columns:
        return apply_dark_layout(fig, "No Precipitation Data")

    cities = selected_cities or df["city"].unique().tolist()
    for city in cities:
        city_df = df[df["city"] == city].sort_values("timestamp")
        color = CITY_COLORS.get(city, "#34D399")
        fig.add_trace(go.Bar(
            x=city_df["timestamp"],
            y=city_df["precipitation_mm"],
            name=city,
            marker_color=color,
            hovertemplate=f"<b>{city}</b><br>Time: %{{x|%H:%M UTC}}<br>Precip: <b>%{{y}} mm</b><extra></extra>"
        ))

    fig.update_xaxes(title="Observation Time (UTC)", tickformat="%H:%M")
    fig.update_yaxes(title="Precipitation (mm)")
    return apply_dark_layout(fig, "Hourly Precipitation Distribution (mm)")


def create_wind_speed_chart(df: pd.DataFrame, selected_cities: Optional[List[str]] = None) -> go.Figure:
    """
    Render 24-hour wind speed lines.
    """
    fig = go.Figure()
    if df.empty or "wind_speed_kmh" not in df.columns:
        return apply_dark_layout(fig, "No Wind Speed Data")

    cities = selected_cities or df["city"].unique().tolist()
    for city in cities:
        city_df = df[df["city"] == city].sort_values("timestamp")
        color = CITY_COLORS.get(city, "#FBBF24")
        fig.add_trace(go.Scatter(
            x=city_df["timestamp"],
            y=city_df["wind_speed_kmh"],
            mode="lines",
            name=city,
            line={"color": color, "width": 1.8},
            hovertemplate=f"<b>{city}</b><br>Time: %{{x|%H:%M UTC}}<br>Wind: <b>%{{y:.1f}} km/h</b><extra></extra>"
        ))

    fig.update_xaxes(title="Observation Time (UTC)", tickformat="%H:%M")
    fig.update_yaxes(title="Wind Speed (km/h)")
    return apply_dark_layout(fig, "Wind Speed Variation (km/h)")


def create_geohash_boxplot(df: pd.DataFrame, metric: str = "temperature_c") -> go.Figure:
    """
    Render distribution of metric grouped by Geohash identifier.
    """
    fig = go.Figure()
    if df.empty or metric not in df.columns or "geohash" not in df.columns:
        return apply_dark_layout(fig, "No Geohash Data")

    geohashes = df["geohash"].unique()
    for gh in sorted(geohashes):
        gh_df = df[df["geohash"] == gh]
        city_name = gh_df["city"].iloc[0] if "city" in gh_df.columns else ""
        label = f"{gh} ({city_name})" if city_name else gh

        fig.add_trace(go.Box(
            y=gh_df[metric],
            name=label,
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8,
            marker={"size": 4, "color": "#38BDF8"},
            line={"width": 1.5, "color": "#0284C7"}
        ))

    unit_map = {
        "temperature_c": "Temperature (°C)",
        "humidity_percent": "Relative Humidity (%)",
        "wind_speed_kmh": "Wind Speed (km/h)",
        "precipitation_mm": "Precipitation (mm)"
    }
    unit = unit_map.get(metric, metric)
    fig.update_xaxes(title="Geohash Identifier (Precision 6)")
    fig.update_yaxes(title=unit)
    return apply_dark_layout(fig, f"Geospatial Metric Distribution by Geohash — {unit}")


def create_hourly_heatmap(df: pd.DataFrame, metric: str = "temperature_c") -> go.Figure:
    """
    Render an hour-of-day vs City matrix heatmap.
    """
    fig = go.Figure()
    if df.empty or metric not in df.columns or "city" not in df.columns:
        return apply_dark_layout(fig, "No Heatmap Data")

    df_copy = df.copy()
    df_copy["hour"] = df_copy["timestamp"].dt.strftime("%H:00")

    pivot = df_copy.pivot_table(index="city", columns="hour", values=metric, aggfunc="mean")

    fig.add_trace(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="Viridis",
        colorbar={"title": metric.replace("_", " ").title(), "tickfont": {"color": SUBTEXT_COLOR}},
        hovertemplate="City: <b>%{y}</b><br>Hour: %{x} UTC<br>Value: <b>%{z:.1f}</b><extra></extra>"
    ))

    fig.update_xaxes(title="Hour of Day (UTC)")
    fig.update_yaxes(title="Monitored City")
    return apply_dark_layout(fig, f"24-Hour Diurnal Heatmap Across Cities ({metric})", height=320)
