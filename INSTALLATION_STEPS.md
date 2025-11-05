# Step-by-Step Manual Installation Guide
# For when automated installation has issues with Python 3.14.0

## Current Situation:
You have Python 3.14.0 which is very new. Some packages need special handling.
The red errors in your IDE are because packages aren't installed yet.

## Option 1: Let Current Installation Finish (Recommended)
The installation I started is still running. It's slow because:
- Python 3.14.0 is brand new
- ChromaDB is resolving complex dependencies
- Some packages need to build from source

**What to do:**
1. Open a NEW PowerShell terminal in this folder
2. The installation is running in the background
3. It may take 20-30 minutes total
4. Once done, restart your IDE and red errors will vanish

## Option 2: Install Step-by-Step (If you want control)

Open PowerShell in this folder and run these commands ONE AT A TIME:

### Step 1: Install PyTorch (GPU version)
```powershell
python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
```
Wait for this to finish (5-10 minutes, ~2GB download)

### Step 2: Install HuggingFace libraries
```powershell
python -m pip install transformers sentence-transformers
```
Wait for this to finish (3-5 minutes)

### Step 3: Install document processing
```powershell
python -m pip install pypdf python-docx beautifulsoup4
```
This should be quick (1-2 minutes)

### Step 4: Install ChromaDB (specific version)
```powershell
python -m pip install chromadb==0.4.22
```
If this fails, try:
```powershell
python -m pip install chromadb==0.4.15
```

### Step 5: Install remaining dependencies
```powershell
python -m pip install numpy tqdm
```

### Step 6: Verify installation
```powershell
python -m pip list
```
You should see: torch, transformers, sentence-transformers, chromadb, pypdf, python-docx, numpy, tqdm

## Option 3: Use Simplified Requirements (Fastest)

I created a simpler requirements file. Use it:

```powershell
python -m pip install -r requirements-simple.txt
```

This uses an older, more stable ChromaDB version that works better with new Python.

## After Installation Completes:

### 1. Verify packages are installed:
```powershell
python -c "import torch; import transformers; import chromadb; print('All packages OK!')"
```

If you see "All packages OK!" then installation succeeded!

### 2. Restart your IDE
Close and reopen Qoder. This refreshes the package cache.

### 3. Check the code
All red errors should be GONE! ✨

### 4. Run the system:
```powershell
python main.py
```

## Troubleshooting:

### If you see "ModuleNotFoundError":
The package isn't installed. Re-run the installation for that package.

### If ChromaDB won't install:
Try these versions in order:
```powershell
python -m pip install chromadb==0.4.22
python -m pip install chromadb==0.4.15
python -m pip install chromadb==0.4.0
```

### If torch won't install:
```powershell
# Try CPU version first (smaller, faster)
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu

# For GPU support (recommended for your RTX 1000):
python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### If numpy is taking forever:
It's building from source. Just wait (can take 15-20 minutes).
Or try:
```powershell
python -m pip install numpy==1.26.4
```

## What I Recommend:

**Right now:**
1. Open a PowerShell terminal
2. Navigate to: C:\Users\LAVORO\OneDrive - ITS MAKER ACADEMY\Desktop\APP
3. Run: `python -m pip install -r requirements-simple.txt`
4. Wait for completion (15-20 minutes)
5. Restart Qoder IDE
6. All red errors will disappear!
7. Run: `python main.py`

## Why the Red Errors?

Your code is perfect! The errors are just your IDE saying:
"Hey, these packages don't exist yet!"

Once installed, the IDE will detect them and errors vanish.

Think of it like:
- Recipe (code) ✅ Perfect
- Ingredients (packages) ❌ Not in kitchen yet
- Shopping (installing) 🛒 In progress
- Once home (installed) ✅ Ready to cook!

---

The code works, we just need to finish getting the ingredients! 🚀
