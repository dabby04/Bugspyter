# get the notebook you want to run
# convert to python script

# ignore:   extract code cells from the notebook
# ignore:   iterate through these code cells in the notebook
# ignore:   for each cell, create a python file
# pass that python file to bandit
# return results of bandit as a string
# use that result in chat.py
    
# read the whole txt file as an input to the LLM after sending in the notebook
import json
import os
from pathlib import Path
import nbformat
from nbconvert import PythonExporter
import subprocess

def run_bandit(notebook_path):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Failed to load {notebook_path}: {e}")
        return
    
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            content=nbformat.read(f, as_version=4)
        
        exporter=PythonExporter()
        script, _ = exporter.from_notebook_node(content)
        
        name=Path(notebook_path).stem
        output_dir=Path(notebook_path).parent
        output_script_path= output_dir/(name+ ".py")
        with open(output_script_path, 'w', encoding='utf-8') as script_file:
            script_file.write(script)
        
        json_output=output_dir/(name+".json")
        subprocess.check_call(["bandit","-r",str(output_script_path),"-f","json","-o",str(json_output)])
        
        # stringify content in json path
        with open(json_output, 'r', encoding='utf-8') as json_file:
            bandit_results = json.load(json_file)
            json_string = json.dumps(bandit_results, indent=4)
        # delete output_script_path (python script)
        os.remove(output_script_path)
        # delete json_output (json file)
        os.remove(json_output)
        # return json string
        return json_string
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
