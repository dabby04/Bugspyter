import os
import csv
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from datetime import datetime

FAILED_INPUT_CSV = "failed.csv"
FAILED_OUTPUT_CSV = "failed_retry.csv"
SUCCESS_CSV = "success_retry.csv"

# Initialize CSVs
def init_csv(file_path, headers):
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

init_csv(SUCCESS_CSV, ["notebook_path", "timestamp"])
init_csv(
    FAILED_OUTPUT_CSV,
    ["notebook_path", "timestamp", "error_type", "error_message"]
)

def log_success(notebook_path):
    with open(SUCCESS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            notebook_path,
            datetime.utcnow().isoformat()
        ])

def log_failure(notebook_path, error):
    with open(FAILED_OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            notebook_path,
            datetime.utcnow().isoformat(),
            type(error).__name__,
            str(error)
        ])

# Read failed notebooks
with open(FAILED_INPUT_CSV, newline="") as f:
    reader = csv.DictReader(f)
    failed_notebooks = [row["notebook_path"] for row in reader]

# Re-run failed notebooks
for notebook_path in failed_notebooks:
    if not os.path.exists(notebook_path):
        print(f"⚠️ Notebook not found: {notebook_path}")
        continue

    notebook_dir = os.path.dirname(notebook_path)
    print(f"Retrying: {notebook_path}")

    try:
        with open(notebook_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        executor = ExecutePreprocessor(
            timeout=600,
            kernel_name="python3",
            allow_errors=False
        )

        executor.preprocess(
            nb,
            {"metadata": {"path": notebook_dir}}
        )

        log_success(notebook_path)
        print(f"✅ Success: {notebook_path}")

    except Exception as e:
        log_failure(notebook_path, e)
        print(f"❌ Failed again: {notebook_path}")
        print(f"   {type(e).__name__}: {e}")

print("Retry execution complete.")
