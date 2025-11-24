# Simplified single-stage build with pre-built frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all application files first
COPY . .

# Install minimal system dependencies and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p chroma_db

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run gunicorn
CMD gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 flask_app:app
