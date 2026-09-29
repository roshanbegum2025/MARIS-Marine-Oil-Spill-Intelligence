import os
import numpy as np
import rasterio
from PIL import Image

INPUTS = {
    "VV": r"results\wakashio_calibrated\wakashio_vv_sigma0_db.tif",
    "VH": r"results\wakashio_calibrated\wakashio_vh_sigma0_db.tif"
}

OUT_DIR = r"results\wakashio_calibrated"

for name, path in INPUTS.items():

    with rasterio.open(path) as src:
        data = src.read(1).astype(np.float32)

    valid = data[np.isfinite(data)]

    low = np.percentile(valid, 2)
    high = np.percentile(valid, 98)

    stretched = (data - low) / (high - low)
    stretched = np.clip(stretched, 0, 1)

    image = (stretched * 255).astype(np.uint8)

    output = os.path.join(
        OUT_DIR,
        f"wakashio_{name.lower()}_sigma0_db_view.png"
    )

    Image.fromarray(image).save(output)

    print(f"{name} calibrated visualization created:")
    print(f"  {output}")
    print(f"  2nd percentile: {low:.2f} dB")
    print(f"  98th percentile: {high:.2f} dB")

print("\nCalibrated SAR visualization completed successfully!")
