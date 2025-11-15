"""
Vector Store module for managing FAISS vector database with OpenAI embeddings.
"""
from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from config import Config


class VectorStoreManager:
    """Manage FAISS vector store with OpenAI embeddings."""
    
    def __init__(
        self, 
        embedding_model: str = None,
        vector_store_path: Path = None
    ):
        """
        Initialize the vector store manager.
        
        Args:
            embedding_model: OpenAI embedding model name. If None, uses Config.OPENAI_EMBEDDING_MODEL
            vector_store_path: Path to save/load vector store. If None, uses Config.VECTOR_STORE_PATH
        """
        self.embedding_model = embedding_model or Config.OPENAI_EMBEDDING_MODEL
        self.vector_store_path = vector_store_path or Config.VECTOR_STORE_PATH
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_API_BASE
        )
        
        self.vector_store: Optional[FAISS] = None
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """
        Create a new vector store from documents.
        
        Args:
            documents: List of Document objects to embed.
            
        Returns:
            FAISS vector store instance.
        """
        if not documents:
            raise ValueError("No documents provided to create vector store.")
        
        print(f"Creating vector store with {len(documents)} documents...")
        print(f"Using embedding model: {self.embedding_model}")
        
        # Create FAISS vector store
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        print(f"✓ Vector store created successfully")
        return self.vector_store
    
    def save_vector_store(self, store_name: str = "faiss_index"):
        """
        Save the vector store to disk.
        
        Args:
            store_name: Name for the vector store files.
        """
        if self.vector_store is None:
            raise ValueError("No vector store to save. Create one first.")
        
        save_path = self.vector_store_path / store_name
        self.vector_store.save_local(str(save_path))
        print(f"✓ Vector store saved to: {save_path}")
    
    def load_vector_store(self, store_name: str = "faiss_index") -> FAISS:
        """
        Load an existing vector store from disk.
        
        Args:
            store_name: Name of the vector store to load.
            
        Returns:
            FAISS vector store instance.
        """
        load_path = self.vector_store_path / store_name
        
        if not load_path.exists():
            raise FileNotFoundError(
                f"Vector store not found at: {load_path}\n"
                f"Please create one first using embed_pdfs.py"
            )
        
        print(f"Loading vector store from: {load_path}")
        
        self.vector_store = FAISS.load_local(
            str(load_path),
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        print(f"✓ Vector store loaded successfully")
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        """
        Add new documents to an existing vector store.
        
        Args:
            documents: List of Document objects to add.
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Load or create one first.")
        
        print(f"Adding {len(documents)} documents to vector store...")
        self.vector_store.add_documents(documents)
        print(f"✓ Documents added successfully")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query.
            k: Number of results to return. If None, uses Config.TOP_K_RESULTS
            
        Returns:
            List of most similar documents.
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Load or create one first.")
        
        k = k or Config.TOP_K_RESULTS
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def get_retriever(self, k: int = None):
        """
        Get a retriever for the vector store.
        
        Args:
            k: Number of documents to retrieve. If None, uses Config.TOP_K_RESULTS
            
        Returns:
            VectorStoreRetriever instance.
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Load or create one first.")
        
        k = k or Config.TOP_K_RESULTS
        return self.vector_store.as_retriever(search_kwargs={"k": k})


if __name__ == "__main__":
    # Test the vector store
    from pdf_loader import PDFDocumentLoader
    from text_splitter import DocumentSplitter
    
    print("Testing Vector Store Manager...\n")
    
    # Load and split documents
    loader = PDFDocumentLoader()
    docs = loader.load_pdfs()
    
    if docs:
        splitter = DocumentSplitter()
        chunks = splitter.split_documents(docs)
        
        # Create vector store
        vs_manager = VectorStoreManager()
        vs_manager.create_vector_store(chunks)
        
        # Test similarity search
        query = "What is this document about?"
        results = vs_manager.similarity_search(query, k=2)
        
        print(f"\nSearch results for: '{query}'")
        for i, doc in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Content: {doc.page_content[:150]}...")
            print(f"  Source: {doc.metadata.get('source', 'Unknown')}")
