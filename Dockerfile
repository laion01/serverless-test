FROM runpod/base:0.6.3-cuda11.8.0

# Install Python 3.11 and pip
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Set python3.11 as default
RUN ln -sf $(which python3.11) /usr/local/bin/python && \
    ln -sf $(which python3.11) /usr/local/bin/python3 && \
    ln -sf /usr/local/bin/pip3 /usr/local/bin/pip

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /requirements.txt --no-cache-dir

# Copy your handler code
ADD handler.py .

# Run the handler
CMD ["python", "-u", "/handler.py"]
