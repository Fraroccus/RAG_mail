"""
Text chunking utilities for breaking documents into smaller pieces
"""

from typing import List, Optional
import config


class TextChunker:
    """Split text into overlapping chunks"""
    
    def __init__(self, chunk_size: int = config.CHUNK_SIZE, 
                 chunk_overlap: int = config.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> List[dict]:
        """
        Split text into chunks with overlap
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to each chunk
        
        Returns:
            List of dictionaries with 'text' and 'metadata' keys
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            # Create chunk with metadata
            chunk = {
                'text': chunk_text,
                'metadata': metadata or {}
            }
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            
            # Break if we've reached the end
            if end >= len(text):
                break
        
        return chunks
    
    def chunk_documents(self, documents: List[dict]) -> List[dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of documents with 'content' and optional metadata
        
        Returns:
            List of chunks with metadata
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get('content', '')
            metadata = {
                'filename': doc.get('filename', 'unknown'),
                'path': doc.get('path', '')
            }
            
            chunks = self.chunk_text(content, metadata)
            all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
