"""
EPA Beach Directory Generator
------------------------------
Fetches the complete list of EPA-monitored Irish bathing water locations
from the EPA Ireland API and saves them as a beach name → beach ID
lookup dictionary in beaches.json.

Run this script to regenerate beaches.json if the EPA database is updated.

API source: https://data.epa.ie/bw/api/v1/
"""

import httpx
import json


def get_epa_beach_list():
    """
    Fetch all bathing water locations from the EPA Ireland Locations endpoint.

    Paginates through the full dataset (100 records per page) and builds
    a dictionary mapping beach names to their unique EPA beach IDs.

    Returns:
        dict: A dictionary in the format { "Beach Name": "beach_id" }
    """
    base_url = "https://data.epa.ie/bw/api/v1/Locations"
    all_beaches = []
    page = 1

    with httpx.Client() as client:
        while True:
            # Request 100 records per page to minimise the number of API calls
            params = {"page": page, "per_page": 100}
            try:
                response = client.get(base_url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                batch = data.get('list', [])

                # Stop paginating if the current page returned no records
                if not batch:
                    break

                all_beaches.extend(batch)

                # Stop if we have collected all available records
                if len(all_beaches) >= data.get('count', 0):
                    break

                page += 1

            except Exception as e:
                print(f"Error at page {page}: {e}")
                break

    # Build a quick-lookup dictionary: { "Beach Name": "beach_id" }
    return {b['beach_name']: b['beach_id'] for b in all_beaches}


# --- Main Execution ---

beach_directory = get_epa_beach_list()
print(f"Loaded {len(beach_directory)} beaches.")

# Save the directory to beaches.json for use with epa_beach_quality.py
with open('beaches.json', 'w', encoding='utf-8') as f:
    json.dump(beach_directory, f, indent=2, ensure_ascii=False)
print("Beach data saved to beaches.json")
