import numpy as np
from PIL import Image
from skimage.measure import label, regionprops

INPUT = r"results\wakashio_detection\wakashio_vv_clean_mask.png"

image = np.array(Image.open(INPUT)) > 0

labeled = label(image, connectivity=2)
regions = sorted(
    regionprops(labeled),
    key=lambda r: r.area,
    reverse=True
)

# Consider regions with at least 500 pixels
candidates = [r for r in regions if r.area >= 500]

max_area = max(r.area for r in candidates)

results = []

for region in candidates:

    min_row, min_col, max_row, max_col = region.bbox

    height = max_row - min_row
    width = max_col - min_col

    aspect_ratio = width / height if height > 0 else 0

    # Prefer moderately elongated shapes.
    # Score peaks around aspect ratio 2.
    shape_score = min(aspect_ratio, 1 / aspect_ratio) if aspect_ratio > 0 else 0

    # Normalize area
    area_score = region.area / max_area

    # Extent describes how much of the bounding box is occupied
    extent_score = region.extent

    # Simple heuristic score
    score = (
        0.50 * area_score +
        0.20 * shape_score +
        0.30 * extent_score
    )

    results.append((score, region))

results.sort(key=lambda x: x[0], reverse=True)

print("Oil-Spill Candidate Ranking")
print("============================")
print("Regions considered:", len(candidates))

for rank, (score, region) in enumerate(results[:15], start=1):

    cy, cx = region.centroid

    print(
        f"\nRank {rank}"
        f"\n  Score       : {score:.3f}"
        f"\n  Area        : {region.area:.0f} pixels"
        f"\n  Centroid    : ({cy:.1f}, {cx:.1f})"
        f"\n  Aspect ratio: {region.major_axis_length / region.minor_axis_length:.2f}"
        f"\n  Extent      : {region.extent:.3f}"
    )

print("\nCandidate ranking completed!")
