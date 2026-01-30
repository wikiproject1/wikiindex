from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="WikiTrust Index API",
    description="API for Swahili-first Trust & Translation Reliability System",
    version="0.1.0",
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:4445",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel
from api.services.wikimedia import WikimediaService
from api.services.analysis import AnalysisService

# ... existing code ...

class AnalyzeRequest(BaseModel):
    url: str

@app.get("/api")
async def root():
    return {
        "message": "Welcome to WikiTrust Index API",
        "status": "online",
        "version": "0.1.0"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/suggest")
async def get_suggestions(q: str):
    wiki_service = WikimediaService()
    suggestions = await wiki_service.search_suggestions(q)
    return suggestions

@app.post("/api/analyze")
async def analyze_article(request: AnalyzeRequest):
    wiki_service = WikimediaService()
    analysis_service = AnalysisService()
    
    title = wiki_service.extract_title_from_url(request.url)
    if not title:
        # Try to treat the input as a search term if it doesn't look like a URL
        if not request.url.startswith("http"):
             title = request.url
        else:
             return {"error": "Invalid Wikipedia URL"}
    
    # 1. Fetch Swahili data
    sw_data = await wiki_service.get_page_content(title, "sw")
    if not sw_data:
        return {"error": "Swahili article not found"}
    
    # 2. Fetch language information (from Swahili page)
    lang_info = await wiki_service.get_langlinks(title, "sw")
    
    # 3. Fetch English data if it exists
    en_data = None
    if lang_info.get("en"):
        en_data = await wiki_service.get_page_content(lang_info["en"], "en")
    
    result = analysis_service.analyze_article(sw_data, en_data, lang_info)
    return result

