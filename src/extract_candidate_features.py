import csv
import numpy as np
import rasterio
from PIL import Image
from skimage.measure import label, regionprops

MASK = r"results\wakashio_detection\wakashio_vv_clean_mask.png"

VV = r"results\wakashio_calibrated\wakashio_vv_sigma0_db.tif"
VH = r"results\wakashio_calibrated\wakashio_vh_sigma0_db.tif"

OUTPUT = r"results\wakashio_detection\candidate_features.csv"

mask = np.array(Image.open(MASK)) > 0

labeled = label(mask, connectivity=2)
regions = sorted(
    regionprops(labeled),
    key=lambda r: r.area,
    reverse=True
)

regions = [r for r in regions if r.area >= 500][:10]

with rasterio.open(VV) as src:
    vv = src.read(1).astype(np.float32)

with rasterio.open(VH) as src:
    vh = src.read(1).astype(np.float32)

results = []

for rank, region in enumerate(regions, start=1):

    coords = region.coords
    rows = coords[:, 0]
    cols = coords[:, 1]

    vv_values = vv[rows, cols]
    vh_values = vh[rows, cols]

    vv_values = vv_values[np.isfinite(vv_values)]
    vh_values = vh_values[np.isfinite(vh_values)]

    mean_vv = np.mean(vv_values)
    min_vv = np.min(vv_values)

    mean_vh = np.mean(vh_values)
    min_vh = np.min(vh_values)

    vv_vh_difference = mean_vv - mean_vh

    major = region.axis_major_length
    minor = region.axis_minor_length

    aspect_ratio = major / minor if minor > 0 else 0

    cy, cx = region.centroid

    results.append({
        "rank": rank,
        "area_pixels": int(region.area),
        "centroid_row": round(cy, 2),
        "centroid_col": round(cx, 2),
        "aspect_ratio": round(aspect_ratio, 3),
        "extent": round(region.extent, 3),
        "mean_vv_db": round(mean_vv, 3),
        "min_vv_db": round(min_vv, 3),
        "mean_vh_db": round(mean_vh, 3),
        "min_vh_db": round(min_vh, 3),
        "vv_minus_vh_db": round(vv_vh_difference, 3)
    })

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Candidate feature extraction completed!")
print("-----------------------------------------")
print("Candidates analyzed:", len(results))
print("Output:", OUTPUT)

for item in results:
    print(
        f"\nRank {item['rank']}"
        f"\n  Area       : {item['area_pixels']}"
        f"\n  Mean VV    : {item['mean_vv_db']:.2f} dB"
        f"\n  Mean VH    : {item['mean_vh_db']:.2f} dB"
        f"\n  VV - VH    : {item['vv_minus_vh_db']:.2f} dB"
        f"\n  Aspect     : {item['aspect_ratio']:.2f}"
        f"\n  Extent     : {item['extent']:.3f}"
    )
