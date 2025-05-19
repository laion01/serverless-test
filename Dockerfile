FROM python:3.11-slim

WORKDIR /app

# Install git + pip dependencies
RUN apt-get update && apt-get install -y git \
 && pip install --no-cache-dir --upgrade pip

 COPY requirements.txt .
 
 RUN pip install --no-cache-dir -r requirements.txt
 

 ADD handler.py .

 # Run the handler
 CMD python -u /handler.py