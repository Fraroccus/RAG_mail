# RAG System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         LOCAL RAG SYSTEM                             │
│                    (No API Keys | 100% Local)                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                             │
│                            (main.py)                                 │
│  ┌────────┐  ┌────────┐  ┌──────┐  ┌───────┐  ┌──────┐            │
│  │ Index  │  │ Query  │  │ Stats│  │ Clear │  │ Exit │            │
│  └────────┘  └────────┘  └──────┘  └───────┘  └──────┘            │
└───────┬────────────┬──────────────────────────────────────────────┘
        │            │
        │            │
        ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE                                 │
│                        (rag_system.py)                               │
│                                                                       │
│  Orchestrates: Loading → Chunking → Embedding → Storage → Retrieval │
└─────────────────────────────────────────────────────────────────────┘
        │
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      COMPONENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │  DOCUMENT       │  │  TEXT           │  │  VECTOR          │   │
│  │  LOADER         │  │  CHUNKER        │  │  STORE           │   │
│  │                 │  │                 │  │                  │   │
│  │ • Load PDFs     │  │ • Split text    │  │ • Embeddings     │   │
│  │ • Load DOCX     │  │ • Overlap       │  │ • ChromaDB       │   │
│  │ • Load TXT      │  │ • Metadata      │  │ • Similarity     │   │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘   │
│                                                                       │
│  ┌─────────────────┐                                                │
│  │  LOCAL LLM      │                                                │
│  │                 │                                                │
│  │ • Flan-T5       │                                                │
│  │ • GPU/CPU       │                                                │
│  │ • Generation    │                                                │
│  └─────────────────┘                                                │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
        │
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        MODEL LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐    │
│  │   EMBEDDING MODEL            │  │   LANGUAGE MODEL         │    │
│  │                              │  │                          │    │
│  │   all-MiniLM-L6-v2          │  │   google/flan-t5-base    │    │
│  │   Size: ~80MB               │  │   Size: ~900MB           │    │
│  │   Device: GPU               │  │   Device: GPU            │    │
│  │   Purpose: Semantic Search   │  │   Purpose: Generation    │    │
│  └──────────────────────────────┘  └──────────────────────────┘    │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
        │
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────┐    ┌──────────────────────┐              │
│  │   VECTOR DATABASE    │    │   DOCUMENTS FOLDER   │              │
│  │                      │    │                      │              │
│  │   ChromaDB           │    │   • PDFs             │              │
│  │   (./chroma_db/)     │    │   • DOCX             │              │
│  │                      │    │   • TXT              │              │
│  │   Stores:            │    │   • Your files       │              │
│  │   • Embeddings       │    │                      │              │
│  │   • Metadata         │    │                      │              │
│  │   • Text chunks      │    │                      │              │
│  └──────────────────────┘    └──────────────────────┘              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. INDEXING FLOW (Adding Documents)

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  1. Document Loader         │
│  • Scan documents/ folder   │
│  • Load PDF/DOCX/TXT        │
│  • Extract text content     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  2. Text Chunker            │
│  • Split into 500 char      │
│  • 50 char overlap          │
│  • Add metadata             │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  3. Embedding Model         │
│  • Convert to vectors       │
│  • all-MiniLM-L6-v2         │
│  • GPU acceleration         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  4. Vector Store            │
│  • Save to ChromaDB         │
│  • Index for search         │
│  • Persist to disk          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────┐
│     DONE    │
└─────────────┘
```

### 2. QUERY FLOW (Asking Questions)

```
┌─────────────┐
│   USER      │
│  QUESTION   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  1. Embed Query             │
│  • Convert question         │
│  • To vector embedding      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  2. Similarity Search       │
│  • Search ChromaDB          │
│  • Find top K chunks        │
│  • Ranked by relevance      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  3. Build Context           │
│  • Combine retrieved chunks │
│  • Add to prompt template   │
│  • Include question         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  4. Generate Answer         │
│  • Local LLM (Flan-T5)      │
│  • Process on GPU           │
│  • Generate response        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  5. Format & Display        │
│  • Show answer              │
│  • Show sources             │
│  • Show relevance scores    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────┐
│    ANSWER   │
│  + SOURCES  │
└─────────────┘
```

---

## Component Details

### Document Loader (`document_loader.py`)

**Purpose**: Load various document formats
**Input**: File paths
**Output**: Text content + metadata

```python
Supported Formats:
├── .txt  → Plain text
├── .pdf  → PyPDF extraction
└── .docx → python-docx parsing
```

---

### Text Chunker (`text_chunker.py`)

**Purpose**: Split documents into searchable chunks
**Strategy**: Overlapping fixed-size chunks

```
Document: "ABCDEFGHIJKLMNOP"
Chunk Size: 6
Overlap: 2

Chunk 1: "ABCDEF"
Chunk 2: "EFGHIJ"  (EF overlaps)
Chunk 3: "IJKLMN"  (IJ overlaps)
Chunk 4: "MNOP"    (MN overlaps)
```

**Why overlap?** Ensures context isn't lost at chunk boundaries

---

### Vector Store (`vector_store.py`)

**Purpose**: Semantic search over document chunks
**Technology**: ChromaDB + Sentence Transformers

```
How it works:
1. Text → Embedding Model → 384-dim vector
2. Store vectors in ChromaDB
3. Query → vector → find similar vectors
4. Return closest matches
```

**Embedding Model**: `all-MiniLM-L6-v2`
- 384 dimensions
- Trained on 1B+ sentence pairs
- Fast and accurate

---

### Local LLM (`local_llm.py`)

**Purpose**: Generate answers from context
**Model**: Google Flan-T5-Base

```
Prompt Template:
┌─────────────────────────────────┐
│ Answer based on context:        │
│                                  │
│ Context:                         │
│ [Retrieved chunk 1]              │
│ [Retrieved chunk 2]              │
│ [Retrieved chunk 3]              │
│                                  │
│ Question: [User question]        │
│                                  │
│ Answer:                          │
└─────────────────────────────────┘
       ↓
  [LLM processes]
       ↓
  Generated answer
```

---

## Hardware Utilization

### GPU (NVIDIA RTX 1000 Ada)

```
Used for:
├── Embedding generation (fast)
├── LLM inference (fast)
└── Batch processing

Benefits:
├── 5-10x faster than CPU
├── Can handle larger models
└── Better user experience
```

### CPU Fallback

```
If no GPU:
├── System still works
├── Slower inference
└── Same accuracy
```

---

## Configuration (`config.py`)

All tuneable parameters:

```python
# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "google/flan-t5-base"

# Device
DEVICE = "cuda" / "cpu"  # Auto-detected

# Chunking
CHUNK_SIZE = 500        # Characters per chunk
CHUNK_OVERLAP = 50      # Overlap size

# Retrieval
TOP_K_RESULTS = 3       # Chunks to retrieve

# Generation
MAX_NEW_TOKENS = 256    # Max answer length
TEMPERATURE = 0.7       # Creativity (0-1)
```

---

## File Manifest

```
APP/
│
├── Core Components
│   ├── main.py              # CLI interface
│   ├── rag_system.py        # Pipeline orchestrator
│   ├── document_loader.py   # Document reading
│   ├── text_chunker.py      # Text splitting
│   ├── vector_store.py      # Embedding & search
│   └── local_llm.py         # Answer generation
│
├── Configuration
│   └── config.py            # All settings
│
├── Dependencies
│   └── requirements.txt     # Python packages
│
├── Documentation
│   ├── README.md            # Overview
│   ├── SETUP_GUIDE.md       # Detailed setup
│   ├── QUICK_START.txt      # Quick reference
│   └── ARCHITECTURE.md      # This file
│
├── Utilities
│   └── install.bat          # Windows installer
│
├── Data Directories
│   ├── documents/           # Your documents
│   │   ├── ai_introduction.txt
│   │   ├── python_guide.txt
│   │   └── rag_guide.txt
│   └── chroma_db/          # Vector database (created on first run)
│
└── Cache (auto-created)
    └── C:\Users\LAVORO\.cache\huggingface\
        └── [Downloaded models]
```

---

## Performance Characteristics

### Speed Benchmarks (RTX 1000 Ada)

```
Operation               Time
─────────────────────────────────
Load 1 document         <1s
Chunk 1000 words        <1s
Generate embeddings     1-2s
Store in ChromaDB       <1s
Search query            <0.5s
Generate answer         2-5s
─────────────────────────────────
Total query time:       3-7s
```

### Resource Usage

```
Component           RAM     VRAM    Disk
─────────────────────────────────────────
Embedding model     500MB   500MB   80MB
LLM model          1-2GB   1GB     900MB
ChromaDB           100MB   -       varies
Total              ~2.5GB  ~1.5GB  ~1GB + docs
```

---

## Extension Points

Want to customize? Here are the extension points:

### Add New Document Types

Edit `document_loader.py`:
```python
def load_markdown(self, file_path: str) -> str:
    # Your markdown parsing logic
    pass
```

### Change Chunking Strategy

Edit `text_chunker.py`:
```python
# Implement semantic chunking
# Implement sentence-based chunking
# Implement paragraph-based chunking
```

### Use Different Models

Edit `config.py`:
```python
# Larger LLM for better quality
LLM_MODEL = "google/flan-t5-large"

# Different embedding model
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
```

### Add Preprocessing

Edit `document_loader.py`:
```python
def preprocess_text(self, text: str) -> str:
    # Clean text
    # Remove headers/footers
    # Normalize formatting
    return cleaned_text
```

---

## Security & Privacy

```
✓ All processing happens locally
✓ No data sent to external servers
✓ No API keys required
✓ No telemetry or tracking
✓ Models cached locally
✓ Full control over your data
```

---

## Comparison: Local vs Cloud RAG

```
Feature              Local RAG          Cloud RAG
─────────────────────────────────────────────────────
Privacy              ✓ 100% private     ✗ Data sent to API
Cost                 ✓ Free forever     ✗ Pay per use
Internet Required    ✗ Only for setup   ✓ Always
Speed                ○ Good with GPU    ✓ Very fast
Quality              ○ Good             ✓ Excellent
Setup Difficulty     ○ Medium           ✓ Easy
Resource Usage       ✗ ~3GB RAM/VRAM    ✓ Minimal
Model Control        ✓ Full control     ✗ Limited
Customization        ✓ Full access      ○ Limited
```

---

This architecture provides a solid foundation for local RAG while remaining
simple, maintainable, and extensible!
