import os
import numpy as np
from PIL import Image
from skimage.measure import label, regionprops

INPUT = r"results\wakashio_detection\wakashio_vv_clean_mask.png"

image = np.array(Image.open(INPUT)) > 0

# Label connected regions
labeled = label(image, connectivity=2)

regions = regionprops(labeled)

# Sort largest first
regions = sorted(regions, key=lambda r: r.area, reverse=True)

print("Connected-component analysis")
print("----------------------------")
print("Total regions:", len(regions))

print("\nLargest candidate regions:")
print("---------------------------")

for i, region in enumerate(regions[:20], start=1):
    min_row, min_col, max_row, max_col = region.bbox

    print(
        f"Region {i}: "
        f"Area={region.area} pixels, "
        f"BBox=({min_row},{min_col}) to ({max_row},{max_col})"
    )
