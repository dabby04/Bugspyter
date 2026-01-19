import os
import subprocess

CHOSEN_MODEL = "gemini-2.0-flash"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Path to your Benchmark folder
BENCHMARK_DIR = os.path.join("experiments","notebooks")

# Path to output folder
EXPERIMENTS_DIR = os.path.join(PROJECT_ROOT,"experiments","Santana",CHOSEN_MODEL)

os.makedirs(EXPERIMENTS_DIR, exist_ok=True)


# Loop over reproduced notebooks
for file in os.listdir(BENCHMARK_DIR):
    if file.endswith(".ipynb"):
        notebook_path = os.path.join(BENCHMARK_DIR, file)

        # Construct the expected JSON path
        json_file_name = os.path.splitext(file)[0] + ".json"
        json_file_path = os.path.join(EXPERIMENTS_DIR, json_file_name)

        # Skip notebook if JSON exists
        if os.path.exists(json_file_path):
            print(f"Skipping (already processed): {notebook_path}")
            continue

        # Run your extension from notebook folder to fix relative paths
        print(f"Processing: {notebook_path}")
        subprocess.run(
            ["python", "-m", "bugspyter.script", notebook_path],
            cwd=BENCHMARK_DIR,  # run from notebook folder
            check=True
        )