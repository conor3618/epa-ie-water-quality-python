"""
EPA All Beaches Updater
-----------------------
Downloads all EPA measurement pages concurrently into memory, then searches
locally for each beach. Fast - fetches 10 pages at a time.

Run:  python update_all_beaches.py
Output: latest_beaches.json
"""

import json
import time
import requests
import os
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE  = os.path.join(BASE_DIR, "beaches.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "latest_beaches.json")

URLS = [
    "https://data.epa.ie/bw/api/v1/Measurements/in-season",
    "https://data.epa.ie/bw/api/v1/Measurements/out-season"
]


def fetch_page(url, page):
    try:
        response = requests.get(
            f"{url}?page={page}&per_page=100", timeout=30
        )
        if response.status_code == 200:
            return response.json().get('list', [])
    except Exception as e:
        print(f"\n  Error on page {page}: {e}")
    return []


def fetch_all_measurements():
    """Download every page from both endpoints concurrently into one dict keyed by beach_id."""
    all_measurements = {}

    for url in URLS:
        season = url.split('/')[-1]
        print(f"Downloading {season} data...")

        try:
            response = requests.get(f"{url}?page=1&per_page=100", timeout=30)
            data = response.json()
            total_count = data.get('count', 0)
            last_page = (total_count + 99) // 100
            print(f"  {last_page} pages, {total_count} records")
        except Exception as e:
            print(f"  Failed to get page count: {e}")
            continue

        completed = 0
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(fetch_page, url, page): page
                for page in range(1, last_page + 1)
            }
            for future in as_completed(futures):
                batch = future.result()
                completed += 1
                print(f"  Fetched {completed}/{last_page} pages...", end="\r")
                for m in batch:
                    bid = m.get('beach_id')
                    result_date = m.get('result_date', '')
                    if bid:
                        existing = all_measurements.get(bid)
                        if not existing or result_date > existing.get('result_date', ''):
                            all_measurements[bid] = m

        print(f"\n  Done. {len(all_measurements)} unique beaches so far.\n")

    return all_measurements


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        beaches = json.load(f)

    total = len(beaches)

    print("Downloading all measurements first...\n")
    all_measurements = fetch_all_measurements()

    print(f"Building results for {total} beaches...\n")

    results = []
    failed  = []

    for name, beach_id in beaches.items():
        m = all_measurements.get(beach_id)
        if m:
            results.append({
                "beach_id":               beach_id,
                "name":                   name,
                "status":                 m.get("sample_water_quality_status"),
                "result_date":            m.get("result_date"),
                "e_coli":                 m.get("e_coli_result"),
                "intestinal_enterococci": m.get("intestinal_enterococci_result"),
                "county":                 m.get("county_name"),
                "local_authority":        m.get("local_authority_name"),
                "updated_at":             datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
            print(f"  ✓ {name}: {m.get('sample_water_quality_status')} ({m.get('result_date')})")
        else:
            failed.append(name)
            print(f"  ✗ {name}: no data")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"Done! {len(results)}/{total} beaches updated.")
    print(f"Saved to: {OUTPUT_FILE}")

    if failed:
        print(f"\nNo data found for {len(failed)} beaches:")
        for name in failed:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
