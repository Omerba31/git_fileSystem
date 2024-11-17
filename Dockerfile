# Use an official Ubuntu base image
FROM ubuntu:latest

# Set environment variables to avoid interactive prompts during installations
ENV DEBIAN_FRONTEND=noninteractive

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
    python3-dev \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Create the virtual environment (if not already created)
RUN python3 -m venv /opt/venv

# Ensure pip is installed and upgrade it within the virtual environment
RUN /opt/venv/bin/pip install --upgrade pip

# Install Python packages: pytest, coverage, ruff in the virtual environment
RUN /opt/venv/bin/pip install pytest coverage ruff

# Clone, build, and install Google Test and Google Mock
RUN git clone https://github.com/google/googletest.git /usr/src/googletest && \
    cd /usr/src/googletest && \
    cmake -DBUILD_GMOCK=ON . && \
    make && \
    make install && \
    rm -rf /usr/src/googletest

# Clean up unnecessary files (optional to reduce image size)
RUN rm -rf /var/lib/apt/lists/*

# Confirm installation of ctypes using the virtual environment's Python
RUN /opt/venv/bin/python -c "import ctypes"

# Confirm OpenSSL installation
RUN openssl version

# Set the default command to use the virtual environment's Python
CMD ["/opt/venv/bin/python"]
