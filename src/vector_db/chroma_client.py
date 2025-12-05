"""
Chroma database client wrapper
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import Optional, List, Dict, Any
from src.config.settings import get_settings


class ChromaClient:
    """Wrapper for Chroma database client"""
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        persist_dir: Optional[str] = None,
        collection_name: Optional[str] = None
    ):
        """
        Initialize Chroma client
        
        Args:
            host: Chroma host (defaults to config)
            port: Chroma port (defaults to config)
            persist_dir: Persistence directory (defaults to config)
            collection_name: Collection name (defaults to config)
        """
        settings = get_settings()
        
        self.host = host or settings.chroma_host
        self.port = port or settings.chroma_port
        self.persist_dir = persist_dir or settings.chroma_persist_dir
        self.collection_name = collection_name or settings.chroma_collection_name
        
        # Initialize Chroma client
        if self.host == "localhost" or self.host == "127.0.0.1":
            # Local persistent client
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        else:
            # Remote client
            self.client = chromadb.HttpClient(
                host=self.host,
                port=self.port,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "IT Ops Instructions"}
        )
    
    def get_collection(self):
        """Get the collection"""
        return self.collection
    
    def reset_collection(self):
        """Reset the collection (delete all data)"""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass  # Collection might not exist
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "IT Ops Instructions"}
        )
    
    def health_check(self) -> bool:
        """Check if Chroma is accessible"""
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False

