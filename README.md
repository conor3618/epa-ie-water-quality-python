# EPA Ireland Beach Water Quality

A Python project that queries the [EPA Ireland Bathing Water API](https://data.epa.ie/api-list/bathing-water-open-data/) to retrieve the latest water quality measurements for Irish beaches. Includes a scheduled GitHub Action that automatically updates data for all 238 monitored beaches 3 times daily.

## Features
- Searches both in-season and out-of-season EPA measurement endpoints
- Paginates backwards from the most recent data for efficient searching
- Retrieves key water quality metrics including E.coli and Intestinal Enterococci levels
- Bulk fetches all 238 beaches concurrently and saves to a single JSON file
- GitHub Action runs automatically at 8am, 2pm and 8pm UTC daily
- `latest_beaches.json` is always up to date and publicly accessible via raw GitHub URL

## Scripts

| Script | Description |
|--------|-------------|
| `epa_beach_quality.py` | Query a single beach by ID interactively |
| `generate_beaches.py` | Regenerate `beaches.json` from the EPA Locations API |
| `update_all_beaches.py` | Fetch latest data for all beaches and save to `latest_beaches.json` |

## Usage

### Single beach lookup
Run the script and enter a beach ID when prompted:

    python epa_beach_quality.py

### Update all beaches

    python update_all_beaches.py

Beach IDs for all monitored Irish beaches are listed in `beaches.json`.

### Example output

    Enter beach ID: IESWBWC090_0000_0300

    Fetching latest measurement for beach ID: IESWBWC090_0000_0300...

    Searching in-season (starting from page 241)...
      Found measurements on page 239
    Searching out-season (starting from page 10)...
      No measurements found in out-season

    Latest measurement for Garrylucas, White Strand:
      Beach ID:                    IESWBWC090_0000_0300
      Date:                        2025-09-01
      E.coli:                      31
      Intestinal Enterococci:      3
      Water Quality Status:        Excellent
      County:                      Cork
      Local Authority:             Cork County Council

    Full record saved to: Garrylucas,_White_Strand_latest.json

## How It Works
1. Fetches the total record count from both the in-season and out-of-season endpoints
2. Calculates the last page and searches backwards to find the most recent entry
3. Filters results by the provided beach ID and tracks the latest measurement by date
4. Prints a formatted summary and saves the full record as a JSON file

## GitHub Action
A scheduled workflow runs `update_all_beaches.py` at 8am, 2pm and 8pm UTC daily and commits the updated `latest_beaches.json` to the repository automatically. You can also trigger it manually from the Actions tab.

The latest data for all beaches is always available at:

    https://raw.githubusercontent.com/conor3618/epa-ie-water-quality-python/main/latest_beaches.json

## beaches.json
`beaches.json` contains a full reference list of all EPA-monitored Irish beaches and their corresponding beach IDs. Use this file to look up the correct ID before running the script. To regenerate `beaches.json` with the latest EPA beach list, run `generate_beaches.py`.

## Data Source
All water quality data is sourced from the [EPA Ireland Open Data Portal](https://data.epa.ie).
Data is provided under the [Creative Commons Attribution 4.0 licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
EPA Ireland neither endorses this project nor guarantees data accuracy.
