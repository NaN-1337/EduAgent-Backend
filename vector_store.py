"""
Vector Store module for managing ChromaDB vector database with OpenAI embeddings.
"""
from pathlib import Path
from typing import List, Optional, Dict
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from config import Config


class VectorStoreManager:
    """Manage ChromaDB vector store with OpenAI embeddings."""
    
    def __init__(
        self, 
        embedding_model: str = None,
        vector_store_path: Path = None,
        collection_name: str = None
    ):
        """
        Initialize the vector store manager.
        
        Args:
            embedding_model: OpenAI embedding model name. If None, uses Config.OPENAI_EMBEDDING_MODEL
            vector_store_path: Path to the vector store. If None, uses Config.VECTOR_STORE_PATH
            collection_name: Name of the Chroma collection. If None, uses Config.CHROMA_COLLECTION_NAME
        """
        self.embedding_model = embedding_model or Config.OPENAI_EMBEDDING_MODEL
        self.vector_store_path = vector_store_path or Config.VECTOR_STORE_PATH
        self.collection_name = collection_name or Config.CHROMA_COLLECTION_NAME
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_API_BASE
        )
        
        self.vector_store: Optional[Chroma] = None
    
    def load_vector_store(self) -> Chroma:
        """
        Load an existing vector store from disk.
        
        Returns:
            Chroma vector store instance.
        """
        if not self.vector_store_path.exists():
            raise FileNotFoundError(
                f"Vector store not found at: {self.vector_store_path}\n"
                f"Please ensure the vector store exists at the configured path."
            )
        
        print(f"Loading vector store from: {self.vector_store_path}")
        
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.vector_store_path)
        )
        
        print(f"✓ Vector store loaded successfully")
        return self.vector_store
    
    def similarity_search(
        self, 
        query: str, 
        k: int = None,
        filter: Optional[Dict] = None
    ) -> List[Document]:
        """
        Search for similar documents with optional metadata filtering.
        
        Args:
            query: Search query.
            k: Number of results to return. If None, uses Config.TOP_K_RESULTS
            filter: Optional metadata filter dictionary (e.g., {"subject": "biologie", "grade": 5})
            
        Returns:
            List of most similar documents.
        """
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Load one first.")
        
        k = k or Config.TOP_K_RESULTS
        
        # Use filter if provided
        if filter:
            results = self.vector_store.similarity_search(query, k=k, filter=filter)
        else:
            results = self.vector_store.similarity_search(query, k=k)
        
        return results
