import xml.etree.ElementTree as ET

XML_PATH = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE\annotation\s1b-iw-grd-vv-20200810t013755-20200810t013820-022854-02b625-001.xml"

TARGET_LAT = -20.400
TARGET_LON = 57.720

tree = ET.parse(XML_PATH)
root = tree.getroot()

points = []

for point in root.iter():
    if point.tag.endswith("geolocationGridPoint"):
        values = {}

        for child in point:
            name = child.tag.split("}")[-1]
            values[name] = child.text

        if all(k in values for k in ["line", "pixel", "latitude", "longitude"]):
            points.append({
                "line": int(values["line"]),
                "pixel": int(values["pixel"]),
                "lat": float(values["latitude"]),
                "lon": float(values["longitude"])
            })

# Find points near the target
nearby = sorted(
    points,
    key=lambda p: (p["lat"] - TARGET_LAT)**2 + (p["lon"] - TARGET_LON)**2
)[:10]

print("\n10 nearest geolocation points:")
print("-" * 70)

for p in nearby:
    print(
        f"Line={p['line']:5d}  "
        f"Pixel={p['pixel']:5d}  "
        f"Lat={p['lat']:.6f}  "
        f"Lon={p['lon']:.6f}"
    )

print("\nTarget:")
print(f"Lat={TARGET_LAT}, Lon={TARGET_LON}")
