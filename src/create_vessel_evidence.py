import csv
from collections import defaultdict

EVIDENCE_FILE = r"results\wakashio_detection\maris_evidence_matrix.csv"
IDENTITY_FILE = r"results\wakashio_detection\ais_vessel_identity.csv"
OUTPUT_FILE = r"results\wakashio_detection\maris_vessel_evidence.csv"


# ---------------------------------------------------------
# Load vessel identities
# ---------------------------------------------------------

identity = {}

with open(
    IDENTITY_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        mmsi = row["mmsi"]

        # Prefer a record containing an actual vessel name
        if (
            mmsi not in identity
            or (
                not identity[mmsi].get("shipname")
                and row.get("shipname")
            )
        ):
            identity[mmsi] = row


# ---------------------------------------------------------
# Load joint evidence
# ---------------------------------------------------------

groups = defaultdict(list)

with open(
    EVIDENCE_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        if row["joint_match"].lower() == "true":
            groups[row["mmsi"]].append(row)


# ---------------------------------------------------------
# Create vessel summary
# ---------------------------------------------------------

summary = []

for mmsi, records in groups.items():

    distances = [
        float(r["distance_km"])
        for r in records
    ]

    time_diffs = [
        abs(float(r["time_difference_hours"]))
        for r in records
    ]

    candidates = sorted(
        set(r["candidate_id"] for r in records)
    )

    info = identity.get(mmsi, {})

    summary.append({

        "mmsi": mmsi,

        "shipname": info.get(
            "shipname",
            ""
        ),

        "flag": info.get(
            "flag",
            ""
        ),

        "imo": info.get(
            "imo",
            ""
        ),

        "callsign": info.get(
            "callsign",
            ""
        ),

        "joint_match_count": len(records),

        "candidate_count": len(candidates),

        "candidate_ids": ", ".join(
            candidates
        ),

        "minimum_distance_km": round(
            min(distances),
            3
        ),

        "average_distance_km": round(
            sum(distances) / len(distances),
            3
        ),

        "minimum_time_difference_hours": round(
            min(time_diffs),
            2
        ),

        "identity_available": bool(
            info.get("shipname")
        )
    })


# Sort by number of candidate regions covered
summary.sort(
    key=lambda x: (
        -x["candidate_count"],
        x["minimum_distance_km"]
    )
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

fieldnames = [
    "mmsi",
    "shipname",
    "flag",
    "imo",
    "callsign",
    "joint_match_count",
    "candidate_count",
    "candidate_ids",
    "minimum_distance_km",
    "average_distance_km",
    "minimum_time_difference_hours",
    "identity_available"
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


# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

print()
print("=" * 80)
print("MARIS VESSEL-LEVEL EVIDENCE SUMMARY")
print("=" * 80)

for row in summary:

    name = row["shipname"] or "IDENTITY NOT AVAILABLE"

    print(
        f"{name} | "
        f"MMSI={row['mmsi']} | "
        f"Candidates={row['candidate_count']} | "
        f"Matches={row['joint_match_count']} | "
        f"Min distance={row['minimum_distance_km']} km | "
        f"Min time={row['minimum_time_difference_hours']} h"
    )

print()
print("Vessels with joint evidence:", len(summary))
print("Output:", OUTPUT_FILE)
print()
print("MARIS vessel evidence summary completed successfully!")
