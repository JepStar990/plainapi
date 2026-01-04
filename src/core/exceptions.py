class PlainAPIException(Exception):
    """Base exception for PlainAPI."""
    
    def __init__(self, error: str, message: str, status_code: int = 500, detail: dict = None):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)

class VectorStoreException(PlainAPIException):
    """Exception for vector store operations."""
    
    def __init__(self, message: str, detail: dict = None):
        super().__init__(
            error="VECTOR_STORE_ERROR",
            message=message,
            status_code=500,
            detail=detail
        )

class LLMException(PlainAPIException):
    """Exception for LLM operations."""
    
    def __init__(self, message: str, detail: dict = None):
        super().__init__(
            error="LLM_ERROR",
            message=message,
            status_code=500,
            detail=detail
        )

class APIException(PlainAPIException):
    """Exception for external API operations."""
    
    def __init__(self, message: str, status_code: int = 502, detail: dict = None):
        super().__init__(
            error="EXTERNAL_API_ERROR",
            message=message,
            status_code=status_code,
            detail=detail
        )

class ValidationException(PlainAPIException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, detail: dict = None):
        super().__init__(
            error="VALIDATION_ERROR",
            message=message,
            status_code=400,
            detail=detail
        )
