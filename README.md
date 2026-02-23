# EPA Ireland Beach Water Quality Checker

A Python script that queries the [EPA Ireland Bathing Water API](https://data.epa.ie/bw/api/v1/) to retrieve the latest water quality measurement for a specified Irish beach.

## Features
- Searches both in-season and out-of-season EPA measurement endpoints
- Paginates backwards from the most recent data for efficient searching
- Retrieves key water quality metrics including E.coli and Intestinal Enterococci levels
- Saves the full measurement record to a local JSON file named after the beach

## Usage
Run the script and enter a beach ID when prompted:
```bash
python epa_beach_quality.py
```

Beach IDs for all monitored Irish beaches are listed in `beaches.json` included in this repository.

Example output:
```
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
```

## How It Works
1. Fetches the total record count from both the in-season and out-of-season endpoints
2. Calculates the last page and searches backwards to find the most recent entry
3. Filters results by the provided beach ID and tracks the latest measurement by date
4. Prints a formatted summary and saves the full record as a JSON file

## beaches.json
`beaches.json` contains a full reference list of all EPA-monitored Irish beaches and their corresponding beach IDs. Use this file to look up the correct ID before running the script.

## Data Source
All water quality data is sourced from the [EPA Ireland Open Data Portal](https://data.epa.ie).
