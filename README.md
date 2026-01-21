# Bugspyter


A JupyterLab extension that uses an agent-based model to detect buggy and vulnerable code.

This extension is composed of a Python package named `bugspyter`
for the server extension and a NPM package named `bugspyter`
for the frontend extension.

![ToolDemo](https://github.com/user-attachments/assets/2a13fe1e-e2e1-47b4-9907-976ef18fb30d)


## Requirements

- JupyterLab >= 4.0.0

# Getting Started
To start using Bugspyter, follow these installation and execution steps:

## Install
1. First clone this repository to your local system.
2. In this current working directory, run
```
docker build --no-cache -t bugspyter:dev .
```
3. Once the application has been built, run:
```
docker run --rm -it \
  -p 8888:8888 \
  -e NB_UID="$(id -u)" -e NB_GID="$(id -g)" \
  -v "$PWD":/home/jovyan/bugspyter \
  bugspyter:dev bash
```
4. In the Docker shell, run:
```
pip install -e .
```
## Launch
1. In the same Docker shell, start JupyterLab:
```
jupyter lab --ip 0.0.0.0 --no-browser
```
2. Open the printed URL in your browser (http://localhost:8888/…).
3. You should see the Bugspyter icon at the top right of the ribbon bar.

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

If it is installed, try:

```
jupyter lab clean
jupyter lab build
```

# Running Evaluations
We provide helper scripts to help automate the process of running evaluations.

**To run evaluations on Santana et al.'s dataset:**

1. First extract the notebooks by running:
```
bash experiments/extract_notebooks_Santana.sh experiments/implementation_notebooks_Santana.csv
```

2. Run 
```
python ./automate/run_all_Santana.py
```

Note: Update CHOSEN_MODEL, SELECTED_LLM, SELECTED_MODEL, and API_KEY in automate/run_all_Santana.py (or set them as environment variables) before running.

**To run evaluations on JunoBench's benchmark dataset:**
1. First clone the repository on HuggingFace in the open terminal:
```
git clone https://huggingface.co/datasets/PELAB-LiU/JunoBench
```

2. Follow the instruction for `docker pull` on their HuggingFace Repo:
```
docker pull yarinamomo/kaggle_python_env:latest
```

3.  In the terminal for this active JunoBench project, run:
```
docker run \
  -v "$(pwd):/junobench_env" \
  -v "PATH_TO_CLONED_BUGSPYTER_REPO":/home/jovyan/bugspyter/" \
  -w /junobench_env \
  -p 8888:8888 \
  -it yarinamomo/kaggle_python_env:latest \
  bash
  ```
4. In the Docker shell, run:
```
pip install -e /home/jovyan/bugspyter
```
5. Run 
```
python /home/jovyan/bugspyter/automate/run_all_JunoBench.py
```
