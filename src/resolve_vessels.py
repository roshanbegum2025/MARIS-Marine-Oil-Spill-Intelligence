import os
import csv
import requests

TOKEN = os.environ.get("GFW_API_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "GFW_API_TOKEN is not set."
    )

INPUT_FILE = r"results\wakashio_detection\ais_presence.csv"
OUTPUT_FILE = r"results\wakashio_detection\ais_vessel_identity.csv"

URL = "https://gateway.api.globalfishingwatch.org/v3/vessels/search"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

DATASET = "public-global-vessel-identity:latest"


# Get unique MMSIs
mmsis = set()

with open(
    INPUT_FILE,
    newline="",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f)

    for row in reader:
        mmsi = str(row["mmsi"]).strip()

        if mmsi:
            mmsis.add(mmsi)


print("Unique MMSIs:", len(mmsis))
print()


results = []


for mmsi in sorted(mmsis):

    params = {
        "query": mmsi,
        "datasets[0]": DATASET
    }

    response = requests.get(
        URL,
        headers=HEADERS,
        params=params,
        timeout=60
    )

    print(
        f"MMSI {mmsi} -> HTTP {response.status_code}"
    )

    if response.status_code != 200:
        print(response.text[:500])
        continue

    data = response.json()
    entries = data.get("entries", [])

    print(
        f"  Matches returned: {len(entries)}"
    )


    for entry in entries:

        # GFW v3 stores AIS/self-reported identity here
        identity_records = entry.get(
            "selfReportedInfo",
            []
        )

        if not identity_records:
            print("  No self-reported identity information.")
            continue


        for identity in identity_records:

            results.append({
                "mmsi": mmsi,
                "vessel_id": identity.get("id"),
                "shipname": identity.get("shipname"),
                "flag": identity.get("flag"),
                "imo": identity.get("imo"),
                "callsign": identity.get("callsign"),
                "messages_counter": identity.get(
                    "messagesCounter"
                ),
                "positions_counter": identity.get(
                    "positionsCounter"
                ),
                "source": ", ".join(
                    identity.get("sourceCode", [])
                ),
                "match_fields": identity.get(
                    "matchFields"
                ),
                "transmissionDateFrom": identity.get(
                    "transmissionDateFrom"
                ),
                "transmissionDateTo": identity.get(
                    "transmissionDateTo"
                )
            })


fieldnames = [
    "mmsi",
    "vessel_id",
    "shipname",
    "flag",
    "imo",
    "callsign",
    "messages_counter",
    "positions_counter",
    "source",
    "match_fields",
    "transmissionDateFrom",
    "transmissionDateTo"
]


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


print()
print("=" * 70)
print("VESSEL IDENTITY RESOLUTION COMPLETE")
print("=" * 70)

for row in results:

    print(
        f"MMSI={row['mmsi']} | "
        f"Name={row['shipname']} | "
        f"Flag={row['flag']} | "
        f"IMO={row['imo']} | "
        f"Callsign={row['callsign']}"
    )

print()
print("Identity records:", len(results))
print("Output:", OUTPUT_FILE)
print()
print("Completed successfully!")
