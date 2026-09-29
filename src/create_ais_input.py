import os
import csv
from datetime import datetime, timedelta

INPUT = r"results\wakashio_detection\maris_candidate_evidence.csv"
OUTPUT = r"results\wakashio_detection\ais_correlation_input.csv"

# Sentinel-1 acquisition time
ACQUISITION_TIME = datetime.fromisoformat(
    "2020-08-10T01:37:55+00:00"
)

# AIS search window around satellite observation.
# We use a wider window because vessel movement before/after
# the satellite observation can be relevant.
WINDOW_BEFORE_HOURS = 24
WINDOW_AFTER_HOURS = 24

window_start = ACQUISITION_TIME - timedelta(
    hours=WINDOW_BEFORE_HOURS
)

window_end = ACQUISITION_TIME + timedelta(
    hours=WINDOW_AFTER_HOURS
)

# Read MARIS master evidence
with open(INPUT, newline="") as f:
    rows = list(csv.DictReader(f))

ais_rows = []

for row in rows:

    ais_rows.append({
        "candidate_id": row["candidate_id"],

        # Spill candidate location
        "spill_latitude": row["latitude"],
        "spill_longitude": row["longitude"],

        # Satellite observation
        "satellite": "Sentinel-1B",
        "acquisition_time_utc": row[
            "sentinel1_acquisition_time"
        ],

        # AIS search window
        "ais_window_start_utc": window_start.isoformat().replace(
            "+00:00", "Z"
        ),
        "ais_window_end_utc": window_end.isoformat().replace(
            "+00:00", "Z"
        ),

        # Detection information
        "area_pixels": row["area_pixels"],
        "mean_vv_db": row["mean_vv_db"],
        "mean_vh_db": row["mean_vh_db"],
        "vv_minus_vh_db": row["vv_minus_vh_db"],
        "aspect_ratio": row["aspect_ratio"],
        "extent": row["extent"],

        # These will be filled after AIS data is obtained
        "vessel_mmsi": "",
        "vessel_name": "",
        "vessel_latitude": "",
        "vessel_longitude": "",
        "vessel_timestamp_utc": "",
        "distance_km": "",
        "time_difference_hours": "",
        "ais_gap_detected": "",
        "track_consistency": "",
        "evidence_score": ""
    })

# Save AIS correlation input
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

fieldnames = list(ais_rows[0].keys())

with open(OUTPUT, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(ais_rows)

print("AIS correlation input created successfully!")
print("==========================================")
print("Candidates:", len(ais_rows))
print("Output:", OUTPUT)

print("\nAIS search window:")
print("------------------")
print("Start:", window_start.isoformat().replace("+00:00", "Z"))
print("End  :", window_end.isoformat().replace("+00:00", "Z"))

print("\nCandidate locations:")
print("--------------------")

for row in ais_rows:
    print(
        f"{row['candidate_id']} | "
        f"Lat={row['spill_latitude']} | "
        f"Lon={row['spill_longitude']}"
    )

print("\nAIS correlation input generation completed!")
