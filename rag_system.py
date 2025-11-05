"""
Main RAG system that ties everything together
"""

from document_loader import DocumentLoader
from text_chunker import TextChunker
from vector_store import VectorStore
from local_llm import LocalLLM
import config


class RAGSystem:
    """Complete RAG pipeline"""
    
    def __init__(self):
        print("=" * 60)
        print("Initializing Local RAG System")
        print("=" * 60)
        
        self.document_loader = DocumentLoader()
        self.text_chunker = TextChunker()
        self.vector_store = VectorStore()
        self.llm = LocalLLM()
        
        print("\n" + "=" * 60)
        print("✓ RAG System Ready!")
        print("=" * 60)
    
    def index_documents(self, documents_dir: str = "./documents"):
        """
        Load and index all documents from a directory
        
        Args:
            documents_dir: Directory containing documents to index
        """
        print(f"\n{'=' * 60}")
        print("Starting Document Indexing")
        print("=" * 60)
        
        # Update document loader directory
        self.document_loader.documents_dir = documents_dir
        
        # Load documents
        documents = self.document_loader.load_all_documents()
        
        if not documents:
            print("\n⚠ No documents found to index!")
            return
        
        # Chunk documents
        chunks = self.text_chunker.chunk_documents(documents)
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        print(f"\n{'=' * 60}")
        print("✓ Indexing Complete!")
        print(f"Total chunks in database: {self.vector_store.get_collection_count()}")
        print("=" * 60)
    
    def query(self, question: str, top_k: int = config.TOP_K_RESULTS) -> dict:
        """
        Query the RAG system
        
        Args:
            question: User question
            top_k: Number of relevant chunks to retrieve
        
        Returns:
            Dictionary with answer and source information
        """
        print(f"\n{'=' * 60}")
        print(f"Query: {question}")
        print("=" * 60)
        
        # Check if database has documents
        count = self.vector_store.get_collection_count()
        if count == 0:
            return {
                'answer': "No documents have been indexed yet. Please add documents first.",
                'sources': []
            }
        
        # Retrieve relevant chunks
        print(f"\n🔍 Searching vector database ({count} chunks)...")
        relevant_chunks = self.vector_store.search(question, top_k=top_k)
        
        if not relevant_chunks:
            return {
                'answer': "No relevant information found in the indexed documents.",
                'sources': []
            }
        
        print(f"✓ Found {len(relevant_chunks)} relevant chunks")
        
        # Generate answer
        print("\n🤖 Generating answer...")
        answer = self.llm.generate_with_context(question, relevant_chunks)
        
        # Format sources
        sources = []
        for chunk in relevant_chunks:
            sources.append({
                'filename': chunk['metadata'].get('filename', 'unknown'),
                'text': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'],
                'distance': chunk.get('distance', 0.0)
            })
        
        return {
            'answer': answer,
            'sources': sources
        }
    
    def clear_index(self):
        """Clear all indexed documents"""
        self.vector_store.clear_collection()
    
    def get_stats(self):
        """Get system statistics"""
        return {
            'total_chunks': self.vector_store.get_collection_count(),
            'embedding_model': config.EMBEDDING_MODEL,
            'llm_model': config.LLM_MODEL,
            'device': config.DEVICE
        }
