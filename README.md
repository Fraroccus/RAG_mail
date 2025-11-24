A RAG system to automatically respond to emails.

## Features

- 📚 **Multi-format Support**: PDF, DOCX, and TXT files
- 🎯 **Semantic Search**: Uses sentence transformers for accurate retrieval
- 🤖 **Free LLM**: Free Groq key for answer generation
- 💾 **Persistent Storage**: PostgreSQL integration for storage
  

## System Requirements

- Python 3.14.0 ✓
- NVIDIA GPU (CUDA compatible) ✓
- ~5GB disk space for models
- 8GB+ RAM

## Workflow

1. Create account
2. Create workspace
3. Set system prompt and upload reference emails
4. Give it a go


## How It Works

1. **Document Loading**: Reads PDF, DOCX, and TXT files
2. **Text Chunking**: Splits documents into overlapping chunks
3. **Embedding**: Converts chunks to vector embeddings
4. **Vector Storage**: Stores embeddings in ChromaDB
5. **Retrieval**: Finds relevant chunks for your query
6. **Generation**: Uses local LLM to generate contextual answers

