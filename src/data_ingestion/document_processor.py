import json
from pathlib import Path
from typing import List, Dict, Any
import logging
from datetime import datetime

from .schemas import RawDocument, APIDocument, DocumentType, ProcessedDocument
from src.core.config import settings
from src.core.utils import chunk_text, generate_id, clean_text

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process raw documents into chunks for vector store."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
    def process_raw_documents(self, raw_docs: List[RawDocument]) -> List[ProcessedDocument]:
        """Process multiple raw documents."""
        processed_docs = []
        
        for raw_doc in raw_docs:
            try:
                processed = self._process_single_document(raw_doc)
                processed_docs.append(processed)
            except Exception as e:
                logger.error(f"Error processing document from {raw_doc.url}: {e}")
                # Create a failed result
                failed = ProcessedDocument(
                    original_url=raw_doc.url,
                    chunks=[],
                    total_chunks=0,
                    processing_time=0,
                    errors=[str(e)]
                )
                processed_docs.append(failed)
        
        return processed_docs
    
    def _process_single_document(self, raw_doc: RawDocument) -> ProcessedDocument:
        """Process a single raw document."""
        import time
        start_time = time.time()
        
        # Determine document type
        doc_type = self._classify_document(raw_doc)
        
        # Extract metadata
        metadata = self._extract_metadata(raw_doc, doc_type)
        
        # Chunk the content
        chunks = self._create_chunks(raw_doc.content, raw_doc.url, doc_type, metadata)
        
        processing_time = time.time() - start_time
        
        return ProcessedDocument(
            original_url=raw_doc.url,
            chunks=chunks,
            total_chunks=len(chunks),
            processing_time=processing_time,
            errors=[]
        )
    
    def _classify_document(self, raw_doc: RawDocument) -> DocumentType:
        """Classify the type of document."""
        url = raw_doc.url.lower()
        content = raw_doc.content.lower()
        
        if 'example' in content or 'example' in url:
            return DocumentType.EXAMPLE
        elif 'parameter' in content or 'param' in url:
            return DocumentType.PARAMETER
        elif 'response' in content or 'schema' in content:
            return DocumentType.RESPONSE_SCHEMA
        elif 'error' in content or 'status' in content:
            return DocumentType.ERROR_CODE
        elif 'tutorial' in content or 'guide' in content:
            return DocumentType.TUTORIAL
        elif '/#' in url or 'endpoint' in content:
            return DocumentType.API_ENDPOINT
        else:
            return DocumentType.OVERVIEW
    
    def _extract_metadata(self, raw_doc: RawDocument, doc_type: DocumentType) -> Dict[str, Any]:
        """Extract metadata from document."""
        metadata = {
            "source_type": raw_doc.content_type,
            "document_type": doc_type.value,
            "scraped_at": raw_doc.timestamp.isoformat(),
            "url": raw_doc.url
        }
        
        # Try to extract API endpoint from URL
        if 'api.nasa.gov' in raw_doc.url:
            parts = raw_doc.url.split('/')
            for i, part in enumerate(parts):
                if part == '#':
                    if i + 1 < len(parts):
                        metadata["api_endpoint"] = parts[i + 1]
                    break
        
        # Extract possible parameters from content
        if doc_type == DocumentType.PARAMETER:
            metadata["extracted_parameters"] = self._extract_parameters(raw_doc.content)
        
        return metadata
    
    def _extract_parameters(self, content: str) -> List[str]:
        """Extract parameter names from content."""
        import re
        
        parameters = []
        
        # Look for parameter patterns
        patterns = [
            r'parameter[\s:]+["\']?(\w+)["\']?',
            r'[\s{]+(\w+)[\s}]+\(string\)',
            r'query.*parameter.*[:=]\s*["\'](\w+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            parameters.extend(matches)
        
        return list(set(parameters))
    
    def _create_chunks(self, content: str, url: str, doc_type: DocumentType, 
                      metadata: Dict) -> List[APIDocument]:
        """Create chunks from content."""
        chunks = []
        text_chunks = chunk_text(content, self.chunk_size, self.chunk_overlap)
        
        for i, chunk_content in enumerate(text_chunks):
            # Skip very short chunks
            if len(chunk_content.strip()) < 50:
                continue
            
            # Create document for this chunk
            doc = APIDocument(
                id=generate_id(f"{url}_{i}"),
                content=chunk_content,
                document_type=doc_type,
                source_url=url,
                api_endpoint=metadata.get("api_endpoint"),
                metadata={
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "chunk_size": len(chunk_content)
                }
            )
            chunks.append(doc)
        
        return chunks
    
    def save_processed_documents(self, processed_docs: List[ProcessedDocument]) -> List[Path]:
        """Save processed documents to disk."""
        saved_paths = []
        
        for i, proc_doc in enumerate(processed_docs):
            filename = f"processed_{i:03d}_{generate_id(proc_doc.original_url)}.json"
            filepath = settings.processed_docs_path / filename
            
            # Convert to dict and save
            data = proc_doc.dict()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            saved_paths.append(filepath)
        
        logger.info(f"Saved {len(saved_paths)} processed documents to disk")
        return saved_paths
    
    def load_processed_documents(self) -> List[ProcessedDocument]:
        """Load processed documents from disk."""
        processed_docs = []
        
        for filepath in settings.processed_docs_path.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert chunks back to APIDocument objects
                if "chunks" in data:
                    data["chunks"] = [APIDocument(**chunk) for chunk in data["chunks"]]
                
                processed_docs.append(ProcessedDocument(**data))
            except Exception as e:
                logger.error(f"Error loading {filepath}: {e}")
        
        return processed_docs
