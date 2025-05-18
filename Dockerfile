FROM nvidia/cuda:12.4.0-devel-ubuntu22.04

# Set environment
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV CPATH=/usr/local/cuda/include:/usr/include
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3.11-dev \
    gcc-13 g++-13 lld cmake ninja-build \
    zstd libzstd-dev wget curl git build-essential \
    && ln -sf /usr/bin/gcc-13 /usr/bin/gcc \
    && ln -sf /usr/bin/g++-13 /usr/bin/g++ \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python

# Copy files and install Python dependencies
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Add files
ADD handler.py .

# Run the handler
CMD python -u /handler.py
