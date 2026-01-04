import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "PlainAPI"
    app_version: str = "1.0.0"
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    port: int = int(os.getenv("APP_PORT", 8000))
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    
    # API Keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    nasa_api_key: str = os.getenv("NASA_API_KEY", "DEMO_KEY")
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    vector_store_path: Path = data_dir / "vector_store"
    raw_docs_path: Path = data_dir / "raw_docs"
    processed_docs_path: Path = data_dir / "processed_docs"
    
    # LLM
    primary_llm_model: str = os.getenv("PRIMARY_LLM_MODEL", "gpt-3.5-turbo")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", 
                                   "sentence-transformers/all-MiniLM-L6-v2")
    max_tokens: int = int(os.getenv("MAX_TOKENS", 4096))
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", 0.1))
    
    # NASA API
    nasa_base_url: str = "https://api.nasa.gov"
    
    # Vector Store
    collection_name: str = "nasa_api_docs"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Rate Limiting
    nasa_rate_limit: int = int(os.getenv("NASA_API_RATE_LIMIT", 1000))
    user_rate_limit: int = int(os.getenv("USER_RATE_LIMIT", 100))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class NASAConfig:
    """NASA API specific configuration."""
    
    @staticmethod
    def get_endpoints() -> Dict[str, str]:
        return {
            "apod": "/planetary/apod",
            "mars_photos": "/mars-photos/api/v1/rovers/{rover}/photos",
            "earth_imagery": "/planetary/earth/imagery",
            "neo_feed": "/neo/rest/v1/feed",
            "donki": "/DONKI/{service}",
            "insight": "/insight_weather/",
            "image_library": "https://images-api.nasa.gov/search",
            "exoplanet": "/exoplanet/archive",
            "techtransfer": "/techtransfer/patent/",
        }
    
    @staticmethod
    def get_api_documentation_urls() -> Dict[str, str]:
        return {
            "apod": "https://api.nasa.gov/#apod",
            "mars_photos": "https://api.nasa.gov/#mars-rover-photos",
            "earth": "https://api.nasa.gov/#earth",
            "neo": "https://api.nasa.gov/#neo",
            "donki": "https://api.nasa.gov/#donki",
            "insight": "https://api.nasa.gov/#insight",
            "exoplanet": "https://api.nasa.gov/#exoplanet",
            "techtransfer": "https://api.nasa.gov/#techtransfer",
        }


# Global settings instance
settings = Settings()

# Create necessary directories
def create_directories():
    """Create required directories if they don't exist."""
    directories = [
        settings.data_dir,
        settings.vector_store_path,
        settings.raw_docs_path,
        settings.processed_docs_path,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
