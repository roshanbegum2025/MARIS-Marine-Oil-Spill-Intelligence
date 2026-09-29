# Approximate interpolation for Pointe d'Esny

# Four surrounding geolocation points
p00 = (-20.313176, 57.755071, 14161, 12760)
p01 = (-20.284032, 57.631336, 14161, 14036)
p10 = (-20.493301, 57.708483, 16184, 12760)
p11 = (-20.464357, 57.585633, 16184, 14036)

target_lat = -20.400
target_lon = 57.720

# Use latitude to estimate line
lat_top = (p00[0] + p01[0]) / 2
lat_bottom = (p10[0] + p11[0]) / 2

line_fraction = (target_lat - lat_top) / (lat_bottom - lat_top)
line = 14161 + line_fraction * (16184 - 14161)

# Use longitude at the interpolated line
lon_left = p00[1] + line_fraction * (p10[1] - p00[1])
lon_right = p01[1] + line_fraction * (p11[1] - p01[1])

pixel_fraction = (target_lon - lon_left) / (lon_right - lon_left)
pixel = 12760 + pixel_fraction * (14036 - 12760)

print("\nEstimated Pointe d'Esny image position")
print("----------------------------------------")
print(f"Line  : {line:.1f}")
print(f"Pixel : {pixel:.1f}")

print("\nSurrounding area:")
print(f"Lines  : approximately {int(line)-1000} to {int(line)+1000}")
print(f"Pixels : approximately {int(pixel)-1000} to {int(pixel)+1000}")
