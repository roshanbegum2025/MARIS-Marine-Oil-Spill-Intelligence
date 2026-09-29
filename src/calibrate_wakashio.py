import os
import xml.etree.ElementTree as ET

import numpy as np
import rasterio


SAFE_DIR = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE"
CROP_DIR = r"results\wakashio_crop"
OUT_DIR = r"results\wakashio_calibrated"

os.makedirs(OUT_DIR, exist_ok=True)


def get_child_text(element, name):
    for child in element:
        if child.tag.split("}")[-1] == name:
            return (child.text or "").strip()
    return ""


def load_calibration_lut(xml_path):
    root = ET.parse(xml_path).getroot()

    lines = []
    pixels = None
    values = []

    for elem in root.iter():

        if elem.tag.split("}")[-1] != "calibrationVector":
            continue

        line_text = get_child_text(elem, "line")
        pixel_text = get_child_text(elem, "pixel")
        sigma_text = get_child_text(elem, "sigmaNought")

        if line_text and pixel_text and sigma_text:

            lines.append(int(line_text))

            if pixels is None:
                pixels = np.array(
                    [float(x) for x in pixel_text.split()],
                    dtype=np.float64
                )

            values.append(
                np.array(
                    [float(x) for x in sigma_text.split()],
                    dtype=np.float64
                )
            )

    return (
        np.array(lines, dtype=np.float64),
        pixels,
        np.array(values, dtype=np.float64)
    )


def load_noise_lut(xml_path):
    root = ET.parse(xml_path).getroot()

    lines = []
    pixels = None
    values = []

    current_line = None
    current_pixels = None

    for elem in root.iter():

        tag = elem.tag.split("}")[-1]

        if tag == "noiseRangeVector":

            current_line = None
            current_pixels = None

            for child in elem:
                child_tag = child.tag.split("}")[-1]

                if child_tag == "line":
                    current_line = int(child.text)

                elif child_tag == "pixel":
                    current_pixels = np.array(
                        [float(x) for x in child.text.split()],
                        dtype=np.float64
                    )

                elif child_tag == "noiseRangeLut":
                    lut = np.array(
                        [float(x) for x in child.text.split()],
                        dtype=np.float64
                    )

                    if current_line is not None and current_pixels is not None:
                        lines.append(current_line)

                        if pixels is None:
                            pixels = current_pixels

                        values.append(lut)

    # Some Sentinel-1 noise files use noiseRangeVector
    # but the parser above may not match the exact XML structure.
    # Therefore, fall back to scanning direct line/pixel/LUT groups.

    if len(lines) == 0:

        elements = list(root.iter())

        for i, elem in enumerate(elements):

            if elem.tag.split("}")[-1] != "line":
                continue

            line_text = (elem.text or "").strip()

            if not line_text.isdigit():
                continue

            parent = None

            # Find the nearest parent containing the LUT
            for candidate in root.iter():
                children = list(candidate)

                if elem in children:
                    parent = candidate
                    break

            if parent is None:
                continue

            p = None
            n = None

            for child in parent:
                child_tag = child.tag.split("}")[-1]

                if child_tag == "pixel":
                    p = child.text

                elif child_tag == "noiseRangeLut":
                    n = child.text

            if p and n:

                lines.append(int(line_text))

                if pixels is None:
                    pixels = np.array(
                        [float(x) for x in p.split()],
                        dtype=np.float64
                    )

                values.append(
                    np.array(
                        [float(x) for x in n.split()],
                        dtype=np.float64
                    )
                )

    return (
        np.array(lines, dtype=np.float64),
        pixels,
        np.array(values, dtype=np.float64)
    )


def interpolate_lut(lines, pixels, values, target_lines, target_pixels):

    result = np.zeros(
        (len(target_lines), len(target_pixels)),
        dtype=np.float64
    )

    for r, line in enumerate(target_lines):

        if line <= lines[0]:

            i0 = i1 = 0
            weight = 0.0

        elif line >= lines[-1]:

            i0 = i1 = len(lines) - 1
            weight = 0.0

        else:

            i1 = np.searchsorted(lines, line)
            i0 = i1 - 1

            weight = (
                (line - lines[i0]) /
                (lines[i1] - lines[i0])
            )

        row0 = np.interp(
            target_pixels,
            pixels,
            values[i0]
        )

        row1 = np.interp(
            target_pixels,
            pixels,
            values[i1]
        )

        result[r, :] = (
            (1.0 - weight) * row0 +
            weight * row1
        )

    return result


def process_polarization(pol):

    pol_lower = pol.lower()

    suffix = "001" if pol == "VV" else "002"

    measurement = os.path.join(
        SAFE_DIR,
        "measurement",
        f"s1b-iw-grd-{pol_lower}-20200810t013755-20200810t013820-022854-02b625-{suffix}.tiff"
    )

    calibration_xml = os.path.join(
        SAFE_DIR,
        "annotation",
        "calibration",
        f"calibration-s1b-iw-grd-{pol_lower}-20200810t013755-20200810t013820-022854-02b625-{suffix}.xml"
    )

    noise_xml = os.path.join(
        SAFE_DIR,
        "annotation",
        "calibration",
        f"noise-s1b-iw-grd-{pol_lower}-20200810t013755-20200810t013820-022854-02b625-{suffix}.xml"
    )

    crop_path = os.path.join(
        CROP_DIR,
        f"wakashio_{pol_lower}_crop.tif"
    )

    print(f"\nProcessing {pol}")
    print("-" * 40)

    with rasterio.open(crop_path) as src:
        dn = src.read(1).astype(np.float64)

    height, width = dn.shape

    print("Crop size:", dn.shape)

    START_LINE = 14299
    START_PIXEL = 11851

    target_lines = START_LINE + np.arange(height)
    target_pixels = START_PIXEL + np.arange(width)

    cal_lines, cal_pixels, sigma_lut = load_calibration_lut(
        calibration_xml
    )

    noise_lines, noise_pixels, noise_lut = load_noise_lut(
        noise_xml
    )

    print("Calibration vectors:", len(cal_lines))
    print("Noise vectors:", len(noise_lines))

    if len(noise_lines) == 0:
        raise RuntimeError(
            "No noise vectors were found. Processing stopped safely."
        )

    sigma_cal = interpolate_lut(
        cal_lines,
        cal_pixels,
        sigma_lut,
        target_lines,
        target_pixels
    )

    noise = interpolate_lut(
        noise_lines,
        noise_pixels,
        noise_lut,
        target_lines,
        target_pixels
    )

    numerator = np.maximum(
        dn ** 2 - noise,
        1e-12
    )

    sigma0 = numerator / np.maximum(
        sigma_cal ** 2,
        1e-12
    )

    sigma0_db = 10.0 * np.log10(
        np.maximum(sigma0, 1e-12)
    )

    sigma0_db = np.clip(
        sigma0_db,
        -40,
        10
    )

    output_path = os.path.join(
        OUT_DIR,
        f"wakashio_{pol_lower}_sigma0_db.tif"
    )

    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": "float32"
    }

    with rasterio.open(
        output_path,
        "w",
        **profile
    ) as dst:

        dst.write(
            sigma0_db.astype(np.float32),
            1
        )

    print("Output:", output_path)
    print(
        "dB range:",
        f"{sigma0_db.min():.2f}",
        "to",
        f"{sigma0_db.max():.2f}"
    )


process_polarization("VV")
process_polarization("VH")

print("\nCalibration completed successfully!")
