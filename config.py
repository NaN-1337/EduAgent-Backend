"""
Configuration module for the RAG system.
Loads environment variables and provides configuration settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for RAG system settings."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    
    # Paths
    VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", "./vectorstore"))
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "hackathon_collection")
    
    # Retrieval Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "8"))

    # Firebase Storage Configuration
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found. Please create a .env file with your API key. "
                "See .env.example for reference."
            )
        
        if not cls.VECTOR_STORE_PATH.exists():
            raise ValueError(
                f"Vector store not found at: {cls.VECTOR_STORE_PATH}\n"
                f"Please ensure the vectorstore directory exists."
            )
        
        return True

# Validate configuration on import
Config.validate()
