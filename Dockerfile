# Use an appropriate base image
FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts during installations
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /workspace

# Update the package list and install required packages, including OpenSSL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    cmake \
    git \
    python3 \
    python3-pip \
    python3-venv \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file if you have one
# COPY requirements.txt .

# Install any dependencies
# RUN pip install -r requirements.txt

# Install pytest
RUN pip install pytest

# Create the virtual environment (if not already created)
RUN python3 -m venv /opt/venv

# Ensure pip is installed and upgrade it within the virtual environment
RUN /opt/venv/bin/pip install --upgrade pip

# Install Python packages: coverage, ruff in the virtual environment
RUN /opt/venv/bin/pip install coverage ruff

# Clone, build, and install Google Test and Google Mock
RUN git clone https://github.com/google/googletest.git /usr/src/googletest && \
    cd /usr/src/googletest && \
    cmake -DBUILD_GMOCK=ON . && \
    make && \
    make install && \
    rm -rf /usr/src/googletest

# Clean up unnecessary files (optional to reduce image size)
RUN rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /workspace

# Confirm installation of ctypes using the virtual environment's Python
RUN /opt/venv/bin/python -c "import ctypes"

# Confirm OpenSSL installation
RUN openssl version