import xml.etree.ElementTree as ET
import math

XML_PATH = r"sentinel1_wakashio\S1B_IW_GRDH_1SDV_20200810T013755_20200810T013820_022854_02B625_672D.SAFE\annotation\s1b-iw-grd-vv-20200810t013755-20200810t013820-022854-02b625-001.xml"

# Approximate Pointe d'Esny location
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

# Find closest geolocation-grid point to Pointe d'Esny
def distance(p):
    return math.sqrt(
        (p["lat"] - TARGET_LAT) ** 2 +
        (p["lon"] - TARGET_LON) ** 2
    )

closest = min(points, key=distance)

print("\nTarget location")
print("----------------")
print("Latitude :", TARGET_LAT)
print("Longitude:", TARGET_LON)

print("\nClosest geolocation point")
print("-------------------------")
print("Line     :", closest["line"])
print("Pixel    :", closest["pixel"])
print("Latitude :", closest["lat"])
print("Longitude:", closest["lon"])

print("\nDistance in degrees:")
print(distance(closest))
