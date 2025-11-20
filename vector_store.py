"""
Vector store using FAISS for semantic search
(ChromaDB replacement for Python 3.14.0 compatibility)
"""

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import config
import os
import pickle

# Global model cache to avoid reloading
_embedding_model_cache = None

def get_embedding_model():
    """Get or create the embedding model (singleton pattern)"""
    global _embedding_model_cache
    if _embedding_model_cache is None:
        print(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        _embedding_model_cache = SentenceTransformer(config.EMBEDDING_MODEL)
        _embedding_model_cache.to(config.DEVICE)
        print("✓ Embedding model loaded")
    return _embedding_model_cache


class VectorStore:
    """Manages vector embeddings and similarity search using FAISS"""
    
    def __init__(self, collection_name: Optional[str] = None):
        print("Initializing Vector Store...")
        
        # Set collection name
        self.collection_name = collection_name or config.COLLECTION_NAME
        
        # Defer model loading until first use
        self._embedding_model = None
        
        # Get embedding dimension (requires model)
        model = get_embedding_model()
        self.dimension = model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)
        self.index_path = os.path.join(config.CHROMA_DB_DIR, f"{self.collection_name}.index")
        self.metadata_path = os.path.join(config.CHROMA_DB_DIR, f"{self.collection_name}.pkl")
        
        # Load or create index
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data['documents']
                    self.metadatas = data['metadatas']
                print(f"Loaded existing index '{self.collection_name}' with {len(self.documents)} documents")
            except Exception as e:
                print(f"⚠️ Warning: Could not load index '{self.collection_name}': {e}")
                print(f"🔧 Creating new index instead...")
                # If loading fails, create new index
                self.index = faiss.IndexFlatL2(self.dimension)
                self.documents = []
                self.metadatas = []
                # Remove corrupted files
                try:
                    if os.path.exists(self.index_path):
                        os.remove(self.index_path)
                    if os.path.exists(self.metadata_path):
                        os.remove(self.metadata_path)
                except:
                    pass
                print(f"Created new FAISS index '{self.collection_name}'")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.metadatas = []
            print(f"Created new FAISS index '{self.collection_name}'")
    
    @property
    def embedding_model(self):
        """Lazy load embedding model on first access"""
        return get_embedding_model()
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.embedding_model.encode(
            texts, 
            convert_to_tensor=False,
            show_progress_bar=True
        )
        # Convert numpy array to list of lists
        if isinstance(embeddings, np.ndarray):
            return embeddings.tolist()
        return embeddings
    
    def add_documents(self, chunks: List[dict]):
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of dicts with 'text' and 'metadata' keys
        """
        if not chunks:
            print("No chunks to add")
            return
        
        print(f"\nAdding {len(chunks)} chunks to vector store...")
        
        # Extract texts and metadata
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embed_texts(texts)
        
        # Convert to numpy array for FAISS
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings_array)  # type: ignore
        
        # Store documents and metadata
        self.documents.extend(texts)
        self.metadatas.extend(metadatas)
        
        # Save to disk
        self._save_index()
        
        print(f"✓ Successfully added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, top_k: int = config.TOP_K_RESULTS) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of relevant document chunks with metadata
        """
        if len(self.documents) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        query_vector = np.array([query_embedding]).astype('float32')
        
        # Search FAISS index
        top_k = min(top_k, len(self.documents))  # Don't request more than we have
        distances, indices = self.index.search(query_vector, top_k)  # type: ignore
        
        # Format results
        formatted_results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):  # Ensure valid index
                formatted_results.append({
                    'text': self.documents[idx],
                    'metadata': self.metadatas[idx] if idx < len(self.metadatas) else {},
                    'distance': float(distances[0][i])
                })
        
        return formatted_results
    
    def clear_collection(self):
        """Delete all documents from the collection"""
        try:
            # Reset FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.metadatas = []
            
            # Delete saved files
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            print("✓ Collection cleared")
        except Exception as e:
            print(f"Error clearing collection: {e}")
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection"""
        return len(self.documents)
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadatas': self.metadatas
                }, f)
            print(f"✓ Index saved to {self.index_path}")
        except Exception as e:
            print(f"❌ Error saving index to {self.index_path}: {e}")
            # Don't raise - allow operation to continue even if save fails
