import os
import numpy as np
import rasterio
from PIL import Image

INPUT = r"results\wakashio_calibrated\wakashio_vv_sigma0_db.tif"
OUTPUT_DIR = r"results\wakashio_detection"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with rasterio.open(INPUT) as src:
    data = src.read(1).astype(np.float32)

# Basic candidate threshold
# Pixels below this backscatter level are marked as potential dark regions
THRESHOLD = -20.0

mask = np.where(data < THRESHOLD, 255, 0).astype(np.uint8)

output = os.path.join(
    OUTPUT_DIR,
    "wakashio_vv_dark_mask.png"
)

Image.fromarray(mask).save(output)

total_pixels = mask.size
candidate_pixels = np.count_nonzero(mask)

print("Oil-spill candidate mask created!")
print("--------------------------------")
print("Threshold       :", THRESHOLD, "dB")
print("Total pixels    :", total_pixels)
print("Candidate pixels:", candidate_pixels)
print("Candidate area  :", f"{candidate_pixels / total_pixels * 100:.2f}%")
print("Output          :", output)
