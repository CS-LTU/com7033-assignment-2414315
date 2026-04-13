"""
import_dataset.py

Imports the Kaggle Stroke Prediction Dataset CSV into MongoDB.

Usage:
    python import_dataset.py
    python import_dataset.py --file path/to/your/file.csv
    python import_dataset.py --clear   # drops existing records first

Place this file in the same folder as run.py (project root).
Make sure MongoDB is running before executing.
"""

import csv
import argparse
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# ── Configuration ────────────────────────────────────────────
MONGO_URI  = os.environ.get("MONGO_URI",  "mongodb://localhost:27017/")
DB_NAME    = os.environ.get("MONGO_DB_NAME", "stroke_prediction_db")
COLLECTION = "patients"
DEFAULT_CSV = "healthcare-dataset-stroke-data.csv"


def parse_row(row: dict) -> dict:
    """
    Convert a raw CSV row into a properly-typed MongoDB document.
    - Numeric fields are cast to float/int
    - 'N/A' BMI is stored as None (null in MongoDB)
    - The original 'id' column is kept as 'patient_csv_id'
      so it doesn't conflict with MongoDB's _id
    """
    return {
        "patient_csv_id":   int(row["id"]),
        "gender":           row["gender"].strip(),
        "age":              float(row["age"]),
        "hypertension":     int(row["hypertension"]),
        "heart_disease":    int(row["heart_disease"]),
        "ever_married":     row["ever_married"].strip(),
        "work_type":        row["work_type"].strip(),
        "Residence_type":   row["Residence_type"].strip(),
        "avg_glucose_level": round(float(row["avg_glucose_level"]), 2),
        "bmi":              None if row["bmi"].strip() in ("N/A", "", "n/a")
                            else round(float(row["bmi"]), 2),
        "smoking_status":   row["smoking_status"].strip(),
        "stroke":           int(row["stroke"]),
    }


def run_import(csv_path: str, clear_first: bool = False) -> None:
    """Connect to MongoDB, optionally clear the collection, then bulk insert."""

    # ── Connect ──────────────────────────────────────────────
    print(f"Connecting to MongoDB at {MONGO_URI} …")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
        client.admin.command("ping")
    except Exception as exc:
        print(f"[ERROR] Cannot connect to MongoDB: {exc}")
        print("Make sure mongod is running, then try again.")
        sys.exit(1)

    db  = client[DB_NAME]
    col = db[COLLECTION]

    # ── Optionally clear ─────────────────────────────────────
    if clear_first:
        deleted = col.delete_many({}).deleted_count
        print(f"Cleared {deleted} existing records.")

    # ── Read CSV ──────────────────────────────────────────────
    print(f"Reading CSV: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"[ERROR] File not found: {csv_path}")
        sys.exit(1)

    records   = []
    skipped   = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            try:
                records.append(parse_row(row))
            except (ValueError, KeyError) as exc:
                print(f"  [SKIP] Row {i}: {exc}")
                skipped += 1

    if not records:
        print("[ERROR] No valid records to import.")
        sys.exit(1)

    # ── Bulk insert ───────────────────────────────────────────
    print(f"Inserting {len(records)} records into '{DB_NAME}.{COLLECTION}' …")
    result = col.insert_many(records)
    print(f"\n✅  Done!")
    print(f"   Inserted : {len(result.inserted_ids)}")
    print(f"   Skipped  : {skipped}")
    print(f"   Total in DB now: {col.count_documents({})}")
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Stroke Prediction Dataset into MongoDB")
    parser.add_argument("--file",  default=DEFAULT_CSV, help="Path to CSV file")
    parser.add_argument("--clear", action="store_true",
                        help="Delete all existing patient records before importing")
    args = parser.parse_args()
    run_import(args.file, args.clear)
