# Multi-stage build to keep image small
FROM node:18-alpine AS frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production --ignore-scripts
COPY frontend/ ./
RUN npm run build

# Python runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application code first
COPY . .

# Install Python dependencies one by one to reduce memory spikes
RUN pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir Flask Flask-SQLAlchemy Flask-CORS && \
    pip install --no-cache-dir psycopg2-binary requests && \
    pip install --no-cache-dir sentence-transformers && \
    pip install --no-cache-dir faiss-cpu && \
    pip install --no-cache-dir python-dotenv langdetect MSAL

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create directory for vector store
RUN mkdir -p chroma_db

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run gunicorn
CMD gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 flask_app:app
