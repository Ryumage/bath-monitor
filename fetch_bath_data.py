#!/usr/bin/env python3
"""
fetch_bath_data.py

Fetches current visitor counts from Munich baths API and stores them
in a SQLite database. One table per bath key is used. Occupancy
is stored with 1 decimal precision.

This script should be scheduled via cron.
"""

import requests
import sqlite3
from datetime import datetime
from config import BATHS, DB_FILE


def fetch_data():
    """
    Fetch visitor data for all configured baths and store in SQLite.

    Creates tables if they do not exist and adds an index on timestamp.
    Occupancy is calculated as (personCount / maxPersonCount * 100),
    rounded to 1 decimal.
    """
    timestamp = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        for key, bath in BATHS.items():
            table_name = key
            # Create table if missing
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    timestamp TEXT,
                    bath_id INTEGER,
                    bath_name TEXT,
                    personCount INTEGER,
                    maxPersonCount INTEGER,
                    occupancy REAL
                )
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{key}_timestamp ON {table_name}(timestamp)")

            try:
                response = requests.get(bath["apiUrl"], timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data or not isinstance(data, list):
                    print(f"⚠️ No data received for {bath['label']}")
                    continue

                entry = data[0]
                bath_id = entry["organizationUnitId"]
                person_count = entry["personCount"]
                max_person_count = entry["maxPersonCount"]
                occupancy = round((person_count / max_person_count * 100) if max_person_count else 0, 1)

                cursor.execute(
                    f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?, ?)",
                    (timestamp, bath_id, bath["label"], person_count, max_person_count, occupancy),
                )
                print(f"✅ {timestamp}: {bath['label']} → {occupancy:.1f}%")

            except Exception as err:
                print(f"❌ Error fetching {bath['label']}: {err}")

        conn.commit()


if __name__ == "__main__":
    fetch_data()
