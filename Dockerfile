FROM mcr.microsoft.com/vscode/devcontainers/base:latest 

ARG VENV_DIR=/tmp/venv

RUN apt-get clean && apt-get update && apt-get install -y --no-install-recommends \
        debian-archive-keyring \
        python3-full \
        python3-pip \
        python3.11-venv \
        && rm -rf /var/lib/apt/lists/*

USER vscode

COPY requirements.txt .
RUN python3 -m venv $VENV_DIR && \
    . $VENV_DIR/bin/activate && \
    pip3 install -r requirements.txt

ENV VIRTUAL_ENV=$VENV_DIR
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

