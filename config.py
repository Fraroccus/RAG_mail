"""
Configuration file for the RAG system
"""

import os
import torch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # ~80MB
LLM_MODEL = "google/flan-t5-large"  # ~3GB - better quality, multilingual support

# Alternative LLM options:
# LLM_MODEL = "google/flan-t5-base"  # ~900MB - faster but less capable
# LLM_MODEL = "facebook/opt-1.3b"  # ~2.5GB - different architecture

# Device Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# ChromaDB Configuration
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "local_rag_collection"

# Dual Knowledge Base Collections
COLLECTION_HISTORICAL_EMAILS = "historical_emails_collection"
COLLECTION_ENROLLMENT_DOCS = "enrollment_docs_collection"

# Text Chunking Configuration
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks

# Retrieval Configuration
TOP_K_RESULTS = 3  # number of relevant chunks to retrieve

# Generation Configuration
MAX_NEW_TOKENS = 512  # maximum length of generated response (increased for emails)
TEMPERATURE = 0.7  # creativity (0.0 = deterministic, 1.0 = creative)

# Email System Configuration
EMAIL_CHECK_INTERVAL = 300  # seconds (5 minutes)
AUTO_SEND_ENABLED = False  # manual approval required by default
CONFIDENCE_THRESHOLD = 0.9  # minimum confidence for auto-send (when enabled)

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/email_rag_db')

# Microsoft Graph API Configuration
MS_CLIENT_ID = os.getenv('MS_CLIENT_ID', '')
MS_CLIENT_SECRET = os.getenv('MS_CLIENT_SECRET', '')
MS_TENANT_ID = os.getenv('MS_TENANT_ID', '')
MS_REDIRECT_URI = os.getenv('MS_REDIRECT_URI', 'http://localhost:5000/callback')

# Flask Configuration
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
FLASK_PORT = 5000
FLASK_DEBUG = True

# Email Signature (optional)
EMAIL_SIGNATURE = os.getenv('EMAIL_SIGNATURE', '')
