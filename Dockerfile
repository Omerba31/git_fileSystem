FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts during installations
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc g++ make cmake git python3 python3-dev python3-pip \
    libssl-dev libssl3 &&\
    apt-get clean

# Create symbolic link for python3 as python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install necessary Python packages globally
RUN pip3 install --upgrade pip && \
    pip3 install pytest pytest-md pytest-emoji coverage ruff pybind11
