from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from pydantic import BaseModel
import httpx
from playwright.async_api import async_playwright
import random
import re
import json
import logging
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import redis
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/krypton")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# FastAPI app
app = FastAPI(title="Krypton Leads API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

# Pydantic models
class ScrapeRequest(BaseModel):
    business_type: str
    location: str
    max_results: int = 25

class ScrapeResponse(BaseModel):
    job_id: str
    status: str
    estimated_time: int

class Lead(BaseModel):
    business_name: str
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    quality_score: int

class ScrapeResult(BaseModel):
    job_id: str
    status: str
    leads: List[Lead]
    total_found: int
    processing_time: float

# Database models
class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    business_type = Column(String, nullable=False)
    location = Column(String, nullable=False)
    max_results = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)

# Create tables
Base.metadata.create_all(bind=engine)

# Browser pool for connection reuse
class BrowserPool:
    def __init__(self, max_contexts=3):
        self.browser = None
        self.contexts = []
        self.max_contexts = max_contexts
        
    async def get_browser(self):
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--memory-pressure-off'
                ]
            )
        return self.browser
    
    @asynccontextmanager
    async def get_context(self):
        context = None
        try:
            if self.contexts:
                context = self.contexts.pop()
            else:
                browser = await self.get_browser()
                context = await browser.new_context(
                    user_agent=get_random_user_agent(),
                    viewport={'width': 1920, 'height': 1080}
                )
            
            yield context
        finally:
            if context and len(self.contexts) < self.max_contexts:
                self.contexts.append(context)
            elif context:
                await context.close()

# Global browser pool
browser_pool = BrowserPool()

# User agent rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT token verification
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Core scraping logic
async def extract_business_data(page, element, business_num: int) -> Optional[dict]:
    """Extract business data from Google Maps element"""
    try:
        # Click on business
        await element.click()
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        lead = {
            'business_name': '',
            'website': '',
            'phone': '',
            'address': '',
            'rating': 0,
            'reviews': 0
        }
        
        # Extract business name
        name_selectors = ['h1', '[data-attrid="title"]', '.DUwDvf']
        for selector in name_selectors:
            try:
                name_element = await page.query_selector(selector)
                if name_element:
                    name = await name_element.inner_text()
                    if name and len(name) > 2:
                        lead['business_name'] = name.strip()
                        break
            except:
                continue
        
        if not lead['business_name']:
            return None
        
        # Extract website
        try:
            website_element = await page.query_selector('a[href*="http"]:not([href*="google"]):not([href*="maps"])')
            if website_element:
                lead['website'] = await website_element.get_attribute('href')
        except:
            pass
        
        # Extract phone
        try:
            phone_element = await page.query_selector('button[data-item-id*="phone"]')
            if phone_element:
                lead['phone'] = (await phone_element.inner_text()).strip()
        except:
            pass
        
        # Extract address
        try:
            address_element = await page.query_selector('button[data-item-id="address"]')
            if address_element:
                lead['address'] = (await address_element.inner_text()).strip()
        except:
            pass
        
        # Calculate quality score
        quality = 0
        if lead['business_name']: quality += 1
        if lead['website']: quality += 3
        if lead['phone']: quality += 2
        if lead['address']: quality += 1
        
        lead['quality_score'] = min(quality, 10)
        
        return lead
        
    except Exception as e:
        logger.error(f"Error extracting business {business_num}: {str(e)}")
        return None

async def scrape_leads_optimized(business_type: str, location: str, max_results: int) -> List[dict]:
    """Optimized lead scraping with parallel processing"""
    leads = []
    
    try:
        async with browser_pool.get_context() as context:
            page = await context.new_page()
            
            # Block unnecessary resources
            await page.route('**/*.{css,png,jpg,jpeg,gif,svg,woff,woff2}', lambda route: route.abort())
            
            # Navigate to Google Maps
            search_url = f"https://www.google.com/maps/search/{business_type}+{location}".replace(' ', '+')
            await page.goto(search_url, timeout=15000)
            
            # Wait for results
            await page.wait_for_selector('[role="main"]', timeout=10000)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Get business elements
            business_elements = await page.query_selector_all('[data-result-index]')
            
            if not business_elements:
                return leads
            
            # Process in batches
            batch_size = min(5, max_results)
            total_elements = min(len(business_elements), max_results)
            
            for i in range(0, total_elements, batch_size):
                batch = business_elements[i:i + batch_size]
                
                # Process batch in parallel
                tasks = []
                for idx, element in enumerate(batch):
                    tasks.append(extract_business_data(page, element, i + idx))
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, dict) and result.get('business_name'):
                        leads.append(result)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(0.5, 1.0))
        
        return leads
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return leads

# Background task for scraping
async def process_scrape_job(job_id: str, user_id: str, business_type: str, location: str, max_results: int):
    """Background task to process scraping job"""
    db = SessionLocal()
    
    try:
        # Update job status to processing
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if job:
            job.status = "processing"
            db.commit()
        
        # Perform scraping
        start_time = datetime.utcnow()
        leads = await scrape_leads_optimized(business_type, location, max_results)
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Update job with results
        if job:
            job.status = "completed"
            job.results = {
                "leads": leads,
                "total_found": len(leads),
                "processing_time": processing_time
            }
            job.completed_at = datetime.utcnow()
            db.commit()
        
        # Cache results
        cache_key = f"scrape:{job_id}"
        redis_client.setex(
            cache_key, 
            3600,  # 1 hour
            json.dumps({
                "job_id": job_id,
                "status": "completed",
                "leads": leads,
                "total_found": len(leads),
                "processing_time": processing_time
            })
        )
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
    finally:
        db.close()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Krypton Leads API v1.0.0"}

@app.post("/scrape", response_model=ScrapeResponse)
async def create_scrape_job(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a new scraping job"""
    
    # Generate job ID
    job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
    
    # Create job record
    job = ScrapeJob(
        id=job_id,
        user_id=user_id,
        business_type=request.business_type,
        location=request.location,
        max_results=request.max_results
    )
    db.add(job)
    db.commit()
    
    # Start background task
    background_tasks.add_task(
        process_scrape_job,
        job_id,
        user_id,
        request.business_type,
        request.location,
        request.max_results
    )
    
    # Estimate processing time
    estimated_time = min(30 + (request.max_results * 0.5), 300)  # Max 5 minutes
    
    return ScrapeResponse(
        job_id=job_id,
        status="pending",
        estimated_time=int(estimated_time)
    )

@app.get("/scrape/{job_id}", response_model=ScrapeResult)
async def get_scrape_result(
    job_id: str,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get scraping job result"""
    
    # Check cache first
    cache_key = f"scrape:{job_id}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Check database
    job = db.query(ScrapeJob).filter(
        ScrapeJob.id == job_id,
        ScrapeJob.user_id == user_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == "completed" and job.results:
        return ScrapeResult(
            job_id=job_id,
            status=job.status,
            leads=[Lead(**lead) for lead in job.results["leads"]],
            total_found=job.results["total_found"],
            processing_time=job.results["processing_time"]
        )
    elif job.status == "failed":
        raise HTTPException(status_code=500, detail=job.error_message or "Scraping failed")
    else:
        return ScrapeResult(
            job_id=job_id,
            status=job.status,
            leads=[],
            total_found=0,
            processing_time=0
        )

@app.get("/jobs")
async def list_user_jobs(
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """List user's scraping jobs"""
    jobs = db.query(ScrapeJob).filter(
        ScrapeJob.user_id == user_id
    ).order_by(ScrapeJob.created_at.desc()).limit(20).all()
    
    return [
        {
            "job_id": job.id,
            "business_type": job.business_type,
            "location": job.location,
            "status": job.status,
            "created_at": job.created_at,
            "total_leads": len(job.results.get("leads", [])) if job.results else 0
        }
        for job in jobs
    ]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)