import rasterio
import os

TIFF = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE\measurement\s1b-iw-grd-vv-20200810t013755-20200810t013820-022854-02b625-001.tiff"

OUT_DIR = r"results\wakashio_crop"
os.makedirs(OUT_DIR, exist_ok=True)

# Approximate Pointe d'Esny position
CENTER_LINE = 15299
CENTER_PIXEL = 12852

CROP_SIZE = 2000

row_start = CENTER_LINE - CROP_SIZE // 2
col_start = CENTER_PIXEL - CROP_SIZE // 2

with rasterio.open(TIFF) as src:

    window = rasterio.windows.Window(
        col_start,
        row_start,
        CROP_SIZE,
        CROP_SIZE
    )

    data = src.read(1, window=window)

    profile = src.profile.copy()
    profile.update(
        width=CROP_SIZE,
        height=CROP_SIZE
    )

    output = os.path.join(OUT_DIR, "wakashio_vv_crop.tif")

    with rasterio.open(output, "w", **profile) as dst:
        dst.write(data, 1)

print("VV crop created successfully!")
print("Output:", output)
print("Crop size:", data.shape)
print("Center line:", CENTER_LINE)
print("Center pixel:", CENTER_PIXEL)
