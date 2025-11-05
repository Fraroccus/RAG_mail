@echo off
echo ============================================================
echo Local RAG System - Installation Script
echo ============================================================
echo.

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)
echo.

echo Step 2: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 3: Installing dependencies...
echo This will take 5-10 minutes depending on your internet speed.
echo.
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Installation failed!
    echo Please check the error messages above
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Run: python main.py
echo    (Note: If 'python' doesn't work, try 'py main.py')
echo 2. Choose option 1 to index the sample documents
echo 3. Choose option 2 to start asking questions!
echo.
echo See SETUP_GUIDE.md for detailed instructions.
echo.
pause
