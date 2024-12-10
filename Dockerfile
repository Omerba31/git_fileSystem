FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts during installations
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES 1

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    cmake \
    git \
    python3 \
    python3-dev \
    python3-pip \
    libssl-dev && \
    apt-get clean

# Install necessary Python packages globally
RUN pip3 install --upgrade pip && \
    pip3 install pytest coverage ruff pybind11