import os
import numpy as np
from PIL import Image
from skimage.measure import label, regionprops

INPUT = r"results\wakashio_detection\wakashio_vv_clean_mask.png"
OUTPUT = r"results\wakashio_detection\candidate_regions.png"

image = np.array(Image.open(INPUT)) > 0

labeled = label(image, connectivity=2)
regions = sorted(regionprops(labeled), key=lambda r: r.area, reverse=True)

# Keep only the 10 largest regions
output = np.zeros((*image.shape, 3), dtype=np.uint8)

for rank, region in enumerate(regions[:10], start=1):
    coords = region.coords

    # Different grayscale intensity for each region
    intensity = 25 + rank * 20
    output[coords[:, 0], coords[:, 1]] = intensity

Image.fromarray(output).save(OUTPUT)

print("Candidate-region map created!")
print("--------------------------------")
print("Regions displayed:", min(10, len(regions)))
print("Output:", OUTPUT)

for i, region in enumerate(regions[:10], start=1):
    print(f"Region {i}: {region.area:.0f} pixels")
