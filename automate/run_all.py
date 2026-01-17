import os
import subprocess

# Path to your Benchmark folder inside Docker
BENCHMARK_DIR = "/junobench_env"

# Path to experiments folder inside Docker (must match your Docker mount)
EXPERIMENTS_DIR = "/opt/my_extension/experiments/CHOSEN_MODEL"

for subfolder in os.listdir(BENCHMARK_DIR):
    subfolder_path = os.path.join(BENCHMARK_DIR, subfolder)
    if not os.path.isdir(subfolder_path):
        continue

    # Loop over reproduced notebooks
    for file in os.listdir(subfolder_path):
        if file.endswith("_reproduced.ipynb") and "_fixed" not in file:
            notebook_path = os.path.join(subfolder_path, file)

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
                cwd=subfolder_path,  # run from notebook folder
                check=True
            )
