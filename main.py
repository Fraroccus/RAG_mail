"""
Main entry point for the RAG system with CLI interface
"""

from rag_system import RAGSystem
import sys


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 70)
    print(" " * 20 + "LOCAL RAG SYSTEM")
    print(" " * 15 + "Powered by HuggingFace Models")
    print("=" * 70)


def print_menu():
    """Print main menu"""
    print("\n" + "-" * 70)
    print("OPTIONS:")
    print("  1. Index documents (add documents to the system)")
    print("  2. Query the system (ask questions)")
    print("  3. Show statistics")
    print("  4. Clear index")
    print("  5. Exit")
    print("-" * 70)


def index_documents_interactive(rag: RAGSystem):
    """Interactive document indexing"""
    print("\n" + "=" * 70)
    print("DOCUMENT INDEXING")
    print("=" * 70)
    print("\nPlace your documents in the './documents' folder")
    print("Supported formats: .txt, .pdf, .docx")
    
    input("\nPress ENTER to start indexing...")
    rag.index_documents()


def query_interactive(rag: RAGSystem):
    """Interactive querying"""
    print("\n" + "=" * 70)
    print("QUERY MODE")
    print("=" * 70)
    print("Type your questions below (or 'back' to return to menu)")
    print("-" * 70)
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if not question:
            continue
        
        if question.lower() in ['back', 'exit', 'quit', 'menu']:
            break
        
        # Query the system
        result = rag.query(question)
        
        # Display answer
        print("\n" + "=" * 70)
        print("📝 ANSWER:")
        print("-" * 70)
        print(result['answer'])
        
        # Display sources
        if result['sources']:
            print("\n" + "-" * 70)
            print("📚 SOURCES:")
            print("-" * 70)
            for i, source in enumerate(result['sources'], 1):
                print(f"\n{i}. From: {source['filename']}")
                print(f"   Relevance: {1 - source['distance']:.2%}")
                print(f"   Excerpt: {source['text']}")
        
        print("\n" + "=" * 70)


def show_stats(rag: RAGSystem):
    """Show system statistics"""
    stats = rag.get_stats()
    
    print("\n" + "=" * 70)
    print("SYSTEM STATISTICS")
    print("=" * 70)
    print(f"Total indexed chunks: {stats['total_chunks']}")
    print(f"Embedding model: {stats['embedding_model']}")
    print(f"LLM model: {stats['llm_model']}")
    print(f"Device: {stats['device']}")
    print("=" * 70)


def main():
    """Main application loop"""
    print_header()
    
    # Initialize RAG system
    try:
        rag = RAGSystem()
    except Exception as e:
        print(f"\n❌ Error initializing RAG system: {e}")
        print("\nPlease make sure you've installed all dependencies:")
        print("  pip install -r requirements.txt")
        return
    
    # Main loop
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            index_documents_interactive(rag)
        
        elif choice == '2':
            query_interactive(rag)
        
        elif choice == '3':
            show_stats(rag)
        
        elif choice == '4':
            confirm = input("\n⚠ Are you sure you want to clear the index? (yes/no): ")
            if confirm.lower() == 'yes':
                rag.clear_index()
                print("✓ Index cleared")
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
