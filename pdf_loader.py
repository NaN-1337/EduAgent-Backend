"""
PDF Loader module for loading PDF documents from local directory.
"""
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from config import Config


class PDFDocumentLoader:
    """Load PDF documents from the configured directory."""
    
    def __init__(self, pdf_directory: Path = None):
        """
        Initialize the PDF loader.
        
        Args:
            pdf_directory: Path to directory containing PDFs. 
                         If None, uses Config.PDF_DIRECTORY
        """
        self.pdf_directory = pdf_directory or Config.PDF_DIRECTORY
        
    def load_pdfs(self) -> List[Document]:
        """
        Load all PDF files from the directory.
        
        Returns:
            List of Document objects containing the PDF content.
        """
        documents = []
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            print(f"Warning: No PDF files found in {self.pdf_directory}")
            return documents
        
        print(f"Found {len(pdf_files)} PDF files to load...")
        
        for pdf_file in pdf_files:
            try:
                print(f"Loading: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                pdf_documents = loader.load()
                
                # Add source metadata
                for doc in pdf_documents:
                    doc.metadata["source"] = pdf_file.name
                
                documents.extend(pdf_documents)
                print(f"  ✓ Loaded {len(pdf_documents)} pages from {pdf_file.name}")
                
            except Exception as e:
                print(f"  ✗ Error loading {pdf_file.name}: {e}")
                continue
        
        print(f"\nTotal pages loaded: {len(documents)}")
        return documents
    
    def load_single_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load a single PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            List of Document objects.
        """
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Add source metadata
            pdf_name = Path(pdf_path).name
            for doc in documents:
                doc.metadata["source"] = pdf_name
            
            print(f"Loaded {len(documents)} pages from {pdf_name}")
            return documents
            
        except Exception as e:
            print(f"Error loading {pdf_path}: {e}")
            return []


if __name__ == "__main__":
    # Test the loader
    loader = PDFDocumentLoader()
    docs = loader.load_pdfs()
    
    if docs:
        print(f"\nSample document content (first 200 chars):")
        print(docs[0].page_content[:200])
        print(f"\nMetadata: {docs[0].metadata}")
