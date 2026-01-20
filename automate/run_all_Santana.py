import os
import subprocess
import json
from bugspyter.chat_Santana import request_api_key, load_notebook, analysis

CHOSEN_MODEL = "gemini-2.0-flash"
SELECTED_LLM = "Gemini"
SELECTED_MODEL = CHOSEN_MODEL
API_KEY = "ENTER_API_KEY"

# Path to your Benchmark folder
BENCHMARK_DIR = os.path.join("experiments","notebooks")

# Path to output folder
EXPERIMENTS_DIR = os.path.join("/home/jovyan/bugspyter/", "experiments", "Santana", CHOSEN_MODEL)
os.makedirs(EXPERIMENTS_DIR, exist_ok=True)

# Init LLM once
init_msg = request_api_key(SELECTED_LLM, SELECTED_MODEL, API_KEY)
print(f"LLM init: {init_msg}")

# Loop over notebooks
processed = 0
for file in sorted(os.listdir(BENCHMARK_DIR)):
    if not file.endswith(".ipynb"):
        continue

    notebook_path = os.path.join(BENCHMARK_DIR, file)

    # Construct output JSON path
    json_file_name = os.path.splitext(file)[0] + ".json"
    json_file_path = os.path.join(EXPERIMENTS_DIR, json_file_name)

    # Skip if already processed
    if os.path.exists(json_file_path):
        print(f"Skipping (already processed): {notebook_path}")
        continue

    print(f"Processing: {notebook_path}")

    # Load notebook and parse result
    loaded = load_notebook(notebook_path)
    buggy_questions = json.loads(loaded) if isinstance(loaded, str) else (loaded or {})

    # Run analysis
    analysis_text = analysis()

    # Build requested output shape
    output = {
        "buggy_or_not": buggy_questions.get("buggy_or_not_final", buggy_questions.get("buggy_or_not")),
        "major_bug": buggy_questions.get("major_bug"),
        "root_cause": buggy_questions.get("root_cause"),
        "analysis": analysis_text,
    }

    # Write JSON
    with open(json_file_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote: {json_file_path}")
    processed += 1

print(f"Processed files: {processed}")