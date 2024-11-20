FROM ubuntu:20.04

# Set environment variables to avoid interactive prompts during installations
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /workspace

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    cmake \
    git \
    python3 \
    python3-pip \
    libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*



# Install necessary Python packages globally
RUN pip3 install --upgrade pip && \
    pip3 install pytest coverage ruff
# Clone, build, and install Google Test and Google Mock
RUN git clone https://github.com/google/googletest.git /usr/src/googletest && \
    cd /usr/src/googletest && \
    cmake -DBUILD_GMOCK=ON . && \
    make && \
    make install && \
    rm -rf /usr/src/googletest
