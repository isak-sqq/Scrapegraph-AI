from fastapi import FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from scrapegraphai.graphs import SmartScraperGraph
import os
import json

app = FastAPI(title="ScrapeGraphAI API")

# Simple API key auth to protect your endpoint
API_KEY = os.getenv("API_KEY", "change-me-secret")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key

class ScrapeRequest(BaseModel):
    url: str
    prompt: str

@app.get("/")
def root():
    return {"status": "ok", "message": "ScrapeGraphAI is running"}

@app.post("/scrape")
def scrape(req: ScrapeRequest, key: str = Security(verify_key)):
    graph_config = {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "openai/gpt-4o-mini",
        },
        "verbose": False,
        "headless": True,
    }

    try:
        scraper = SmartScraperGraph(
            prompt=req.prompt,
            source=req.url,
            config=graph_config
        )
        result = scraper.run()
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
