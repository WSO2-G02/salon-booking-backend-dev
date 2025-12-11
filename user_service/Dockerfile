# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Avoid Python writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (optional but recommended)
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Upgrade pip to fix CVE-2025-8869
RUN pip install --upgrade pip

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose FastAPI port
EXPOSE 8001

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
