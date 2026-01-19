# Bugspyter

[![Github Actions Status](https://github.com/github_username/bugspyter/workflows/Build/badge.svg)](https://github.com/github_username/bugspyter/actions/workflows/build.yml)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/github_username/bugspyter/main?urlpath=lab)


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

To install the extension, execute:

```bash
pip install bugspyter
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall bugspyter
```

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

To run evaluations on Santana et al.'s dataset:

1. First extract the notebooks by running:
```
bash experiments/extract_notebooks_Santana.sh experiments/implementation_notebooks_Santana.csv
```

2. Run `python ./automate/run_all_Santana.py`

To run evaluations on JunoBench's benchmark dataset:
1. First clone the repository on HuggingFace:
```
git clone https://huggingface.co/datasets/PELAB-LiU/JunoBench
```

2. Follow the `docker run` command on their HuggingFace Repository.

