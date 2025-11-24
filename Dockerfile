# Simplified single-stage build with pre-built frontend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Install only essential Python dependencies (lighter packages first)
RUN pip install --no-cache-dir gunicorn Flask Flask-SQLAlchemy Flask-CORS && \
    pip install --no-cache-dir psycopg2-binary requests python-dotenv langdetect MSAL && \
    pip install --no-cache-dir sentence-transformers faiss-cpu

# Create directory for vector store
RUN mkdir -p chroma_db

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run gunicorn
CMD gunicorn --bind 0.0.0.0:8080 --workers 1 --timeout 120 flask_app:app
