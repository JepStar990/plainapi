from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class DocumentType(str, Enum):
    """Types of documents we can process."""
    API_ENDPOINT = "api_endpoint"
    PARAMETER = "parameter"
    EXAMPLE = "example"
    RESPONSE_SCHEMA = "response_schema"
    ERROR_CODE = "error_code"
    OVERVIEW = "overview"
    TUTORIAL = "tutorial"

class APIDocument(BaseModel):
    """Schema for API documentation chunks."""
    id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="The actual text content")
    document_type: DocumentType = Field(..., description="Type of document")
    source_url: str = Field(..., description="URL where this was sourced from")
    api_endpoint: Optional[str] = Field(None, description="API endpoint this relates to")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (parameters, examples, etc.)"
    )
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('id', pre=True, always=True)
    def generate_id_if_missing(cls, v, values):
        """Generate ID from content if not provided."""
        if v is None:
            import hashlib
            content = values.get('content', '')
            source = values.get('source_url', '')
            combined = f"{content[:100]}{source}"
            return hashlib.md5(combined.encode()).hexdigest()[:16]
        return v
    
    class Config:
        use_enum_values = True

class RawDocument(BaseModel):
    """Schema for raw scraped documents before processing."""
    url: str
    content: str
    content_type: str  # html, json, text, etc.
    headers: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class ProcessedDocument(BaseModel):
    """Schema for processed documents after chunking."""
    original_url: str
    chunks: List[APIDocument]
    total_chunks: int
    processing_time: float
    errors: List[str] = Field(default_factory=list)

class ScrapingResult(BaseModel):
    """Result of a scraping operation."""
    successful: bool
    documents: List[RawDocument] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    total_urls: int
    processed_urls: int
    start_time: datetime
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Get scraping duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
