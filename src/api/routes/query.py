from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str
    conversation_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Show me recent photos from Mars",
                "conversation_id": "session_123",
                "preferences": {
                    "detail_level": "summary"
                }
            }
        }

class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str
    data_source: str
    confidence: float
    processing_time: float
    raw_response: Optional[Dict[str, Any]] = None

@router.post("/query")
async def process_query(request: QueryRequest) -> QueryResponse:
    """Process a natural language query about NASA APIs."""
    # This is a placeholder for Phase 1
    # In Phase 2, this will integrate with the full system
    
    logger.info(f"Received query: {request.query}")
    
    # For Phase 1, just return a simple response
    return QueryResponse(
        answer="I understand you want information about NASA APIs. In Phase 1, I've loaded NASA API documentation into a vector store. In Phase 2, I'll be able to answer your specific queries!",
        data_source="NASA API Documentation",
        confidence=0.8,
        processing_time=0.1
    )

@router.get("/query/test")
async def test_query():
    """Test query endpoint with sample queries."""
    test_queries = [
        "How do I get the astronomy picture of the day?",
        "Show me Mars rover photos from last week",
        "What NASA APIs are available?",
        "How to search for space images?"
    ]
    
    return {
        "test_queries": test_queries,
        "message": "Use POST /api/query with one of these queries"
    }
