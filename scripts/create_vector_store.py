#!/usr/bin/env python3
"""Script to create and populate the vector store."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store.chroma_manager import ChromaManager
from src.data_ingestion.document_processor import DocumentProcessor
from src.core.config import create_directories

def main():
    """Create vector store from processed documents."""
    print("Creating vector store from processed documents...")
    
    # Create directories
    create_directories()
    
    # Load processed documents
    processor = DocumentProcessor()
    processed_docs = processor.load_processed_documents()
    
    if not processed_docs:
        print("No processed documents found. Run scrape_nasa_docs.py first.")
        return
    
    # Collect all chunks
    all_chunks = []
    for proc_doc in processed_docs:
        all_chunks.extend(proc_doc.chunks)
    
    print(f"Loaded {len(all_chunks)} chunks from {len(processed_docs)} documents")
    
    # Initialize vector store
    chroma_manager = ChromaManager()
    chroma_manager.initialize()
    
    # Add to vector store
    print("Adding documents to vector store...")
    chroma_manager.add_documents(all_chunks)
    
    # Verify
    info = chroma_manager.get_collection_info()
    print(f"Vector store created successfully!")
    print(f"  Collection: {info.get('name')}")
    print(f"  Documents: {info.get('document_count')}")
    print(f"  Location: {info.get('path')}")

if __name__ == "__main__":
    main()
