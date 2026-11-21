"""
ThermoGrid — Geospatial Weather Intelligence Platform
Main Streamlit Application Controller
"""

from pathlib import Path
import importlib
import streamlit as st

# Configure Application Page Settings
st.set_page_config(
    page_title="ThermoGrid | Geospatial Weather Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS Stylesheet
CSS_PATH = Path(__file__).resolve().parent / "assets" / "styles.css"
if CSS_PATH.exists():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def build_sidebar():
    """Render branded ThermoGrid sidebar header and platform metadata."""
    with st.sidebar:
        st.markdown(
            """
            <div class="tg-sidebar-brand">
                <div class="tg-brand-title">
                    <span style="color: #38BDF8;">🌐</span> ThermoGrid
                </div>
                <div class="tg-brand-subtitle">
                    Geospatial Weather Intelligence Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="font-size: 0.78rem; color: #94A3B8; background: rgba(17, 24, 39, 0.6); padding: 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 16px;">
                <div style="margin-bottom: 6px;"><b style="color: #F1F5F9;">Target Nodes:</b> 5 Indian Cities</div>
                <div style="margin-bottom: 6px;"><b style="color: #F1F5F9;">Resolution:</b> Precision-6 Geohash</div>
                <div style="margin-bottom: 6px;"><b style="color: #F1F5F9;">Storage:</b> Snappy Parquet</div>
                <div style="margin-bottom: 6px;"><b style="color: #F1F5F9;">Pipeline:</b> Apache Airflow</div>
                <div><b style="color: #F1F5F9;">Data Source:</b> Open-Meteo API</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def main():
    """Application entry point and multi-page routing."""
    build_sidebar()

    # Dynamically import page modules
    overview_mod = importlib.import_module("dashboard.pages.1_Overview")
    explorer_mod = importlib.import_module("dashboard.pages.2_Weather_Explorer")
    geospatial_mod = importlib.import_module("dashboard.pages.3_Geospatial_Analytics")
    quality_mod = importlib.import_module("dashboard.pages.4_Data_Quality")
    pipeline_mod = importlib.import_module("dashboard.pages.5_Pipeline_Monitor")

    pages = [
        st.Page(
            overview_mod.render_overview_page,
            title="Overview",
            icon=":material/dashboard:",
            default=True
        ),
        st.Page(
            explorer_mod.render_weather_explorer,
            title="Weather Explorer",
            icon=":material/explore:"
        ),
        st.Page(
            geospatial_mod.render_geospatial_analytics,
            title="Geospatial Analytics",
            icon=":material/public:"
        ),
        st.Page(
            quality_mod.render_data_quality,
            title="Data Quality",
            icon=":material/verified:"
        ),
        st.Page(
            pipeline_mod.render_pipeline_monitor,
            title="Pipeline Monitor",
            icon=":material/account_tree:"
        ),
    ]

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()

