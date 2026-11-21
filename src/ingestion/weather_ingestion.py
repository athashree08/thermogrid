
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = BASE_DIR / "config" / "locations.json"
RAW_DIR = BASE_DIR / "data" / "raw"

API_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def load_locations():
    """Load geographic locations from configuration."""

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def fetch_weather(location):
    """Fetch hourly weather observations for a location."""

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "hourly": ",".join(WEATHER_VARIABLES),
        "forecast_days": 1,
        "timezone": "UTC"
    }

    for attempt in range(1, 4):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            logger.info(
                "Successfully fetched weather for %s",
                location["city"]
            )

            return data

        except requests.RequestException as error:

            logger.warning(
                "Attempt %s failed for %s: %s",
                attempt,
                location["city"],
                error
            )

            if attempt == 3:
                raise

            time.sleep(2 ** attempt)


def save_raw_data(location, data):
    """Save the original API response as JSON."""

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    city = location["city"].lower()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    filename = f"{city}_{timestamp}.json"

    output_path = RAW_DIR / filename

    record = {
        "city": location["city"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": "Open-Meteo",
        "weather_data": data
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(record, file, indent=4)

    logger.info("Saved raw data: %s", output_path)

    return output_path


def run_ingestion():
    """Execute weather ingestion for all configured locations."""

    locations = load_locations()

    successful = 0
    failed = []

    for location in locations:

        try:
            data = fetch_weather(location)

            save_raw_data(location, data)

            successful += 1

        except Exception as error:

            logger.error(
                "Ingestion failed for %s: %s",
                location["city"],
                error
            )

            failed.append(location["city"])

    logger.info("Ingestion completed")
    logger.info("Successful locations: %s", successful)
    logger.info("Failed locations: %s", failed)

    if failed:
        raise RuntimeError(
            f"Weather ingestion incomplete. Failed: {failed}"
        )


if __name__ == "__main__":
    run_ingestion()
