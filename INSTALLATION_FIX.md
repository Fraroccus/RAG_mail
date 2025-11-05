# Installation Fix for Python 3.14.0

## ⚠️ Issue: `pip` command not recognized

If you see this error:
```
pip : Termine 'pip' non riconosciuto come nome di cmdlet...
```

This means `pip` is not in your PATH, but Python is installed correctly.

---

## ✅ Solution: Use `python -m pip` instead

### For ALL pip commands, use this format:

**Instead of:**
```powershell
pip install something
```

**Use:**
```powershell
python -m pip install something
```

---

## 📦 Installing the RAG System

### Step 1: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### Step 2: Install dependencies
```powershell
python -m pip install -r requirements.txt
```

**This will take 5-15 minutes** because it needs to:
- Download PyTorch (~2GB)
- Download all AI libraries
- Compile some packages (like numpy)

---

## 🐌 If Installation is Very Slow

Python 3.14.0 is very new and some packages might not have pre-built wheels yet.

### Option A: Wait it out (Recommended)
- Let it finish (15-20 minutes)
- It's building from source
- This only happens once

### Option B: Use Python 3.12 or 3.11
If you have issues with 3.14.0:

1. Download Python 3.12.x from python.org
2. Install it
3. Use it instead:
```powershell
python3.12 -m pip install -r requirements.txt
python3.12 main.py
```

---

## 📋 Installation Progress Indicators

You'll see these phases:

1. **Collecting packages** ✓
   ```
   Collecting torch>=2.0.0
   Collecting transformers>=4.30.0
   ...
   ```

2. **Downloading** (5-10 min)
   ```
   Downloading torch-2.9.0...
   ```

3. **Building wheels** (5-10 min)
   ```
   Building wheel for numpy...
   Building wheel for chroma-hnswlib...
   ```

4. **Installing** (2-3 min)
   ```
   Installing collected packages...
   ```

5. **Success!**
   ```
   Successfully installed torch-2.9.0 transformers-4.57.1 ...
   ```

---

## ⏱️ Current Installation Status

Based on your terminal output, it's currently:
- ✓ Resolved dependencies
- ✓ Downloaded most packages
- 🔄 **Currently: Building numpy from source** (this can take 10-15 minutes)

**What to do:** Just wait, it will complete!

---

## 🔧 Alternative: Minimal Installation

If you want to test faster, create a minimal version first:

### Create `requirements-minimal.txt`:
```txt
torch
transformers
sentence-transformers
chromadb==0.4.22
pypdf
python-docx
```

Then install:
```powershell
python -m pip install -r requirements-minimal.txt
```

This installs fewer dependencies and should be faster.

---

## ✅ After Installation Completes

Run the system:
```powershell
python main.py
```

If `python` doesn't work, try:
```powershell
py main.py
```

---

## 🆘 Still Having Issues?

### Check Python is working:
```powershell
python --version
```
Should show: `Python 3.14.0`

### Check pip is working:
```powershell
python -m pip --version
```
Should show pip version

### If ALL else fails - Manual installation:
```powershell
python -m pip install torch
python -m pip install transformers
python -m pip install sentence-transformers
python -m pip install chromadb
python -m pip install pypdf
python -m pip install python-docx
python -m pip install beautifulsoup4
python -m pip install langchain
python -m pip install langchain-community
```

Install packages one by one to see which one causes issues.

---

## 💡 Why This Happens

Python 3.14.0 is VERY new (just released). Some issues:
- Not all packages have pre-built "wheels" yet
- Pip needs to compile from source
- Takes longer but will work

**Recommendation:** 
- If you're patient: Wait for current installation
- If you need it working NOW: Use Python 3.12

---

## ⏳ Estimated Time

With Python 3.14.0 on Windows:
- Fast internet: 15-20 minutes total
- Slow internet: 20-30 minutes total

Most time is spent:
- Downloading PyTorch (~2GB)
- Building numpy from source (~10 min)
- Building chroma-hnswlib (~5 min)

**Be patient - it WILL finish!** ☕
