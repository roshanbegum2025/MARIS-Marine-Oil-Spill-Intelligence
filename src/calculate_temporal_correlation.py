import csv
import os
from datetime import datetime, timezone

INPUT_FILE = r"results\wakashio_detection\ais_candidate_distances.csv"
OUTPUT_FILE = r"results\wakashio_detection\ais_temporal_correlation.csv"

SATELLITE_TIME = datetime(
    2020, 8, 10, 1, 37, 55,
    tzinfo=timezone.utc
)

records = []

with open(
    INPUT_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        ais_time = datetime.strptime(
            row["ais_date"],
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=timezone.utc)

        difference_hours = (
            ais_time - SATELLITE_TIME
        ).total_seconds() / 3600

        records.append({
            **row,
            "time_difference_hours":
                round(difference_hours, 2),
            "absolute_time_difference_hours":
                round(abs(difference_hours), 2)
        })


# Sort by candidate, then temporal difference
records.sort(
    key=lambda x: (
        x["candidate_rank"],
        x["absolute_time_difference_hours"]
    )
)


fieldnames = [
    "candidate_id",
    "candidate_rank",
    "candidate_lat",
    "candidate_lon",
    "ais_date",
    "mmsi",
    "ais_lat",
    "ais_lon",
    "distance_km",
    "time_difference_hours",
    "absolute_time_difference_hours"
]

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(records)


# Show closest spatial + temporal relationships
print("Temporal correlation calculated.")
print("================================")

for candidate_rank in range(1, 11):

    candidate_records = [
        r for r in records
        if int(r["candidate_rank"]) == candidate_rank
    ]

    # First choose records with the smallest time difference
    closest_time = min(
        candidate_records,
        key=lambda x: x["absolute_time_difference_hours"]
    )

    print(
        f"CAND-{candidate_rank:02d} | "
        f"MMSI={closest_time['mmsi']} | "
        f"Distance={closest_time['distance_km']} km | "
        f"AIS={closest_time['ais_date']} | "
        f"Time difference="
        f"{closest_time['time_difference_hours']} h"
    )


print("\nOutput:")
print(OUTPUT_FILE)

print("\nTemporal correlation completed successfully!")
