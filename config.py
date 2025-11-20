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

# LLM Configuration - API-based (FAST!)
USE_API_LLM = True  # Use API instead of local model
API_PROVIDER = "groq"  # Options: "groq", "openai", "anthropic"
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')  # Get free key at console.groq.com
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast, current, and high quality

# Local LLM fallback (if USE_API_LLM = False)
LLM_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # ~2.2GB - faster on CPU, decent quality

# Alternative LLM options:
# LLM_MODEL = "microsoft/Phi-3-mini-4k-instruct"  # ~3.8GB - better quality but SLOW on CPU
# LLM_MODEL = "google/flan-t5-large"  # ~3GB - NOT RECOMMENDED for long-form generation
# LLM_MODEL = "HuggingFaceH4/zephyr-7b-beta"  # ~7GB - best quality but needs GPU

# Device Configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

# ChromaDB Configuration
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "local_rag_collection"

# Dual Knowledge Base Collections
COLLECTION_HISTORICAL_EMAILS = "historical_emails_collection"
COLLECTION_ENROLLMENT_DOCS = "enrollment_docs_collection"
COLLECTION_CORRECTIONS = "corrections_collection"  # Feedback-based corrections

# Text Chunking Configuration
CHUNK_SIZE = 300  # characters per chunk (reduced for better context)
CHUNK_OVERLAP = 50  # overlap between chunks

# Retrieval Configuration
TOP_K_RESULTS = 3  # number of relevant chunks to retrieve

# Generation Configuration
MAX_NEW_TOKENS = 1024  # Increased for complete email responses (~700-800 words)
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
FLASK_PORT = int(os.getenv('PORT', 5000))  # Railway/Render use PORT env var
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'  # Default to False in production

# Email Signature (optional)
EMAIL_SIGNATURE = os.getenv('EMAIL_SIGNATURE', '')
