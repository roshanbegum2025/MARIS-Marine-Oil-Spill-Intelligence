import csv
import numpy as np
from PIL import Image
from skimage.measure import label, regionprops

INPUT = r"results\wakashio_detection\wakashio_vv_clean_mask.png"
OUTPUT = r"results\wakashio_detection\candidate_ranking.csv"

image = np.array(Image.open(INPUT)) > 0

labeled = label(image, connectivity=2)
regions = sorted(
    regionprops(labeled),
    key=lambda r: r.area,
    reverse=True
)

candidates = [r for r in regions if r.area >= 500]

max_area = max(r.area for r in candidates)

results = []

for region in candidates:

    major = region.axis_major_length
    minor = region.axis_minor_length

    aspect_ratio = major / minor if minor > 0 else 0

    # Prefer elongated but not extremely thin regions.
    shape_score = min(aspect_ratio / 3.0, 1.0)

    area_score = region.area / max_area
    extent_score = region.extent

    score = (
        0.50 * area_score +
        0.20 * shape_score +
        0.30 * extent_score
    )

    cy, cx = region.centroid

    results.append({
        "area": int(region.area),
        "centroid_row": round(cy, 2),
        "centroid_col": round(cx, 2),
        "width": region.bbox[3] - region.bbox[1],
        "height": region.bbox[2] - region.bbox[0],
        "aspect_ratio": round(aspect_ratio, 3),
        "extent": round(region.extent, 3),
        "score": round(score, 4)
    })

results.sort(key=lambda x: x["score"], reverse=True)

with open(OUTPUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Candidate ranking completed!")
print("--------------------------------")
print("Candidates:", len(results))
print("CSV:", OUTPUT)

print("\nTop candidates:")

for rank, item in enumerate(results[:10], start=1):
    print(
        f"Rank {rank}: "
        f"Score={item['score']:.4f}, "
        f"Area={item['area']}, "
        f"Aspect={item['aspect_ratio']:.2f}, "
        f"Extent={item['extent']:.3f}, "
        f"Centroid=({item['centroid_row']:.1f}, "
        f"{item['centroid_col']:.1f})"
    )
