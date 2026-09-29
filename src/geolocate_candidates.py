import os
import csv
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image
from skimage.measure import label, regionprops

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

SAFE_DIR = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE"

ANNOTATION = os.path.join(
    SAFE_DIR,
    "annotation",
    "s1b-iw-grd-vv-20200810t013755-20200810t013820-022854-02b625-001.xml"
)

MASK = r"results\wakashio_detection\wakashio_vv_clean_mask.png"

OUTPUT = r"results\wakashio_detection\candidate_locations.csv"

# Crop origin in the ORIGINAL Sentinel-1 image
START_LINE = 14299
START_PIXEL = 11851


# --------------------------------------------------
# READ SENTINEL-1 GEOLOCATION GRID
# --------------------------------------------------

tree = ET.parse(ANNOTATION)
root = tree.getroot()

points = []

for point in root.iter():
    if point.tag.endswith("geolocationGridPoint"):

        values = {}

        for child in point:
            name = child.tag.split("}")[-1]
            values[name] = child.text

        if all(k in values for k in ["line", "pixel", "latitude", "longitude"]):

            points.append({
                "line": float(values["line"]),
                "pixel": float(values["pixel"]),
                "lat": float(values["latitude"]),
                "lon": float(values["longitude"])
            })

print("Geolocation grid points:", len(points))


# --------------------------------------------------
# CONVERT TO ARRAYS
# --------------------------------------------------

lines = np.array([p["line"] for p in points])
pixels = np.array([p["pixel"] for p in points])
lats = np.array([p["lat"] for p in points])
lons = np.array([p["lon"] for p in points])


# --------------------------------------------------
# LOAD CANDIDATE MASK
# --------------------------------------------------

image = np.array(Image.open(MASK)) > 0

labeled = label(image, connectivity=2)

regions = sorted(
    regionprops(labeled),
    key=lambda r: r.area,
    reverse=True
)

regions = [r for r in regions if r.area >= 500][:10]


# --------------------------------------------------
# BILINEAR-STYLE LOCAL INTERPOLATION
# --------------------------------------------------

def interpolate_location(original_line, original_pixel):

    # Find closest grid points by distance in image coordinates
    distances = np.sqrt(
        (lines - original_line) ** 2 +
        (pixels - original_pixel) ** 2
    )

    nearest = np.argsort(distances)[:4]

    d = distances[nearest]

    # Exact grid point
    if d[0] == 0:
        return lats[nearest[0]], lons[nearest[0]]

    # Inverse-distance weighting
    weights = 1.0 / (d + 1e-9)
    weights = weights / weights.sum()

    latitude = np.sum(lats[nearest] * weights)
    longitude = np.sum(lons[nearest] * weights)

    return latitude, longitude


# --------------------------------------------------
# PROCESS CANDIDATES
# --------------------------------------------------

results = []

for rank, region in enumerate(regions, start=1):

    crop_row, crop_col = region.centroid

    original_line = START_LINE + crop_row
    original_pixel = START_PIXEL + crop_col

    latitude, longitude = interpolate_location(
        original_line,
        original_pixel
    )

    results.append({
        "rank": rank,
        "area_pixels": int(region.area),
        "crop_row": round(crop_row, 2),
        "crop_col": round(crop_col, 2),
        "original_line": round(original_line, 2),
        "original_pixel": round(original_pixel, 2),
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6)
    })


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

with open(OUTPUT, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("\nCandidate geographic locations")
print("================================")

for item in results:

    print(
        f"\nCandidate {item['rank']}"
        f"\n  Area      : {item['area_pixels']} pixels"
        f"\n  Crop      : ({item['crop_row']:.2f}, {item['crop_col']:.2f})"
        f"\n  Original  : line={item['original_line']:.2f}, "
        f"pixel={item['original_pixel']:.2f}"
        f"\n  Latitude  : {item['latitude']:.6f}"
        f"\n  Longitude : {item['longitude']:.6f}"
    )

print("\n--------------------------------")
print("Output:", OUTPUT)
print("Geolocation extraction completed!")
