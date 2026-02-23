"""
EPA Beach Water Quality Checker
--------------------------------
Queries the EPA Ireland Bathing Water API to retrieve the latest water quality
measurement for a specified beach ID. Searches both in-season and out-of-season
endpoints and saves the result to a local JSON file.

API source: https://data.epa.ie/bw/api/v1/
"""

import requests
import json


def get_latest_measurement(beach_id):
    """
    Retrieve the most recent water quality measurement for a given beach ID.

    Searches both the in-season and out-of-season EPA measurement endpoints,
    paginating backwards from the last page to find the most recent entry
    for the specified beach.

    Args:
        beach_id (str): The EPA beach identifier to search for.

    Returns:
        dict or None: The latest measurement record as a dictionary,
                      or None if no measurement is found.
    """
    urls = [
        "https://data.epa.ie/bw/api/v1/Measurements/in-season",
        "https://data.epa.ie/bw/api/v1/Measurements/out-season"
    ]

    latest_measurement = None
    latest_date = ""

    for url in urls:
        try:
            # Fetch the first page to determine total record count
            response = requests.get(f"{url}?page=1&per_page=100", timeout=10)

            if response.status_code != 200:
                print(f"Error: Got status code {response.status_code}")
                continue

            data = response.json()
            total_count = data.get('count', 0)
            per_page = 100

            # Calculate the last page number using ceiling division
            last_page = (total_count + per_page - 1) // per_page

            # Extract season type (in-season / out-season) from URL for logging
            season_type = url.split('/')[-1]
            print(f"Searching {season_type} (starting from page {last_page})...")

            # Search backwards from the last page — most recent data is likely near the end
            found = False
            for page in range(last_page, max(0, last_page - 10), -1):
                response = requests.get(
                    f"{url}?page={page}&per_page={per_page}", timeout=10
                )

                if response.status_code != 200:
                    continue

                data = response.json()
                batch = data.get('list', [])

                # Check each record in this page for a matching beach ID
                for m in batch:
                    if m.get('beach_id') == beach_id:
                        found = True
                        result_date = m.get('result_date')

                        # Keep track of the most recent measurement by date
                        if result_date:
                            if latest_date == "" or result_date > latest_date:
                                latest_date = result_date
                                latest_measurement = m

                if found:
                    print(f"  Found measurements on page {page}")
                    break  # Stop searching this endpoint once beach is found

            if not found:
                print(f"  No measurements found in {season_type}")

        except Exception as e:
            print(f"Error: {e}")

    return latest_measurement


# --- Main Script ---

# Prompt user to enter a beach ID (as listed in the EPA database)
beach_id = input("Enter beach ID: ").strip()

print(f"\nFetching latest measurement for beach ID: {beach_id}...\n")

# Retrieve the latest measurement from both API endpoints
latest = get_latest_measurement(beach_id)

if latest:
    beach_name = latest.get('beach_name', 'Unknown')

    # Display key water quality metrics in a readable format
    print(f"\nLatest measurement for {beach_name}:")
    print(f"  Beach ID:                    {beach_id}")
    print(f"  Date:                        {latest.get('result_date')}")
    print(f"  E.coli:                      {latest.get('e_coli_result')}")
    print(f"  Intestinal Enterococci:      {latest.get('intestinal_enterococci_result')}")
    print(f"  Water Quality Status:        {latest.get('sample_water_quality_status')}")
    print(f"  County:                      {latest.get('county_name')}")
    print(f"  Local Authority:             {latest.get('local_authority_name')}")

    # Save full measurement record to a JSON file named after the beach
    filename = f'{beach_name.replace(" ", "_")}_latest.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(latest, f, indent=2, ensure_ascii=False)
    print(f"\nFull record saved to: {filename}")

else:
    print(f"No measurements found for beach ID: {beach_id}")