import os
import shutil

# Path to your Benchmark folder inside Docker
BENCHMARK_DIR = "/junobench_env"

for subfolder in os.listdir(BENCHMARK_DIR):
    subfolder_path = os.path.join(BENCHMARK_DIR, subfolder)
    if not os.path.isdir(subfolder_path):
        continue

    for file in os.listdir(subfolder_path):
        if file.endswith("_reproduced.ipynb") and "_fixed" not in file:
            src_path = os.path.join(subfolder_path, file)

            # Replace suffix with _extension
            new_name = file.replace("_reproduced.ipynb", "_extension.ipynb")
            dst_path = os.path.join(subfolder_path, new_name)

            shutil.copy2(src_path, dst_path)
