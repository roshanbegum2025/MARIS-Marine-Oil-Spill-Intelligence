import csv
from collections import defaultdict


CANDIDATE_FILE = r"results\wakashio_detection\maris_candidate_evidence.csv"
UNIQUE_FILE = r"results\wakashio_detection\maris_unique_vessel_candidate_evidence.csv"
IDENTITY_FILE = r"results\wakashio_detection\ais_vessel_identity.csv"

OUTPUT_FILE = r"results\wakashio_detection\maris_evidence_profile.csv"


# ---------------------------------------------------------
# Load candidate SAR evidence
# ---------------------------------------------------------

candidates = {}

with open(
    CANDIDATE_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:
        candidate_id = row["candidate_id"]
        candidates[candidate_id] = row


# ---------------------------------------------------------
# Load vessel identity
# ---------------------------------------------------------

identity_records = defaultdict(list)

with open(
    IDENTITY_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:
        identity_records[row["mmsi"]].append(row)


# ---------------------------------------------------------
# Select the most complete identity record
# ---------------------------------------------------------

def select_identity(records):

    if not records:
        return {
            "shipname": "Unknown",
            "flag": "Unknown",
            "imo": "Unknown",
            "callsign": "Unknown"
        }

    def completeness(row):
        fields = [
            row.get("shipname", ""),
            row.get("flag", ""),
            row.get("imo", ""),
            row.get("callsign", "")
        ]

        return sum(
            1 for value in fields
            if value and value.lower() != "none"
        )

    best = max(
        records,
        key=completeness
    )

    return {
        "shipname": best.get("shipname") or "Unknown",
        "flag": best.get("flag") or "Unknown",
        "imo": best.get("imo") or "Unknown",
        "callsign": best.get("callsign") or "Unknown"
    }


# ---------------------------------------------------------
# Load unique vessel-candidate evidence
# ---------------------------------------------------------

profiles = []

with open(
    UNIQUE_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        candidate_id = row["candidate_id"]
        mmsi = row["mmsi"]

        candidate = candidates.get(
            candidate_id,
            {}
        )

        identity = select_identity(
            identity_records.get(mmsi, [])
        )

        # -------------------------------------------------
        # Build evidence notes
        # -------------------------------------------------

        notes = []

        distance = float(
            row["minimum_distance_km"]
        )

        time_difference = float(
            row["minimum_time_difference_hours"]
        )

        observations = int(
            row["ais_observation_count"]
        )

        both_sides = (
            row["observed_both_sides"].lower()
            == "true"
        )

        if distance <= 1:
            notes.append(
                "AIS observation within 1 km of candidate"
            )
        elif distance <= 5:
            notes.append(
                "AIS observation within 5 km of candidate"
            )
        else:
            notes.append(
                "AIS observation beyond 5 km"
            )

        if time_difference <= 1:
            notes.append(
                "AIS temporally close to satellite acquisition"
            )
        elif time_difference <= 6:
            notes.append(
                "AIS within 6-hour correlation window"
            )
        else:
            notes.append(
                "AIS outside 6-hour correlation window"
            )

        if both_sides:
            notes.append(
                "AIS observations exist before and after acquisition"
            )

        if observations > 1:
            notes.append(
                "Multiple AIS observations in correlation window"
            )
        else:
            notes.append(
                "Single AIS observation in correlation window"
            )

        notes.append(
            "Association only; not proof of spill responsibility"
        )

        profiles.append({

            "candidate_id":
                candidate_id,

            "candidate_rank":
                candidate.get(
                    "candidate_rank",
                    row["candidate_rank"]
                ),

            "vessel_name":
                identity["shipname"],

            "mmsi":
                mmsi,

            "imo":
                identity["imo"],

            "flag":
                identity["flag"],

            "callsign":
                identity["callsign"],

            "candidate_lat":
                candidate.get(
                    "latitude",
                    row["candidate_lat"]
                ),

            "candidate_lon":
                candidate.get(
                    "longitude",
                    row["candidate_lon"]
                ),

            "sar_area_pixels":
                candidate.get(
                    "area_pixels",
                    ""
                ),

            "sar_mean_vv_db":
                candidate.get(
                    "mean_vv_db",
                    ""
                ),

            "sar_mean_vh_db":
                candidate.get(
                    "mean_vh_db",
                    ""
                ),

            "sar_vv_vh_difference_db":
                candidate.get(
                    "vv_vh_difference_db",
                    ""
                ),

            "sar_aspect_ratio":
                candidate.get(
                    "aspect_ratio",
                    ""
                ),

            "sar_extent_ratio":
                candidate.get(
                    "extent_ratio",
                    ""
                ),

            "ais_observation_count":
                observations,

            "minimum_distance_km":
                row["minimum_distance_km"],

            "closest_distance_ais_time":
                row["closest_distance_ais_time"],

            "minimum_time_difference_hours":
                row["minimum_time_difference_hours"],

            "closest_time_ais_time":
                row["closest_time_ais_time"],

            "closest_time_distance_km":
                row["closest_time_distance_km"],

            "observed_before_satellite":
                row["observed_before_satellite"],

            "observed_after_satellite":
                row["observed_after_satellite"],

            "observed_both_sides":
                row["observed_both_sides"],

            "evidence_notes":
                "; ".join(notes)
        })


# ---------------------------------------------------------
# Sort
# ---------------------------------------------------------

profiles.sort(
    key=lambda x: (
        int(x["candidate_rank"]),
        float(x["minimum_distance_km"])
    )
)


# ---------------------------------------------------------
# Save final evidence profile
# ---------------------------------------------------------

fieldnames = [
    "candidate_id",
    "candidate_rank",
    "vessel_name",
    "mmsi",
    "imo",
    "flag",
    "callsign",
    "candidate_lat",
    "candidate_lon",
    "sar_area_pixels",
    "sar_mean_vv_db",
    "sar_mean_vh_db",
    "sar_vv_vh_difference_db",
    "sar_aspect_ratio",
    "sar_extent_ratio",
    "ais_observation_count",
    "minimum_distance_km",
    "closest_distance_ais_time",
    "minimum_time_difference_hours",
    "closest_time_ais_time",
    "closest_time_distance_km",
    "observed_before_satellite",
    "observed_after_satellite",
    "observed_both_sides",
    "evidence_notes"
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
    writer.writerows(profiles)


# ---------------------------------------------------------
# Display summary
# ---------------------------------------------------------

print()
print("=" * 100)
print("MARIS EVIDENCE PROFILE")
print("=" * 100)

print(
    f"Total evidence profiles: {len(profiles)}"
)

print()

for row in profiles:

    print(
        f"{row['candidate_id']} | "
        f"{row['vessel_name']} | "
        f"MMSI={row['mmsi']} | "
        f"Distance={row['minimum_distance_km']} km | "
        f"Time={row['minimum_time_difference_hours']} h | "
        f"Obs={row['ais_observation_count']}"
    )

print()
print("=" * 100)
print("Output:")
print(OUTPUT_FILE)

print()
print("MARIS evidence profile created successfully!")