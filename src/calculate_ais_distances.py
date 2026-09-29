import csv
import math
import os

CANDIDATE_FILE = r"results\wakashio_detection\candidate_locations.csv"
AIS_FILE = r"results\wakashio_detection\ais_presence.csv"

OUTPUT_FILE = r"results\wakashio_detection\ais_candidate_distances.csv"


def haversine(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# -----------------------------
# Load candidates
# -----------------------------

candidates = []

with open(
    CANDIDATE_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    print("Candidate CSV columns:")
    print(reader.fieldnames)

    for row in reader:

        candidates.append({
            "candidate_id": f"CAND-{int(row['rank']):02d}",
            "rank": int(row["rank"]),
            "candidate_lat": float(row["latitude"]),
            "candidate_lon": float(row["longitude"])
        })


# -----------------------------
# Load AIS
# -----------------------------

ais_records = []

with open(
    AIS_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:

        if not row["lat"] or not row["lon"]:
            continue

        ais_records.append({
            "date": row["date"],
            "mmsi": row["mmsi"],
            "ais_lat": float(row["lat"]),
            "ais_lon": float(row["lon"])
        })


print("\nSatellite candidates:", len(candidates))
print("AIS observations:", len(ais_records))


# -----------------------------
# Calculate distances
# -----------------------------

results = []

for candidate in candidates:

    for ais in ais_records:

        distance = haversine(
            candidate["candidate_lat"],
            candidate["candidate_lon"],
            ais["ais_lat"],
            ais["ais_lon"]
        )

        results.append({
            "candidate_id": candidate["candidate_id"],
            "candidate_rank": candidate["rank"],
            "candidate_lat": candidate["candidate_lat"],
            "candidate_lon": candidate["candidate_lon"],
            "ais_date": ais["date"],
            "mmsi": ais["mmsi"],
            "ais_lat": ais["ais_lat"],
            "ais_lon": ais["ais_lon"],
            "distance_km": round(distance, 3)
        })


results.sort(
    key=lambda x: x["distance_km"]
)


# -----------------------------
# Save results
# -----------------------------

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    fieldnames = [
        "candidate_id",
        "candidate_rank",
        "candidate_lat",
        "candidate_lon",
        "ais_date",
        "mmsi",
        "ais_lat",
        "ais_lon",
        "distance_km"
    ]

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


# -----------------------------
# Closest AIS observation
# for each candidate
# -----------------------------

print("\nClosest AIS observation for each candidate:")
print("============================================")

for candidate in candidates:

    candidate_results = [
        r for r in results
        if r["candidate_id"] == candidate["candidate_id"]
    ]

    closest = min(
        candidate_results,
        key=lambda x: x["distance_km"]
    )

    print(
        f"{candidate['candidate_id']} | "
        f"MMSI={closest['mmsi']} | "
        f"Distance={closest['distance_km']:.3f} km | "
        f"AIS time={closest['ais_date']}"
    )


print("\n============================================")
print("AIS-CANDIDATE DISTANCE ANALYSIS COMPLETE")
print("============================================")

print("Total distance records:", len(results))
print("Output:", OUTPUT_FILE)
