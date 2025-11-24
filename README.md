A RAG system to automatically respond to emails.

## Features

- 📚 **Multi-format Support**: PDF, DOCX, and TXT files
- 🎯 **Semantic Search**: Uses sentence transformers for accurate retrieval
- 🤖 **Free LLM**: Free Groq key for answer generation
- 💾 **Persistent Storage**: PostgreSQL integration for local storage, or supabase for online storage

## System Requirements

- Python 3.14.0 ✓
- NVIDIA GPU (CUDA compatible) ✓
- ~5GB disk space for models
- 8GB+ RAM

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: This will download:
- PyTorch with CUDA support
- HuggingFace Transformers
- Sentence Transformers
- ChromaDB
- Document processing libraries

### Step 2: First Run (Downloads Models)

On first run, the system will automatically download:
- **Embedding Model**: `all-MiniLM-L6-v2` (~80MB)
- **LLM**: `google/flan-t5-base` (~900MB)

Models are cached locally and won't be downloaded again.

## Quick Start

### 1. Prepare Your Documents

Create a `documents` folder and add your files:

```bash
mkdir documents
# Copy your PDF, DOCX, or TXT files into this folder
```

### 2. Run the System

```bash
python main.py
```

### 3. Index Your Documents

- Choose option `1` from the menu
- The system will process all files in the `documents` folder

### 4. Ask Questions

- Choose option `2` from the menu
- Type your questions
- Get answers based on your documents!

## Usage Example

```
❓ Your question: What is machine learning?

📝 ANSWER:
Machine learning is a subset of artificial intelligence that enables
systems to learn and improve from experience without being explicitly
programmed...

📚 SOURCES:
1. From: ml_introduction.pdf
   Relevance: 94.23%
   Excerpt: Machine learning (ML) is a field of study...
```

## How It Works

1. **Document Loading**: Reads PDF, DOCX, and TXT files
2. **Text Chunking**: Splits documents into overlapping chunks
3. **Embedding**: Converts chunks to vector embeddings
4. **Vector Storage**: Stores embeddings in ChromaDB
5. **Retrieval**: Finds relevant chunks for your query
6. **Generation**: Uses local LLM to generate contextual answers

