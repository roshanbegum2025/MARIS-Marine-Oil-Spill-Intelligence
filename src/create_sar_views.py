import rasterio
import numpy as np
from PIL import Image
import os

INPUTS = {
    "VV": r"results\wakashio_crop\wakashio_vv_crop.tif",
    "VH": r"results\wakashio_crop\wakashio_vh_crop.tif"
}

OUT_DIR = r"results\wakashio_crop"
os.makedirs(OUT_DIR, exist_ok=True)

for name, path in INPUTS.items():

    with rasterio.open(path) as src:
        data = src.read(1).astype(np.float32)

    # Remove invalid/non-positive values
    valid = data[data > 0]

    low = np.percentile(valid, 2)
    high = np.percentile(valid, 98)

    # Contrast stretch
    stretched = (data - low) / (high - low)
    stretched = np.clip(stretched, 0, 1)

    image = (stretched * 255).astype(np.uint8)

    output = os.path.join(OUT_DIR, f"wakashio_{name.lower()}_view.png")
    Image.fromarray(image).save(output)

    print(f"{name} visualization created:")
    print(f"  {output}")
    print(f"  Min percentile: {low:.2f}")
    print(f"  Max percentile: {high:.2f}")

print("\nSAR visualization completed successfully!")
