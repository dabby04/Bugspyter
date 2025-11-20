from pathlib import Path
import nbformat
import ast
import papermill as pm

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

def execute_notebook_linear(notebook_path):
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
        return output

def return_runtime_cells(nb:nbformat.NotebookNode):
    runtime_cells = []

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
    return runtime_cells
