import os
import requests
import csv

TOKEN = os.getenv("GFW_API_TOKEN")

if not TOKEN:
    print("ERROR: GFW_API_TOKEN not found.")
    raise SystemExit(1)

URL = "https://gateway.api.globalfishingwatch.org/v3/4wings/report"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

MIN_LAT = -20.50
MAX_LAT = -20.25
MIN_LON = 57.60
MAX_LON = 57.85

geojson = {
    "type": "Polygon",
    "coordinates": [[
        [MIN_LON, MIN_LAT],
        [MAX_LON, MIN_LAT],
        [MAX_LON, MAX_LAT],
        [MIN_LON, MAX_LAT],
        [MIN_LON, MIN_LAT]
    ]]
}

params = {
    "spatial-resolution": "HIGH",
    "temporal-resolution": "HOURLY",
    "group-by": "MMSI",
    "datasets[0]": "public-global-presence:latest",
    "date-range": "2020-08-09,2020-08-11",
    "format": "JSON",
    "spatial-aggregation": "false"
}

body = {
    "geojson": geojson
}

print("Querying GFW AIS vessel presence...")
print("--------------------------------------")

response = requests.post(
    URL,
    headers=headers,
    params=params,
    json=body,
    timeout=120
)

print("HTTP status:", response.status_code)

if not response.ok:
    print(response.text[:5000])
    raise SystemExit(1)

data = response.json()

# Extract dataset results
dataset_key = "public-global-presence:v4.0"

entries = data.get("entries", [])

records = []

for entry in entries:

    dataset_records = entry.get(dataset_key, [])

    for record in dataset_records:

        records.append({
            "date": record.get("date"),
            "entryTimestamp": record.get("entryTimestamp"),
            "exitTimestamp": record.get("exitTimestamp"),
            "hours": record.get("hours"),
            "lat": record.get("lat"),
            "lon": record.get("lon"),
            "mmsi": record.get("mmsi")
        })

print("\nAIS records extracted:", len(records))

# Save all AIS records
output_file = r"results\wakashio_detection\ais_presence.csv"

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "date",
            "entryTimestamp",
            "exitTimestamp",
            "hours",
            "lat",
            "lon",
            "mmsi"
        ]
    )

    writer.writeheader()
    writer.writerows(records)

# Unique vessels
unique_mmsi = sorted(
    set(
        record["mmsi"]
        for record in records
        if record["mmsi"]
    )
)

print("Unique MMSIs:", len(unique_mmsi))

print("\nUnique vessels:")
print("----------------")

for mmsi in unique_mmsi:
    count = sum(1 for r in records if r["mmsi"] == mmsi)
    print(f"{mmsi} -> {count} AIS presence records")

print("\nOutput:")
print(output_file)

print("\nAIS presence extraction completed successfully!")
