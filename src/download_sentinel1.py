import requests
import getpass
from pathlib import Path

# Your Copernicus product
PRODUCT_ID = "d9b01bbf-81b2-5ca4-8fc3-0d74c4d3dac0"

# Save inside your project folder
OUTPUT_FILE = Path("S1B_Wakashio_20200810.zip")

TOKEN_URL = (
    "https://identity.dataspace.copernicus.eu/"
    "auth/realms/CDSE/protocol/openid-connect/token"
)

DOWNLOAD_URL = (
    f"https://download.dataspace.copernicus.eu/"
    f"odata/v1/Products({PRODUCT_ID})/$value"
)

print("=== Sentinel-1 Download ===")
print()

username = input("Copernicus username/email: ")
password = getpass.getpass("Copernicus password: ")

print("\nGetting access token...")

token_response = requests.post(
    TOKEN_URL,
    data={
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    },
)

if token_response.status_code != 200:
    print("\nLogin/token failed.")
    print("Status:", token_response.status_code)
    print(token_response.text)
    raise SystemExit

access_token = token_response.json()["access_token"]

print("Authentication successful!")
print("Starting download...")
print("This file is about 1.73 GB.")
print()

headers = {
    "Authorization": f"Bearer {access_token}"
}

with requests.get(
    DOWNLOAD_URL,
    headers=headers,
    stream=True,
    timeout=120
) as response:

    if response.status_code != 200:
        print("Download failed.")
        print("Status:", response.status_code)
        print(response.text[:1000])
        raise SystemExit

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(OUTPUT_FILE, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)

                if total_size:
                    percent = downloaded * 100 / total_size
                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)

                    print(
                        f"\rDownloaded: {downloaded_mb:.1f} / "
                        f"{total_mb:.1f} MB ({percent:.1f}%)",
                        end=""
                    )

print("\n\nDownload completed!")
print("Saved as:", OUTPUT_FILE.resolve())