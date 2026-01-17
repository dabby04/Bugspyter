import os
import csv
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from datetime import datetime

BENCHMARK_DIR = "/junobench_env"

SUCCESS_CSV = "success.csv"
FAILED_CSV = "failed.csv"

# Initialize CSV files with headers
def init_csv(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["notebook_path", "timestamp", "error"])

init_csv(SUCCESS_CSV)
init_csv(FAILED_CSV)

def log_result(csv_path, notebook_path, error=""):
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            notebook_path,
            datetime.utcnow().isoformat(),
            error
        ])

# Loop through benchmark directories
for subfolder in os.listdir(BENCHMARK_DIR):
    subfolder_path = os.path.join(BENCHMARK_DIR, subfolder)
    if not os.path.isdir(subfolder_path):
        continue

    for file in os.listdir(subfolder_path):
        if not file.endswith("_extension.ipynb"):
            continue

        notebook_path = os.path.join(subfolder_path, file)
        print(f"Running: {notebook_path}")

        try:
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            executor = ExecutePreprocessor(
                timeout=600,          # adjust if notebooks are long-running
                kernel_name="python3",
                allow_errors=False    # raise exception on error
            )

            executor.preprocess(
                nb,
                {"metadata": {"path": subfolder_path}}
            )

            log_result(SUCCESS_CSV, notebook_path)
            print(f"✅ Success: {notebook_path}")

        except Exception as e:
            log_result(FAILED_CSV, notebook_path, str(e))
            print(f"❌ Failed: {notebook_path}")
            print(f"   Error: {e}")

print("Execution complete.")
