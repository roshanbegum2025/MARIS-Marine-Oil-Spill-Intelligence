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

print("Candidate Region Characteristics")
print("================================")

for i, region in enumerate(regions[:20], start=1):

    min_row, min_col, max_row, max_col = region.bbox

    height = max_row - min_row
    width = max_col - min_col

    aspect_ratio = width / height if height > 0 else 0
    extent = region.extent

    cy, cx = region.centroid

    print(
        f"\nRegion {i}"
        f"\n  Area        : {region.area:.0f} pixels"
        f"\n  Centroid    : ({cy:.1f}, {cx:.1f})"
        f"\n  Width       : {width} pixels"
        f"\n  Height      : {height} pixels"
        f"\n  Aspect ratio: {aspect_ratio:.2f}"
        f"\n  Extent      : {extent:.3f}"
    )

print("\nAnalysis completed!")
