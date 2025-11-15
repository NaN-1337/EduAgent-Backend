"""
Script to embed PDF documents into a local FAISS vector store.
Run this script first to process your PDF files before using the chatbot.
"""
import sys
from pathlib import Path
from pdf_loader import PDFDocumentLoader
from text_splitter import DocumentSplitter
from vector_store import VectorStoreManager
from config import Config


def main():
    """Main function to embed PDF documents."""
    
    print("="*60)
    print("  PDF Document Embedding Script")
    print("="*60)
    print(f"PDF Directory: {Config.PDF_DIRECTORY}")
    print(f"Vector Store Path: {Config.VECTOR_STORE_PATH}")
    print(f"Embedding Model: {Config.OPENAI_EMBEDDING_MODEL}")
    print(f"Chunk Size: {Config.CHUNK_SIZE}, Overlap: {Config.CHUNK_OVERLAP}")
    print("="*60 + "\n")
    
    # Check if PDF directory exists and has files
    if not Config.PDF_DIRECTORY.exists():
        print(f"❌ Error: PDF directory not found: {Config.PDF_DIRECTORY}")
        print("Creating the directory...")
        Config.PDF_DIRECTORY.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory. Please add PDF files to: {Config.PDF_DIRECTORY}")
        sys.exit(1)
    
    pdf_files = list(Config.PDF_DIRECTORY.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ Error: No PDF files found in {Config.PDF_DIRECTORY}")
        print(f"Please add PDF files to the directory and run this script again.")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    print()
    
    try:
        # Step 1: Load PDFs
        print("Step 1: Loading PDF documents...")
        print("-" * 60)
        loader = PDFDocumentLoader()
        documents = loader.load_pdfs()
        
        if not documents:
            print("❌ Error: No documents were loaded.")
            sys.exit(1)
        
        print(f"✓ Loaded {len(documents)} pages\n")
        
        # Step 2: Split documents into chunks
        print("Step 2: Splitting documents into chunks...")
        print("-" * 60)
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(documents)
        
        # Show statistics
        stats = splitter.get_chunk_stats(chunks)
        print(f"\nChunk Statistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Average length: {stats['avg_chunk_length']:.0f} characters")
        print(f"  Min/Max length: {stats['min_chunk_length']} / {stats['max_chunk_length']} characters")
        print(f"  Total characters: {stats['total_characters']:,}")
        print()
        
        # Step 3: Create embeddings and vector store
        print("Step 3: Creating embeddings and vector store...")
        print("-" * 60)
        print("⏳ This may take a few minutes depending on the number of chunks...")
        
        vs_manager = VectorStoreManager()
        vs_manager.create_vector_store(chunks)
        
        # Step 4: Save vector store
        print("\nStep 4: Saving vector store to disk...")
        print("-" * 60)
        vs_manager.save_vector_store()
        
        # Test the vector store
        print("\nStep 5: Testing vector store...")
        print("-" * 60)
        test_query = "What is this document about?"
        results = vs_manager.similarity_search(test_query, k=2)
        
        print(f"Test query: '{test_query}'")
        print(f"Found {len(results)} results")
        
        if results:
            print("\nSample result:")
            print(f"  Source: {results[0].metadata.get('source', 'Unknown')}")
            print(f"  Page: {results[0].metadata.get('page', 'Unknown')}")
            print(f"  Content preview: {results[0].page_content[:150]}...")
        
        print("\n" + "="*60)
        print("✓ SUCCESS! Vector store created successfully!")
        print("="*60)
        print("\nYou can now run 'python main.py' to start the chatbot.")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during embedding process: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
