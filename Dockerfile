FROM runpod/base:0.6.3-cuda11.8.0

# Set python3.11 as the default python
RUN ln -sf $(which python3.11) /usr/local/bin/python && \
    ln -sf $(which python3.11) /usr/local/bin/python3

# Install dependencies
COPY requirements.txt /requirements.txt
RUN uv pip install --upgrade -r /requirements.txt --no-cache-dir --system
RUN uv pip install --no-cache-dir hf_transfer --system


# Add files
COPY openai_image.py /openai_image.py
COPY realvisxl_image.py /realvisxl_image.py
ADD handler.py .

# Run the handler
CMD python -u /handler.py
