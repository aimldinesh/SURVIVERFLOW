# FROM quay.io/astronomer/astro-runtime:12.6.0

# RUN pip install apache-airflow-providers-google

# Use Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (for Redis and Prometheus support)
RUN apt-get update && apt-get install -y build-essential gcc

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Flask + Prometheus ports
EXPOSE 5000 8000

# Start Flask app
CMD ["python", "app.py"]

