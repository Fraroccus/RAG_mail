"""
Document loader for various file formats
"""

import os
from typing import List
from pathlib import Path


class DocumentLoader:
    """Load documents from various file formats"""
    
    def __init__(self, documents_dir: str = "./documents"):
        self.documents_dir = documents_dir
        os.makedirs(documents_dir, exist_ok=True)
    
    def load_txt(self, file_path: str) -> str:
        """Load a text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_pdf(self, file_path: str) -> str:
        """Load a PDF file"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            print("pypdf not installed. Install with: pip install pypdf")
            return ""
    
    def load_docx(self, file_path: str) -> str:
        """Load a Word document"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            print("python-docx not installed. Install with: pip install python-docx")
            return ""
    
    def load_document(self, file_path: str) -> str:
        """Load a document based on its extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.txt':
            return self.load_txt(file_path)
        elif ext == '.pdf':
            return self.load_pdf(file_path)
        elif ext == '.docx':
            return self.load_docx(file_path)
        else:
            print(f"Unsupported file format: {ext}")
            return ""
    
    def load_all_documents(self) -> List[dict]:
        """Load all documents from the documents directory"""
        documents = []
        
        if not os.path.exists(self.documents_dir):
            print(f"Documents directory not found: {self.documents_dir}")
            return documents
        
        for filename in os.listdir(self.documents_dir):
            file_path = os.path.join(self.documents_dir, filename)
            
            if os.path.isfile(file_path):
                print(f"Loading: {filename}")
                content = self.load_document(file_path)
                
                if content:
                    documents.append({
                        'filename': filename,
                        'content': content,
                        'path': file_path
                    })
        
        print(f"\nLoaded {len(documents)} documents")
        return documents
