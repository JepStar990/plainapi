import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def generate_id(text: str) -> str:
    """Generate a deterministic ID from text."""
    return hashlib.md5(text.encode()).hexdigest()[:16]

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp for display."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    return timestamp.isoformat() + "Z"

def safe_json_loads(text: str) -> Any:
    """Safely parse JSON, returning None on error."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # If this isn't the first chunk, extend backwards to find a good break point
        if start > 0:
            # Look for sentence end or paragraph break
            for i in range(start, max(start - overlap, 0), -1):
                if i < len(text) and text[i] in '.!?\n':
                    start = i + 1
                    break
        
        # If this isn't the last chunk, extend forward to find a good break point
        if end < text_length:
            for i in range(end, min(end + overlap, text_length)):
                if text[i] in '.!?\n':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap  # Move start with overlap
    
    return chunks

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    
    # Remove common noise
    noise_patterns = [
        '\t', '\r', '\xa0', '\u200b', '\u200e', '\u200f'
    ]
    
    cleaned = ' '.join(lines)
    for pattern in noise_patterns:
        cleaned = cleaned.replace(pattern, ' ')
    
    # Normalize spaces
    cleaned = ' '.join(cleaned.split())
    
    return cleaned

def get_file_extension(url: str) -> str:
    """Extract file extension from URL."""
    from urllib.parse import urlparse
    path = urlparse(url).path
    return Path(path).suffix.lower()

def measure_time(func):
    """Decorator to measure execution time."""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.debug(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    
    return wrapper
