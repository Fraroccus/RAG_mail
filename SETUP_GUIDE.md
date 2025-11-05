# RAG System - Step-by-Step Setup Guide

## 🎯 What You Need to Do

Follow these steps exactly to get your RAG system running!

---

## Step 1: Install Dependencies (5-10 minutes)

**IMPORTANT:** Use `python -m pip` instead of just `pip`!

Open PowerShell in this directory and run:

```powershell
python -m pip install -r requirements.txt
```

**If you see "pip not recognized" error:**
- This is normal on some Windows installations
- Always use `python -m pip` instead of `pip`
- See `INSTALLATION_FIX.md` for detailed help

**What this does:**
- Installs PyTorch with CUDA support for your RTX 1000 Ada GPU
- Installs HuggingFace libraries for AI models
- Installs ChromaDB for vector storage
- Installs document processing tools

**Expected output:**
- Lots of download progress bars
- Should complete without errors
- If you see errors, see troubleshooting below

---

## Step 2: First Run (Downloads Models - 5-10 minutes)

Run the main program:

```powershell
python main.py
```

**What happens:**
1. System checks for GPU (should detect your RTX 1000 Ada)
2. Downloads embedding model (~80MB) - happens once
3. Downloads LLM model (~900MB) - happens once
4. Initializes vector database
5. Shows you the main menu

**Models downloaded to:**
- `C:\Users\LAVORO\.cache\huggingface\hub\`

These are cached and won't be downloaded again!

---

## Step 3: Index Sample Documents (30 seconds)

The system comes with 3 sample documents in the `documents` folder:
- `ai_introduction.txt` - About AI and machine learning
- `python_guide.txt` - Python programming guide
- `rag_guide.txt` - Information about RAG systems

**To index them:**
1. From the main menu, choose option `1` (Index documents)
2. Press ENTER to start
3. Wait for processing to complete

**What you'll see:**
```
Loading: ai_introduction.txt
Loading: python_guide.txt
Loading: rag_guide.txt

Loaded 3 documents
Created X chunks from 3 documents
Generating embeddings for X texts...
✓ Successfully added X chunks to vector store
```

---

## Step 4: Ask Questions! (Instant responses)

**To query the system:**
1. From the main menu, choose option `2` (Query)
2. Type your question
3. Get an answer with sources!

**Example questions to try:**
- "What is machine learning?"
- "How do I use Python for data science?"
- "What is a RAG system?"
- "What are the components of RAG?"
- "Tell me about deep learning"

**Example interaction:**
```
❓ Your question: What is machine learning?

🔍 Searching vector database...
✓ Found 3 relevant chunks

🤖 Generating answer...

📝 ANSWER:
Machine learning is a subset of artificial intelligence that enables
systems to learn and improve from experience without being explicitly
programmed...

📚 SOURCES:
1. From: ai_introduction.txt
   Relevance: 94.23%
   Excerpt: Machine learning is a subset of AI...
```

---

## Step 5: Add Your Own Documents

**To add your own documents:**

1. Place your files in the `documents` folder:
   - Supported: `.txt`, `.pdf`, `.docx`
   - Any topic or content

2. Run the program and choose option `1` to index

3. Ask questions about your documents!

---

## 📊 System Menu Options

```
1. Index documents - Add/update documents in the system
2. Query the system - Ask questions
3. Show statistics - See system info
4. Clear index - Remove all indexed documents
5. Exit - Close the program
```

---

## 🔧 Troubleshooting

### Installation Issues

**Problem: `pip install` fails**
```powershell
# Try upgrading pip first
python -m pip install --upgrade pip

# Then try again
pip install -r requirements.txt
```

**Problem: CUDA not detected**
- Check GPU drivers are up to date
- System will work on CPU (just slower)
- Verify with: `nvidia-smi` in PowerShell

### Runtime Issues

**Problem: "No module named 'xxx'"**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem: Out of memory error**
- Close other GPU-intensive programs
- In `config.py`, change to smaller model:
  ```python
  LLM_MODEL = "google/flan-t5-small"  # Smaller, faster
  ```

**Problem: Slow generation**
- First run is slower (downloading models)
- GPU mode should be fast
- Check GPU is detected in stats (option 3)

**Problem: Poor quality answers**
- Try larger model in `config.py`:
  ```python
  LLM_MODEL = "google/flan-t5-large"  # Better quality
  ```
- Increase `TOP_K_RESULTS` for more context

### Document Issues

**Problem: "No documents found"**
- Ensure `documents` folder exists
- Check files are in supported formats
- Verify files aren't empty

**Problem: PDF extraction fails**
```powershell
pip install pypdf --upgrade
```

---

## 🎓 Understanding the System

### What happens when you index?

1. **Load**: Read all documents from `documents` folder
2. **Chunk**: Split into ~500 character pieces with overlap
3. **Embed**: Convert each chunk to vector (numbers)
4. **Store**: Save in ChromaDB vector database

### What happens when you query?

1. **Embed Query**: Convert your question to a vector
2. **Search**: Find similar vectors in database
3. **Retrieve**: Get top 3 most relevant chunks
4. **Generate**: LLM creates answer using context

---

## 🚀 Performance Tips

1. **First time is slower** - Models download once
2. **GPU speeds up generation** - Make sure it's detected
3. **Smaller chunks = more precise** - Edit in `config.py`
4. **More retrieval = better context** - Increase `TOP_K_RESULTS`
5. **Index once, query many** - No need to re-index

---

## 📁 File Structure After Setup

```
APP/
├── main.py                    # Run this!
├── rag_system.py             # Core logic
├── document_loader.py        # File loading
├── text_chunker.py           # Text splitting
├── vector_store.py           # Embeddings
├── local_llm.py              # AI model
├── config.py                 # Settings (edit this!)
├── requirements.txt          # Dependencies
├── README.md                 # Documentation
├── SETUP_GUIDE.md           # This file!
├── documents/                # Your files here
│   ├── ai_introduction.txt
│   ├── python_guide.txt
│   └── rag_guide.txt
└── chroma_db/               # Vector database (auto-created)
    └── [database files]
```

---

## 🎯 Quick Start Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run program: `python main.py`
- [ ] Wait for models to download
- [ ] Index sample documents (option 1)
- [ ] Try asking questions (option 2)
- [ ] Add your own documents
- [ ] Enjoy your local RAG system!

---

## 💡 Next Steps

Once everything works:

1. **Experiment with different questions**
2. **Add your own documents** (PDFs, Word docs, text files)
3. **Adjust settings** in `config.py`
4. **Try different models** for better quality
5. **Build on top** - this is your foundation!

---

## ❓ Common Questions

**Q: Do I need internet?**
A: Only for initial downloads. After that, fully offline!

**Q: Can I use different models?**
A: Yes! Edit `config.py` and change `LLM_MODEL`

**Q: How much does this cost?**
A: FREE! No API keys, no subscriptions

**Q: Can I delete the models?**
A: They're in `C:\Users\LAVORO\.cache\huggingface\`
   Delete to free space, will re-download if needed

**Q: Can I process private documents?**
A: YES! Everything stays on your machine

**Q: How do I update documents?**
A: Just clear index (option 4) and re-index

---

## 🎉 You're Ready!

Your local RAG system is ready to use. No API keys, no cloud dependencies, just pure local AI power!

**Happy querying! 🚀**
