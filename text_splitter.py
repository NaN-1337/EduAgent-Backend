"""
Text Splitter module for chunking documents.
"""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import Config


class DocumentSplitter:
    """Split documents into chunks for embedding."""
    
    def __init__(
        self, 
        chunk_size: int = None, 
        chunk_overlap: int = None,
        separators: List[str] = None
    ):
        """
        Initialize the text splitter.
        
        Args:
            chunk_size: Size of each text chunk. If None, uses Config.CHUNK_SIZE
            chunk_overlap: Overlap between chunks. If None, uses Config.CHUNK_OVERLAP
            separators: List of separators for splitting. If None, uses default.
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
        
        # Default separators prioritize paragraph and sentence breaks
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects to split.
            
        Returns:
            List of chunked Document objects.
        """
        if not documents:
            print("Warning: No documents to split.")
            return []
        
        print(f"Splitting {len(documents)} documents into chunks...")
        print(f"Chunk size: {self.chunk_size}, Overlap: {self.chunk_overlap}")
        
        chunks = self.text_splitter.split_documents(documents)
        
        print(f"Created {len(chunks)} chunks from {len(documents)} documents")
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
        
        return chunks
    
    def get_chunk_stats(self, chunks: List[Document]) -> dict:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of chunked documents.
            
        Returns:
            Dictionary with chunk statistics.
        """
        if not chunks:
            return {}
        
        chunk_lengths = [len(chunk.page_content) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_length": sum(chunk_lengths) / len(chunk_lengths),
            "min_chunk_length": min(chunk_lengths),
            "max_chunk_length": max(chunk_lengths),
            "total_characters": sum(chunk_lengths)
        }


if __name__ == "__main__":
    # Test the splitter
    from pdf_loader import PDFDocumentLoader
    
    # Load documents
    loader = PDFDocumentLoader()
    docs = loader.load_pdfs()
    
    if docs:
        # Split documents
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(docs)
        
        # Show statistics
        stats = splitter.get_chunk_stats(chunks)
        print("\nChunk Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Show sample chunk
        if chunks:
            print(f"\nSample chunk content (first 200 chars):")
            print(chunks[0].page_content[:200])
            print(f"\nMetadata: {chunks[0].metadata}")
