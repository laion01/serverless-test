FROM python:3.11-slim

WORKDIR /app

# Install git + pip dependencies
RUN apt-get update && apt-get install -y git \
 && pip install --no-cache-dir --upgrade pip

 COPY requirements_main.txt .
 COPY requirements_git.txt .
 
 RUN pip install --no-cache-dir --pep517 -r requirements_git.txt
 RUN pip install --no-cache-dir -r requirements_main.txt
 

CMD ["python", "runpod_serverless.py"]
