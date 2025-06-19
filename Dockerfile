# FROM quay.io/astronomer/astro-runtime:12.6.0

# RUN pip install apache-airflow-providers-google

# Use official Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables to improve performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements separately to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy entire project
COPY . .

# Expose Flask and Prometheus ports
EXPOSE 5000 8000

# Start Flask app using gunicorn (production-grade)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

