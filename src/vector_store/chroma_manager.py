import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from src.core.config import settings
from src.data_ingestion.schemas import APIDocument

logger = logging.getLogger(__name__)

class ChromaManager:
    """Manager for ChromaDB vector store operations."""
    
    def __init__(self, collection_name: str = None):
        self.collection_name = collection_name or settings.collection_name
        self.client = None
        self.collection = None
        
    def initialize(self, persist_directory: str = None):
        """Initialize ChromaDB client and collection."""
        persist_directory = persist_directory or str(settings.vector_store_path)
        
        # Create client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info(f"ChromaDB initialized at {persist_directory}")
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "NASA API Documentation"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, documents: List[APIDocument]):
        """Add documents to the vector store."""
        if not self.collection:
            self.initialize()
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        metadatas = []
        documents_text = []
        
        for doc in documents:
            ids.append(doc.id)
            
            # Store embedding if available
            if doc.embedding:
                embeddings.append(doc.embedding)
            
            # Prepare metadata
            metadata = {
                "document_type": doc.document_type,
                "source_url": doc.source_url,
                "api_endpoint": doc.api_endpoint or "",
                "created_at": doc.created_at.isoformat(),
                **doc.metadata
            }
            metadatas.append(metadata)
            
            # Store document text
            documents_text.append(doc.content)
        
        # Add to collection
        if embeddings:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
        else:
            self.collection.add(
                ids=ids,
                metadatas=metadatas,
                documents=documents_text
            )
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5, 
               filter_conditions: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search the vector store."""
        if not self.collection:
            self.initialize()
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_conditions,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else None,
                        "id": results['ids'][0][i] if results['ids'] else None
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        if not self.collection:
            self.initialize()
        
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "document_count": count,
                "path": str(settings.vector_store_path)
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}
    
    def delete_collection(self):
        """Delete the collection."""
        if self.client:
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted collection: {self.collection_name}")
            except Exception as e:
                logger.error(f"Error deleting collection: {e}")
    
    def reset(self):
        """Reset the vector store."""
        self.delete_collection()
        self.initialize()
