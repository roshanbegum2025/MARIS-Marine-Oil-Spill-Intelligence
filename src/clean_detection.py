import os
import numpy as np
from PIL import Image
from skimage.morphology import remove_small_objects, binary_opening, disk

INPUT = r"results\wakashio_detection\wakashio_vv_dark_mask.png"
OUTPUT_DIR = r"results\wakashio_detection"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load binary mask
image = np.array(Image.open(INPUT)) > 0

print("Original candidate pixels:", np.count_nonzero(image))

# Remove very small isolated regions
cleaned = remove_small_objects(
    image,
    min_size=500
)

# Remove small noisy connections
cleaned = binary_opening(
    cleaned,
    disk(2)
)

output = os.path.join(
    OUTPUT_DIR,
    "wakashio_vv_clean_mask.png"
)

Image.fromarray(
    (cleaned * 255).astype(np.uint8)
).save(output)

candidate_pixels = np.count_nonzero(cleaned)
total_pixels = cleaned.size

print("\nCleaned mask created!")
print("--------------------")
print("Candidate pixels:", candidate_pixels)
print("Candidate area  :", f"{candidate_pixels / total_pixels * 100:.2f}%")
print("Output          :", output)
