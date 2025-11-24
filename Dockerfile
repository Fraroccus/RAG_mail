# Simplified single-stage build with pre-built frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Create necessary directories
RUN mkdir -p chroma_db workspaces

# Expose Hugging Face Spaces port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

# Run gunicorn on port 7860
CMD gunicorn --bind 0.0.0.0:7860 --workers 1 --timeout 120 flask_app:app