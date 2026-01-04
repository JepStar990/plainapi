#!/usr/bin/env python3
"""Script to scrape NASA API documentation."""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingestion.nasa_scraper import NASADocumentationScraper
from src.data_ingestion.document_processor import DocumentProcessor
from src.vector_store.chroma_manager import ChromaManager
from src.vector_store.embedding_service import EmbeddingService
from src.core.config import create_directories
from src.core.utils import measure_time

@measure_time
async def main():
    """Main scraping function."""
    print("=" * 60)
    print("NASA API Documentation Scraper")
    print("=" * 60)
    
    # Create directories
    create_directories()
    
    # Step 1: Scrape documentation
    print("\n1. Scraping NASA API documentation...")
    scraper = NASADocumentationScraper(max_concurrent=3)
    result = await scraper.scrape_all()
    
    if not result.successful:
        print(f"Warning: Some errors occurred: {result.errors}")
    
    print(f"Scraped {result.processed_urls}/{result.total_urls} URLs in {result.duration:.2f}s")
    
    # Save raw documents
    if result.documents:
        saved_paths = scraper.save_raw_documents(result.documents)
        print(f"Saved {len(saved_paths)} raw documents to disk")
    
    # Step 2: Process documents
    print("\n2. Processing documents...")
    processor = DocumentProcessor()
    processed_docs = processor.process_raw_documents(result.documents)
    
    # Count total chunks
    total_chunks = sum(len(doc.chunks) for doc in processed_docs)
    print(f"Created {total_chunks} chunks from {len(processed_docs)} documents")
    
    # Save processed documents
    saved_processed = processor.save_processed_documents(processed_docs)
    print(f"Saved {len(saved_processed)} processed documents")
    
    # Step 3: Generate embeddings
    print("\n3. Generating embeddings...")
    embedding_service = EmbeddingService()
    embedding_service.load_model()
    
    # Collect all chunks
    all_chunks = []
    for proc_doc in processed_docs:
        all_chunks.extend(proc_doc.chunks)
    
    # Generate embeddings in batches
    print(f"Generating embeddings for {len(all_chunks)} chunks...")
    batch_size = 32
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        texts = [chunk.content for chunk in batch]
        embeddings = embedding_service.embed_batch(texts)
        
        # Assign embeddings to chunks
        for chunk, embedding in zip(batch, embeddings):
            chunk.embedding = embedding
        
        progress = min(i + batch_size, len(all_chunks))
        print(f"  Processed {progress}/{len(all_chunks)} chunks...", end='\r')
    
    print(f"\nGenerated embeddings for all {len(all_chunks)} chunks")
    
    # Step 4: Store in vector database
    print("\n4. Storing in vector database...")
    chroma_manager = ChromaManager()
    chroma_manager.initialize()
    
    # Add documents to ChromaDB
    chroma_manager.add_documents(all_chunks)
    
    # Get collection info
    info = chroma_manager.get_collection_info()
    print(f"Vector store contains {info.get('document_count', 0)} documents")
    
    # Step 5: Test retrieval
    print("\n5. Testing retrieval...")
    test_queries = [
        "How do I get Mars rover photos?",
        "What parameters does the APOD API accept?",
        "How to use NASA image search?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = chroma_manager.search(query, n_results=2)
        for j, result in enumerate(results):
            doc_type = result['metadata'].get('document_type', 'unknown')
            print(f"  Result {j+1}: [{doc_type}] {result['document'][:100]}...")
    
    print("\n" + "=" * 60)
    print("Scraping and processing complete!")
    print(f"Total documents: {len(all_chunks)}")
    print(f"Vector store location: {info.get('path', 'unknown')}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
