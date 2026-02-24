"""
EPA Beach Directory Generator
------------------------------
Fetches the complete list of EPA-monitored Irish bathing water locations
from the EPA Ireland API and saves them as a beach name -> beach ID
lookup dictionary in beaches.json.

Handles duplicate beach names by appending the county name.

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
    Duplicate names are disambiguated by appending the county name.

    Returns:
        dict: A dictionary in the format { "Beach Name": "beach_id" }
    """
    base_url = "https://data.epa.ie/bw/api/v1/Locations"
    all_beaches = []
    page = 1

    with httpx.Client() as client:
        while True:
            params = {"page": page, "per_page": 100}
            try:
                response = client.get(base_url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                batch = data.get('list', [])

                if not batch:
                    break

                all_beaches.extend(batch)

                if len(all_beaches) >= data.get('count', 0):
                    break

                page += 1

            except Exception as e:
                print(f"Error at page {page}: {e}")
                break

    # Find all duplicate names first
    seen_names = {}
    for b in all_beaches:
        name = b['beach_name']
        seen_names[name] = seen_names.get(name, 0) + 1

    duplicates = {name for name, count in seen_names.items() if count > 1}

    if duplicates:
        print(f"Found {len(duplicates)} duplicate name(s): {', '.join(sorted(duplicates))}")

    # Build dictionary — append county for any duplicate names
    beach_directory = {}
    for b in all_beaches:
        name = b['beach_name']
        if name in duplicates:
            county = b.get('county_name', 'Unknown')
            name = f"{name} ({county})"
        beach_directory[name] = b['beach_id']

    return beach_directory


# --- Main Execution ---
if __name__ == "__main__":
    beach_directory = get_epa_beach_list()
    print(f"Loaded {len(beach_directory)} beaches.")

    with open('beaches.json', 'w', encoding='utf-8') as f:
        json.dump(beach_directory, f, indent=2, ensure_ascii=False)
    print("Beach data saved to beaches.json")
