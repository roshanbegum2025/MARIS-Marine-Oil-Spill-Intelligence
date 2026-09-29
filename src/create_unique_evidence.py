import csv
from collections import defaultdict

INPUT_FILE = r"results\wakashio_detection\maris_evidence_matrix.csv"
OUTPUT_FILE = r"results\wakashio_detection\maris_unique_vessel_candidate_evidence.csv"

groups = defaultdict(list)

# Load joint matches
with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        if row["joint_match"].lower() == "true":
            key = (
                row["mmsi"],
                row["candidate_id"]
            )
            groups[key].append(row)

summary = []

# Aggregate each vessel-candidate pair
for (mmsi, candidate_id), records in groups.items():

    distances = [
        float(r["distance_km"])
        for r in records
    ]

    time_differences = [
        float(r["time_difference_hours"])
        for r in records
    ]

    closest_spatial = min(
        records,
        key=lambda r: float(r["distance_km"])
    )

    closest_temporal = min(
        records,
        key=lambda r: abs(
            float(r["time_difference_hours"])
        )
    )

    before = any(
        float(r["time_difference_hours"]) < 0
        for r in records
    )

    after = any(
        float(r["time_difference_hours"]) > 0
        for r in records
    )

    summary.append({
        "candidate_id": candidate_id,
        "candidate_rank": closest_spatial["candidate_rank"],
        "mmsi": mmsi,
        "candidate_lat": closest_spatial["candidate_lat"],
        "candidate_lon": closest_spatial["candidate_lon"],
        "ais_observation_count": len(records),
        "minimum_distance_km": round(min(distances), 3),
        "closest_distance_ais_time": closest_spatial["ais_date"],
        "minimum_time_difference_hours": round(
            min(abs(x) for x in time_differences), 2
        ),
        "closest_time_ais_time": closest_temporal["ais_date"],
        "closest_time_distance_km": round(
            float(closest_temporal["distance_km"]), 3
        ),
        "observed_before_satellite": before,
        "observed_after_satellite": after,
        "observed_both_sides": before and after
    })

summary.sort(
    key=lambda x: (
        int(x["candidate_rank"]),
        x["minimum_distance_km"]
    )
)

fieldnames = [
    "candidate_id",
    "candidate_rank",
    "mmsi",
    "candidate_lat",
    "candidate_lon",
    "ais_observation_count",
    "minimum_distance_km",
    "closest_distance_ais_time",
    "minimum_time_difference_hours",
    "closest_time_ais_time",
    "closest_time_distance_km",
    "observed_before_satellite",
    "observed_after_satellite",
    "observed_both_sides"
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
    writer.writerows(summary)

print()
print("=" * 90)
print("UNIQUE VESSEL-CANDIDATE EVIDENCE")
print("=" * 90)

for row in summary:
    print(
        f"{row['candidate_id']} | "
        f"MMSI={row['mmsi']} | "
        f"Obs={row['ais_observation_count']} | "
        f"MinDist={row['minimum_distance_km']} km | "
        f"MinTime={row['minimum_time_difference_hours']} h | "
        f"BothSides={row['observed_both_sides']}"
    )

print()
print("=" * 90)
print(f"Unique vessel-candidate pairs: {len(summary)}")
print("Original joint matches: 314")
print()
print("Output:")
print(OUTPUT_FILE)
print()
print("Unique evidence analysis completed successfully!")
