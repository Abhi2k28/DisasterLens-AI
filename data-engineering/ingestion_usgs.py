import json
import requests
from datetime import datetime, timezone


URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"

OUTPUT_FILE = "data/raw/usgs_reports.json"


response = requests.get(URL, timeout=15)
response.raise_for_status()

data = response.json()

features = data.get("features", [])

print("USGS records received:", len(features))


usgs_reports = []

for feature in features:
    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})

    coordinates = geometry.get("coordinates", [None, None, None])

    place = properties.get("place")
    magnitude = properties.get("mag")
    timestamp_ms = properties.get("time")

    if timestamp_ms:
        timestamp = datetime.fromtimestamp(
            timestamp_ms / 1000,
            tz=timezone.utc
        ).isoformat()
    else:
        timestamp = None

    report = {
        "source": "usgs",
        "source_id": feature.get("id"),
        "text": f"Earthquake detected near {place}",
        "magnitude": magnitude,
        "timestamp": timestamp,
        "url": properties.get("url"),
        "location": place,
        "latitude": coordinates[1],
        "longitude": coordinates[0]
    }

    usgs_reports.append(report)


with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(usgs_reports, file, indent=2)


print("Normalized USGS reports saved:", len(usgs_reports))
print("Output file:", OUTPUT_FILE)