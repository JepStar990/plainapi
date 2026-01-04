from fastapi import APIRouter, Depends
from typing import Dict
import time

from src.vector_store.chroma_manager import ChromaManager

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "PlainAPI"
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict:
    """Detailed health check with dependencies."""
    checks = {
        "api": "healthy",
        "vector_store": "unknown",
        "llm": "unknown"
    }
    
    # Check vector store
    try:
        chroma_manager = ChromaManager()
        info = chroma_manager.get_collection_info()
        if "error" not in info:
            checks["vector_store"] = "healthy"
            checks["vector_store_info"] = info
        else:
            checks["vector_store"] = "unhealthy"
    except Exception as e:
        checks["vector_store"] = f"error: {str(e)}"
    
    return {
        "status": "detailed",
        "timestamp": time.time(),
        "checks": checks
    }
