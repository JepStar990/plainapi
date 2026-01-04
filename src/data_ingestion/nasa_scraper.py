import asyncio
import aiohttp
from typing import List, Dict, Optional
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import json
import time

from .schemas import RawDocument, ScrapingResult
from src.core.config import settings, NASAConfig
from src.core.utils import clean_text, get_file_extension

logger = logging.getLogger(__name__)

class NASADocumentationScraper:
    """Scraper for NASA API documentation."""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.base_url = "https://api.nasa.gov"
        self.doc_urls = NASAConfig.get_api_documentation_urls()
        
    async def scrape_all(self) -> ScrapingResult:
        """Scrape all NASA API documentation."""
        logger.info("Starting NASA API documentation scraping")
        start_time = time.time()
        
        result = ScrapingResult(
            successful=True,
            total_urls=len(self.doc_urls),
            processed_urls=0,
            start_time=start_time
        )
        
        try:
            # Create tasks for all URLs
            tasks = []
            for api_name, url in self.doc_urls.items():
                task = self._scrape_single_url(url, api_name)
                tasks.append(task)
            
            # Process in batches
            for i in range(0, len(tasks), self.max_concurrent):
                batch = tasks[i:i + self.max_concurrent]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for doc_result in batch_results:
                    if isinstance(doc_result, Exception):
                        error_msg = f"Error scraping: {str(doc_result)}"
                        logger.error(error_msg)
                        result.errors.append(error_msg)
                    elif doc_result:
                        result.documents.append(doc_result)
                        result.processed_urls += 1
            
            result.successful = len(result.errors) == 0
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            result.successful = False
            result.errors.append(str(e))
        
        result.end_time = time.time()
        logger.info(f"Scraping completed: {result.processed_urls}/{result.total_urls} URLs")
        
        return result
    
    async def _scrape_single_url(self, url: str, api_name: str) -> Optional[RawDocument]:
        """Scrape a single URL."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; PlainAPI/1.0; +https://github.com/plainapi)'
                }
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'application/json' in content_type:
                        content = await response.json()
                        text_content = json.dumps(content, indent=2)
                        content_type_str = 'json'
                    else:
                        text_content = await response.text()
                        content_type_str = 'html'
                    
                    # Clean and extract text
                    if content_type_str == 'html':
                        soup = BeautifulSoup(text_content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style", "nav", "footer"]):
                            script.decompose()
                        
                        # Get text
                        text_content = soup.get_text()
                    
                    # Clean the text
                    cleaned_content = clean_text(text_content)
                    
                    if not cleaned_content:
                        logger.warning(f"No content extracted from {url}")
                        return None
                    
                    document = RawDocument(
                        url=url,
                        content=cleaned_content,
                        content_type=content_type_str,
                        headers=dict(response.headers)
                    )
                    
                    logger.debug(f"Successfully scraped {url}")
                    return document
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout scraping {url}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def save_raw_documents(self, documents: List[RawDocument]) -> List[Path]:
        """Save raw documents to disk."""
        saved_paths = []
        
        for i, doc in enumerate(documents):
            # Create filename from URL
            filename = doc.url.split('//')[-1].replace('/', '_').replace('?', '_')
            if len(filename) > 100:
                filename = filename[:100]
            
            filepath = settings.raw_docs_path / f"{i:03d}_{filename}.json"
            
            # Save as JSON
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(doc.dict(), f, indent=2, default=str)
            
            saved_paths.append(filepath)
        
        logger.info(f"Saved {len(saved_paths)} raw documents to disk")
        return saved_paths

class NASAApiExamples:
    """Collect example API calls and responses."""
    
    @staticmethod
    def get_example_requests() -> List[Dict]:
        """Get example API requests for NASA endpoints."""
        examples = []
        
        # APOD Example
        examples.append({
            "api_name": "APOD",
            "endpoint": "/planetary/apod",
            "description": "Astronomy Picture of the Day",
            "example_request": "GET https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&date=2023-11-15",
            "example_response": {
                "date": "2023-11-15",
                "explanation": "A stunning image of the Orion Nebula...",
                "hdurl": "https://apod.nasa.gov/apod/image/2311/orion_hubble_960.jpg",
                "media_type": "image",
                "service_version": "v1",
                "title": "The Great Orion Nebula",
                "url": "https://apod.nasa.gov/apod/image/2311/orion_hubble_960.jpg"
            },
            "parameters": [
                {"name": "date", "type": "string", "format": "YYYY-MM-DD", "required": False},
                {"name": "start_date", "type": "string", "format": "YYYY-MM-DD", "required": False},
                {"name": "end_date", "type": "string", "format": "YYYY-MM-DD", "required": False},
                {"name": "count", "type": "integer", "required": False},
                {"name": "thumbs", "type": "boolean", "required": False}
            ]
        })
        
        # Mars Rover Photos Example
        examples.append({
            "api_name": "Mars Rover Photos",
            "endpoint": "/mars-photos/api/v1/rovers/{rover}/photos",
            "description": "Photos from Mars rovers",
            "example_request": "GET https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/photos?earth_date=2023-11-15&api_key=DEMO_KEY",
            "example_response": {
                "photos": [
                    {
                        "id": 102693,
                        "sol": 1000,
                        "camera": {"id": 20, "name": "FHAZ", "rover_id": 5},
                        "img_src": "http://mars.nasa.gov/msl-raw-images/...jpg",
                        "earth_date": "2023-11-15",
                        "rover": {
                            "id": 5,
                            "name": "Perseverance",
                            "landing_date": "2021-02-18",
                            "launch_date": "2020-07-30",
                            "status": "active"
                        }
                    }
                ]
            },
            "parameters": [
                {"name": "rover", "type": "string", "required": True, "options": ["curiosity", "opportunity", "spirit", "perseverance"]},
                {"name": "earth_date", "type": "string", "format": "YYYY-MM-DD", "required": False},
                {"name": "sol", "type": "integer", "required": False},
                {"name": "camera", "type": "string", "required": False, "options": ["FHAZ", "RHAZ", "MAST", "CHEMCAM", "MAHLI", "MARDI", "NAVCAM", "PANCAM", "MINITES"]},
                {"name": "page", "type": "integer", "required": False}
            ]
        })
        
        # Add more examples...
        
        return examples
