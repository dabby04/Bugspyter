import os
import json
import csv

# Folder containing the JSON files
INPUT_FOLDER = "experiments/gemini-2.5-flash" 
OUTPUT_CSV = "bug_summary_without_analysis.csv"

# CSV column names
FIELDNAMES = [
    "filename",
    "file_id",          # filename without extension
    "buggy_or_not",
    "major_bug",
    "root_cause"
]

rows = []

for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".json"):
        file_path = os.path.join(INPUT_FOLDER, filename)

        # Extract filename without extension
        file_id = os.path.splitext(filename)[0]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            row = {
                "filename": filename,
                "file_id": file_id,
                "buggy_or_not": data.get("buggy_or_not", ""),
                "major_bug": data.get("major_bug", ""),
                "root_cause": data.get("root_cause", "")
            }

            rows.append(row)

        except (json.JSONDecodeError, IOError) as e:
            print(f"Skipping {filename}: {e}")

# Write to CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)

print(f"Extracted {len(rows)} records into {OUTPUT_CSV}")
