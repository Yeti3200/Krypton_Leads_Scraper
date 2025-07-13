from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio
import random
from typing import List, Optional

app = FastAPI(title="Krypton Leads API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ScrapeRequest(BaseModel):
    business_type: str
    location: str
    max_results: int = 25

class Lead(BaseModel):
    business_name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    quality_score: int

# User agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

async def scrape_leads(business_type: str, location: str, max_results: int) -> List[dict]:
    """Simple lead scraping"""
    leads = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=get_random_user_agent())
            page = await context.new_page()
            
            # Navigate to Google Maps
            search_url = f"https://www.google.com/maps/search/{business_type}+{location}".replace(' ', '+')
            await page.goto(search_url, timeout=15000)
            
            # Wait for results
            await page.wait_for_selector('[role="main"]', timeout=10000)
            await asyncio.sleep(2)
            
            # Get business elements
            business_elements = await page.query_selector_all('[data-result-index]')
            
            for i, element in enumerate(business_elements[:max_results]):
                try:
                    await element.click()
                    await asyncio.sleep(1)
                    
                    # Extract data
                    name = ""
                    try:
                        name_el = await page.query_selector('h1')
                        if name_el:
                            name = await name_el.inner_text()
                    except:
                        pass
                    
                    phone = ""
                    try:
                        phone_el = await page.query_selector('button[data-item-id*="phone"]')
                        if phone_el:
                            phone = await phone_el.inner_text()
                    except:
                        pass
                    
                    website = ""
                    try:
                        website_el = await page.query_selector('a[href*="http"]:not([href*="google"])')
                        if website_el:
                            website = await website_el.get_attribute('href')
                    except:
                        pass
                    
                    if name:
                        quality = 1
                        if phone: quality += 2
                        if website: quality += 3
                        
                        leads.append({
                            "business_name": name,
                            "phone": phone,
                            "website": website,
                            "address": f"{location}",
                            "quality_score": min(quality, 10)
                        })
                        
                except Exception as e:
                    continue
            
            await browser.close()
            
    except Exception as e:
        print(f"Scraping error: {e}")
    
    return leads

@app.get("/")
async def root():
    return {"message": "Krypton Leads API"}

@app.post("/scrape")
async def create_scrape_job(request: ScrapeRequest):
    """Scrape leads"""
    leads = await scrape_leads(request.business_type, request.location, request.max_results)
    
    return {
        "success": True,
        "leads": leads,
        "total": len(leads)
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)