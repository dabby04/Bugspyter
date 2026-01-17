import json
import sys
import os

# Allow running as a module (python -m bugspyter.script) and as a file (python bugspyter/script.py)
try:
    # When run as a module, relative imports work
    from .chat import llm_call_router, request_api_key, router_workflow
    from .chat import load_notebook
    from .chat import load_notebook_content
except ImportError:
    # When run directly, add project root to sys.path and use absolute imports
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from bugspyter.chat import llm_call_router, request_api_key, router_workflow
    from bugspyter.chat import load_notebook
    from bugspyter.chat import load_notebook_content

argument = sys.argv[1]  # Notebook path or name provided by user

# Resolve notebook path: accept absolute, else resolve against current working directory
if os.path.isabs(argument):
    notebook_path = argument
else:
    notebook_path = os.path.abspath(os.path.join(os.getcwd(), argument))

selectedLLM="SELECTED_LLM"
selectedModel= "SELECTED_MODEL"
key="API_KEY"
result=request_api_key(selectedLLM,selectedModel,key)

data = notebook_path
result = json.loads(load_notebook_content(data))
docs = result["docs"]
bandit_report= result["bandit_report"]
load_notebook(docs, bandit_report)

decision = llm_call_router({
    "input": "Decide if runtime or analysis is required."
    })["decision"]

if not decision:
    decision = llm_call_router({"input": "Continue routing based on current memory and reports."})["decision"]
    
result_json = json.loads(router_workflow(decision, notebook_path))
buggy_questions = json.loads(result_json["buggy_questions"])
analysis = result_json["analysis"]
output = {
    "buggy_or_not": buggy_questions["buggy_or_not"],
    "major_bug": buggy_questions["major_bug"],
    "root_cause": buggy_questions["root_cause"],
    "analysis": analysis
}

# Derive output JSON path from the notebook name; save under experiments/gemini-2.5-flash
notebook_filename = os.path.basename(notebook_path)
notebook_stem, _ = os.path.splitext(notebook_filename)

# Base project directory (parent of this file's directory)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_dir = os.path.join(base_dir, "experiments", "NAME_OF_MODEL")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{notebook_stem}.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(output_path)