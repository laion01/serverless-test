FROM runpod/base:0.6.3-cuda11.8.0

# Optional: confirm Python version
RUN python --version

# Install dependencies
COPY requirements.txt /requirements.txt
RUN pip install --upgrade -r /requirements.txt --no-cache-dir

# Add files
ADD handler.py .

# Run the handler
CMD ["python", "-u", "/handler.py"]
