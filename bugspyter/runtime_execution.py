from pathlib import Path
import nbformat
import ast
import papermill as pm
import os
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

def load_notebook(notebook_path)-> nbformat.NotebookNode:
    nb = nbformat.read(notebook_path, as_version=4)
    return nb
    
def get_execution_order(nb:nbformat.NotebookNode):
    execution_data = []
    
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type == "code" and cell.execution_count is not None:
            execution_data.append({
                "cell_id": idx,
                "user_order": cell.execution_count
            })
    
    # sort list on the user's execution_count
    execution_data.sort(key=lambda x: x["user_order"])
    return execution_data

def extract_imports(nb:nbformat.NotebookNode):
    imports = set()

    # Go through each code cell
    for cell in nb.cells:
        if cell.cell_type == "code":
            try:
                tree = ast.parse(cell.source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports.add(n.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
            except Exception:
                continue
    return imports
        
def get_notebook_metadata(nb:nbformat.NotebookNode):
    metadata= nb.metadata
    metadata_formatted = []
    imports = extract_imports(nb)
    metadata_formatted.append({"kernelspec":metadata.kernelspec,
                               "version":metadata.language_info.version,
                               "imports":imports
                               })
    return metadata_formatted

def execute_notebook_linear(notebook_path: str):
    notebook_file_path = Path(notebook_path)
    output = notebook_file_path.stem +"_output.ipynb"
    try:
        pm.execute_notebook(
            notebook_path,
            output,   
            raise_on_error=True,
        )
    except pm.PapermillExecutionError as e:
        pass
    finally:
        runtime_cells = []
        nb = load_notebook(output)
        for index, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue
            
            execution_info = cell.metadata.get("execution")
            if not execution_info:
                continue
            
            metadata=cell.metadata
            pm_meta = metadata.get("papermill", {})
            errors = []
            
            if(pm_meta.get("exception") is True):
                for out in cell.get("outputs", []):
                    if out.get("output_type") == "error":
                        tb_list = out.get("traceback", [])
                        errors.append({
                                "exception_type": out.get("ename"),
                                "exception_message": out.get("evalue"),
                                "traceback": "\n".join(tb_list) if tb_list else None
                            })
                
            runtime_cells.append({
                "cell_index": index,
                "source": cell.source,
                "execution_count": cell.get("execution_count"),
                "start_time": pm_meta.get("start_time"),
                "end_time": pm_meta.get("end_time"),
                "duration": pm_meta.get("duration"),
                "error": pm_meta.get("exception", False),
                "errors":errors,
                "outputs": cell.get("outputs", [])
            })
        
        if os.path.exists(output):
            os.remove(output)
        return runtime_cells

def execute_notebook_user_order(nb:nbformat.NotebookNode, execution_order):
    """ Execute the notebook following the user's execution order"""
    
    kernelspec = nb.metadata.get("kernelspec", {})
    kernel_name = kernelspec.get("name", None)
    
    client = NotebookClient(
        nb,
        timeout=600,
        kernel_name=kernel_name
    )
        
    results = []
    try:
        with client.setup_kernel():
            for item in execution_order:
                cell_index = item["cell_id"]
                cell = nb.cells[cell_index]

                try:
                    client.execute_cell(cell, cell_index)
                    error = False
                except CellExecutionError:
                    error = True

                results.append({
                    "cell_index": cell_index,
                    "source": cell.source,
                    "execution_count": cell.execution_count,
                    "outputs": cell.outputs,
                    "error": error
                })

                if error:
                    break

    finally:
        # Ensures cleanup if needed
        pass

    return results