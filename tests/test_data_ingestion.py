import pytest
from pathlib import Path
import json

from src.data_ingestion.schemas import RawDocument, APIDocument, DocumentType
from src.data_ingestion.document_processor import DocumentProcessor
from src.core.config import settings

class TestDocumentProcessor:
    def test_chunk_text(self):
        """Test text chunking functionality."""
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        
        # Create a test text
        text = "This is a test sentence. " * 10  # About 200 characters
        
        chunks = processor._create_chunks(
            text,
            url="http://test.com",
            doc_type=DocumentType.OVERVIEW,
            metadata={}
        )
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, APIDocument) for chunk in chunks)
        assert all(chunk.content for chunk in chunks)
    
    def test_classify_document(self):
        """Test document classification."""
        processor = DocumentProcessor()
        
        # Test example document
        example_doc = RawDocument(
            url="http://example.com",
            content="This is an example response from the API",
            content_type="text"
        )
        
        doc_type = processor._classify_document(example_doc)
        assert doc_type == DocumentType.EXAMPLE
    
    def test_extract_metadata(self):
        """Test metadata extraction."""
        processor = DocumentProcessor()
        
        doc = RawDocument(
            url="https://api.nasa.gov/#apod",
            content="The Astronomy Picture of the Day API",
            content_type="html"
        )
        
        metadata = processor._extract_metadata(doc, DocumentType.API_ENDPOINT)
        
        assert "api_endpoint" in metadata
        assert metadata["api_endpoint"] == "apod"
        assert metadata["document_type"] == "api_endpoint"

class TestSchemas:
    def test_raw_document(self):
        """Test RawDocument schema."""
        doc = RawDocument(
            url="http://test.com",
            content="Test content",
            content_type="html"
        )
        
        assert doc.url == "http://test.com"
        assert doc.content == "Test content"
        assert doc.content_type == "html"
    
    def test_api_document(self):
        """Test APIDocument schema."""
        doc = APIDocument(
            id="test123",
            content="Test content",
            document_type=DocumentType.API_ENDPOINT,
            source_url="http://test.com"
        )
        
        assert doc.id == "test123"
        assert doc.content == "Test content"
        assert doc.document_type == DocumentType.API_ENDPOINT
        assert doc.source_url == "http://test.com"
