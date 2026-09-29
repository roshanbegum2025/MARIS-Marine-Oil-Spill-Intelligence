import csv
import math
from datetime import datetime, timezone

DISTANCE_FILE = r"results\wakashio_detection\ais_candidate_distances.csv"
OUTPUT_FILE = r"results\wakashio_detection\maris_evidence_matrix.csv"

SATELLITE_TIME = datetime(
    2020, 8, 10, 1, 37, 55,
    tzinfo=timezone.utc
)

MAX_DISTANCE_KM = 5.0
MAX_TIME_HOURS = 6.0


def parse_time(value):
    return datetime.strptime(
        value,
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=timezone.utc)


records = []

with open(
    DISTANCE_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        ais_time = parse_time(row["ais_date"])

        time_difference = (
            ais_time - SATELLITE_TIME
        ).total_seconds() / 3600

        distance = float(row["distance_km"])

        records.append({
            "candidate_id": row["candidate_id"],
            "candidate_rank": row["candidate_rank"],
            "candidate_lat": row["candidate_lat"],
            "candidate_lon": row["candidate_lon"],
            "mmsi": row["mmsi"],
            "ais_date": row["ais_date"],
            "ais_lat": row["ais_lat"],
            "ais_lon": row["ais_lon"],
            "distance_km": round(distance, 3),
            "time_difference_hours": round(
                time_difference, 2
            ),
            "absolute_time_difference_hours": round(
                abs(time_difference), 2
            ),
            "spatial_match": (
                distance <= MAX_DISTANCE_KM
            ),
            "temporal_match": (
                abs(time_difference) <= MAX_TIME_HOURS
            ),
            "joint_match": (
                distance <= MAX_DISTANCE_KM
                and abs(time_difference) <= MAX_TIME_HOURS
            )
        })


fieldnames = [
    "candidate_id",
    "candidate_rank",
    "candidate_lat",
    "candidate_lon",
    "mmsi",
    "ais_date",
    "ais_lat",
    "ais_lon",
    "distance_km",
    "time_difference_hours",
    "absolute_time_difference_hours",
    "spatial_match",
    "temporal_match",
    "joint_match"
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


print("\nMARIS Evidence Matrix")
print("=" * 70)
print(
    f"Distance threshold : {MAX_DISTANCE_KM} km"
)
print(
    f"Time threshold     : {MAX_TIME_HOURS} hours"
)
print()


for rank in range(1, 11):

    candidate_records = [
        r for r in records
        if int(r["candidate_rank"]) == rank
        and r["joint_match"]
    ]

    candidate_records.sort(
        key=lambda r: (
            r["absolute_time_difference_hours"],
            r["distance_km"]
        )
    )

    print(f"CAND-{rank:02d}")

    if not candidate_records:
        print("  No joint spatial-temporal matches")
        continue

    for r in candidate_records[:5]:
        print(
            f"  MMSI={r['mmsi']} | "
            f"Distance={r['distance_km']} km | "
            f"Time={r['time_difference_hours']} h | "
            f"AIS={r['ais_date']}"
        )


joint_count = sum(
    1 for r in records
    if r["joint_match"]
)

print("\n" + "=" * 70)
print(
    f"Total candidate-AIS pairs: {len(records)}"
)
print(
    f"Joint spatial-temporal matches: {joint_count}"
)

print("\nOutput:")
print(OUTPUT_FILE)

print("\nMARIS evidence matrix completed successfully!")
