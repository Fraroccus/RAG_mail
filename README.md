# Local RAG System

A fully local Retrieval-Augmented Generation (RAG) system using HuggingFace models. No API keys required!

## Features

- 🔒 **100% Local**: All processing happens on your machine
- 🚀 **GPU Accelerated**: Utilizes your NVIDIA RTX 1000 Ada
- 📚 **Multi-format Support**: PDF, DOCX, and TXT files
- 🎯 **Semantic Search**: Uses sentence transformers for accurate retrieval
- 🤖 **Local LLM**: Google Flan-T5 for answer generation
- 💾 **Persistent Storage**: ChromaDB for vector embeddings

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

## Project Structure

```
APP/
├── main.py                 # CLI interface
├── rag_system.py          # Main RAG pipeline
├── document_loader.py     # Document loading
├── text_chunker.py        # Text chunking
├── vector_store.py        # Vector database
├── local_llm.py          # Local LLM
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── documents/            # Your documents (create this)
└── chroma_db/           # Vector database (auto-created)
```

## Configuration

Edit `config.py` to customize:

- **Models**: Change embedding or LLM models
- **Chunk Size**: Adjust text chunking parameters
- **Retrieval**: Modify number of retrieved chunks
- **Generation**: Tune temperature and token limits

### Alternative LLM Options

In `config.py`, you can uncomment these for better quality (larger models):

```python
# Better quality, larger size:
LLM_MODEL = "google/flan-t5-large"  # ~3GB

# Different architecture:
LLM_MODEL = "facebook/opt-1.3b"  # ~2.5GB
```

## How It Works

1. **Document Loading**: Reads PDF, DOCX, and TXT files
2. **Text Chunking**: Splits documents into overlapping chunks
3. **Embedding**: Converts chunks to vector embeddings
4. **Vector Storage**: Stores embeddings in ChromaDB
5. **Retrieval**: Finds relevant chunks for your query
6. **Generation**: Uses local LLM to generate contextual answers

## Troubleshooting

### CUDA Out of Memory

If you get GPU memory errors, edit `config.py`:

```python
# Use smaller model
LLM_MODEL = "google/flan-t5-small"  # ~300MB
```

### Slow Performance

- First run is slower (model downloads)
- CPU mode is slower than GPU
- Larger documents take more time to index

### No Documents Found

Make sure:
- `documents` folder exists
- Files are in supported formats (.txt, .pdf, .docx)
- Files have actual content

## Performance Tips

1. **Batch Processing**: Index all documents at once
2. **GPU Usage**: Make sure CUDA is detected (check stats)
3. **Chunk Size**: Smaller chunks = more precise but slower
4. **Model Selection**: Smaller models = faster but less capable

## License

Open source - use freely!

## Credits

Built with:
- HuggingFace Transformers
- Sentence Transformers
- ChromaDB
- PyTorch
