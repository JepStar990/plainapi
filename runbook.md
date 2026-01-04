# 1. Clone and setup
git clone <repository>
cd plainapi

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 4. Scrape NASA documentation
python scripts/scrape_nasa_docs.py

# 5. Start the server
uvicorn src.api.main:app --reload

# 6. Test the API
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I use NASA APIs?"}'
