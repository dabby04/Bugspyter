FROM jupyter/base-notebook:python-3.10

USER root
WORKDIR /home/jovyan/bugspyter

# Build tools for lab extensions
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y curl jq

USER ${NB_UID}
ENV PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
