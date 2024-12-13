FROM ubuntu:latest

# Set environment variables to avoid interactive prompts during installations
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc g++ make cmake git \
    python3 python3-dev python3-pip python3-venv \
    libssl-dev libssl3 &&\
    apt-get clean

# Create symbolic link for python3 as python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create and activate a virtual environment
RUN python3 -m venv /venv

# Upgrade pip and install necessary Python packages in the virtual environment
RUN /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install pytest pytest-md pytest-emoji coverage ruff pybind11

# Set the virtual environment as the default Python environment
ENV PATH="/venv/bin:$PATH"