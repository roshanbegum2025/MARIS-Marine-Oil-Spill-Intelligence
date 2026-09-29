import os
import csv

FEATURES = r"results\wakashio_detection\candidate_features.csv"
LOCATIONS = r"results\wakashio_detection\candidate_locations.csv"

OUTPUT = r"results\wakashio_detection\maris_candidate_evidence.csv"

# Sentinel-1 acquisition time
ACQUISITION_TIME = "2020-08-10T01:37:55Z"

# Read candidate feature data
with open(FEATURES, newline="") as f:
    feature_rows = list(csv.DictReader(f))

# Read candidate location data
with open(LOCATIONS, newline="") as f:
    location_rows = list(csv.DictReader(f))

# Match candidates using rank
locations_by_rank = {
    int(row["rank"]): row
    for row in location_rows
}

master_rows = []

for feature in feature_rows:

    rank = int(feature["rank"])
    location = locations_by_rank[rank]

    master_rows.append({
        "candidate_id": f"CAND-{rank:02d}",
        "area_pixels": feature["area_pixels"],
        "centroid_row": feature["centroid_row"],
        "centroid_col": feature["centroid_col"],
        "original_line": location["original_line"],
        "original_pixel": location["original_pixel"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "mean_vv_db": feature["mean_vv_db"],
        "min_vv_db": feature["min_vv_db"],
        "mean_vh_db": feature["mean_vh_db"],
        "min_vh_db": feature["min_vh_db"],
        "vv_minus_vh_db": feature["vv_minus_vh_db"],
        "aspect_ratio": feature["aspect_ratio"],
        "extent": feature["extent"],
        "sentinel1_acquisition_time": ACQUISITION_TIME
    })

# Save master CSV
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

with open(OUTPUT, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=master_rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(master_rows)

print("MARIS master evidence CSV created!")
print("=================================")
print("Candidates:", len(master_rows))
print("Output:", OUTPUT)

print("\nMaster candidate summary:")
print("-------------------------")

for row in master_rows:

    print(
        f"{row['candidate_id']} | "
        f"Lat={row['latitude']} | "
        f"Lon={row['longitude']} | "
        f"Area={row['area_pixels']} | "
        f"VV={row['mean_vv_db']} dB | "
        f"VH={row['mean_vh_db']} dB"
    )

print("\nMaster CSV generation completed successfully!")
