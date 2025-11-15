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
    PDF_DIRECTORY = Path(os.getenv("PDF_DIRECTORY", "./pdfs"))
    VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", "./vector_store"))
    
    # Text Splitting Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Retrieval Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found. Please create a .env file with your API key. "
                "See .env.example for reference."
            )
        
        # Create directories if they don't exist
        cls.PDF_DIRECTORY.mkdir(exist_ok=True)
        cls.VECTOR_STORE_PATH.mkdir(exist_ok=True)
        
        return True

# Validate configuration on import
Config.validate()
