#!/usr/bin/env python3
"""
Krypton Leads Scraper - Async Version
Advanced lead generation with async operations, data validation, and persistence
"""

import asyncio
import aiohttp
import aiosqlite
import json
import re
import time
import random
import csv
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

# Import validation libraries
try:
    import phonenumbers
    from phonenumbers import NumberParseException
    from email_validator import validate_email, EmailNotValidError
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

# Import async throttling
try:
    from asyncio_throttle import Throttler
    THROTTLING_AVAILABLE = True
except ImportError:
    THROTTLING_AVAILABLE = False

@dataclass
class BusinessLead:
    """Data class for business lead with validation"""
    name: str = ""
    website: str = ""
    phone: str = ""
    address: str = ""
    email: str = ""
    instagram: str = ""
    facebook: str = ""
    tiktok: str = ""
    twitter: str = ""
    owner_twitter: str = ""
    quality_score: int = 0
    data_completeness: float = 0.0
    scraped_at: str = ""
    
    def __post_init__(self):
        self.scraped_at = datetime.now().isoformat()
        self.calculate_quality_score()
    
    def calculate_quality_score(self):
        """Calculate lead quality score based on data completeness"""
        fields = [self.name, self.website, self.phone, self.email, self.address]
        social_fields = [self.instagram, self.facebook, self.tiktok, self.twitter]
        
        # Base score from core fields
        core_score = sum(1 for field in fields if field.strip()) * 2
        
        # Bonus for social media
        social_score = sum(1 for field in social_fields if field.strip())
        
        # Bonus for validated email/phone
        validation_bonus = 0
        if self.email and self.validate_email():
            validation_bonus += 2
        if self.phone and self.validate_phone():
            validation_bonus += 2
        
        self.quality_score = min(10, core_score + social_score + validation_bonus)
        self.data_completeness = (core_score + social_score) / 14.0 * 100
    
    def validate_email(self) -> bool:
        """Validate email format"""
        if not VALIDATION_AVAILABLE or not self.email:
            return False
        try:
            validate_email(self.email)
            return True
        except EmailNotValidError:
            return False
    
    def validate_phone(self) -> bool:
        """Validate and format phone number"""
        if not VALIDATION_AVAILABLE or not self.phone:
            return False
        try:
            # Try to parse phone number
            parsed = phonenumbers.parse(self.phone, "US")
            if phonenumbers.is_valid_number(parsed):
                # Format the phone number
                self.phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
                return True
        except NumberParseException:
            pass
        return False

class AsyncScraperDatabase:
    """Async database handler for scraper persistence"""
    
    def __init__(self, db_path: str = "scraper_data.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS scrape_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_type TEXT,
                    location TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    total_leads INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_progress'
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS business_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    name TEXT,
                    website TEXT,
                    phone TEXT,
                    address TEXT,
                    email TEXT,
                    instagram TEXT,
                    facebook TEXT,
                    tiktok TEXT,
                    twitter TEXT,
                    owner_twitter TEXT,
                    quality_score INTEGER,
                    data_completeness REAL,
                    scraped_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES scrape_sessions (id)
                )
            """)
            
            await db.commit()
    
    async def create_session(self, business_type: str, location: str) -> int:
        """Create new scrape session"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO scrape_sessions (business_type, location, started_at)
                VALUES (?, ?, ?)
            """, (business_type, location, datetime.now().isoformat()))
            session_id = cursor.lastrowid
            await db.commit()
            return session_id
    
    async def save_lead(self, session_id: int, lead: BusinessLead):
        """Save business lead to database"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO business_leads (
                    session_id, name, website, phone, address, email,
                    instagram, facebook, tiktok, twitter, owner_twitter,
                    quality_score, data_completeness, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, lead.name, lead.website, lead.phone, lead.address,
                lead.email, lead.instagram, lead.facebook, lead.tiktok,
                lead.twitter, lead.owner_twitter, lead.quality_score,
                lead.data_completeness, lead.scraped_at
            ))
            await db.commit()
    
    async def complete_session(self, session_id: int, total_leads: int):
        """Mark session as completed"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE scrape_sessions 
                SET completed_at = ?, total_leads = ?, status = 'completed'
                WHERE id = ?
            """, (datetime.now().isoformat(), total_leads, session_id))
            await db.commit()
    
    async def get_incomplete_sessions(self) -> List[Dict]:
        """Get incomplete scrape sessions for resume functionality"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM scrape_sessions WHERE status = 'in_progress'
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

class SmartRateLimiter:
    """Smart rate limiting with adaptive delays"""
    
    def __init__(self):
        self.request_times = []
        self.base_delay = 0.5
        self.max_delay = 5.0
        self.requests_per_minute = 60
    
    async def wait(self):
        """Adaptive rate limiting based on recent request patterns"""
        now = time.time()
        
        # Clean old requests (older than 1 minute)
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Calculate dynamic delay
        if len(self.request_times) >= self.requests_per_minute:
            delay = min(self.max_delay, self.base_delay * 2)
        else:
            delay = self.base_delay
        
        # Add some randomization
        delay += random.uniform(0, 0.5)
        
        await asyncio.sleep(delay)
        self.request_times.append(now)

class AsyncBusinessScraper:
    """Main async scraper class with all improvements"""
    
    def __init__(self):
        self.db = AsyncScraperDatabase()
        self.rate_limiter = SmartRateLimiter()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        ]
        self.session = None
        self.progress_callback = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    async def create_session(self) -> aiohttp.ClientSession:
        """Create optimized aiohttp session"""
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=20,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        return aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        )
    
    async def extract_social_media_links(self, text: str, base_url: str) -> Dict[str, str]:
        """Extract social media links from text"""
        social_links = {
            'instagram': '',
            'facebook': '',
            'tiktok': '',
            'twitter': '',
            'owner_twitter': ''
        }
        
        patterns = {
            'instagram': [
                r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+/?',
                r'instagram\.com/[a-zA-Z0-9_.]+/?'
            ],
            'facebook': [
                r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_.]+/?',
                r'facebook\.com/[a-zA-Z0-9_.]+/?'
            ],
            'tiktok': [
                r'https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.]+/?',
                r'tiktok\.com/@[a-zA-Z0-9_.]+/?'
            ],
            'twitter': [
                r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/?',
                r'(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/?'
            ]
        }
        
        for platform, platform_patterns in patterns.items():
            for pattern in platform_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    link = matches[0]
                    if not link.startswith('http'):
                        link = f"https://{link}"
                    # Convert old twitter.com links to x.com
                    if platform == 'twitter':
                        link = link.replace('twitter.com', 'x.com')
                    social_links[platform] = link
                    break
        
        return social_links
    
    async def scrape_website_async(self, url: str) -> Dict[str, str]:
        """Async website scraping with enhanced data extraction"""
        if not url or not url.startswith('http'):
            return {'email': '', 'instagram': '', 'facebook': '', 'tiktok': '', 'twitter': '', 'owner_twitter': ''}
        
        try:
            await self.rate_limiter.wait()
            
            headers = {'User-Agent': self.get_random_user_agent()}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {'email': '', 'instagram': '', 'facebook': '', 'tiktok': '', 'twitter': '', 'owner_twitter': ''}
                
                html_content = await response.text()
                
                # Extract emails
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, html_content)
                emails = list(set([email.lower() for email in emails if email]))
                
                # Extract social media links
                social_links = await self.extract_social_media_links(html_content, url)
                
                return {
                    'email': emails[0] if emails else '',
                    'instagram': social_links['instagram'],
                    'facebook': social_links['facebook'],
                    'tiktok': social_links['tiktok'],
                    'twitter': social_links['twitter'],
                    'owner_twitter': social_links['owner_twitter']
                }
                
        except Exception as e:
            self.logger.warning(f"Error scraping website {url}: {e}")
            return {'email': '', 'instagram': '', 'facebook': '', 'tiktok': '', 'twitter': '', 'owner_twitter': ''}
    
    async def enrich_lead_async(self, lead_data: Dict) -> BusinessLead:
        """Async lead enrichment with website scraping"""
        lead = BusinessLead(**lead_data)
        
        if lead.website:
            website_info = await self.scrape_website_async(lead.website)
            lead.email = website_info['email']
            lead.instagram = website_info['instagram']
            lead.facebook = website_info['facebook']
            lead.tiktok = website_info['tiktok']
            if not lead.twitter:
                lead.twitter = website_info['twitter']
            if not lead.owner_twitter:
                lead.owner_twitter = website_info['owner_twitter']
        
        # Recalculate quality score after enrichment
        lead.calculate_quality_score()
        
        return lead
    
    async def scrape_google_maps_async(self, business_type: str, location: str, 
                                     session_id: int = None) -> List[BusinessLead]:
        """Async Google Maps scraping with Playwright"""
        from playwright.async_api import async_playwright
        
        leads = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', '--disable-dev-shm-usage', '--disable-images',
                    '--disable-gpu', '--disable-extensions', '--disable-plugins',
                    '--disable-web-security', '--disable-features=TranslateUI'
                ]
            )
            
            context = await browser.new_context(
                user_agent=self.get_random_user_agent(),
                viewport={'width': 1280, 'height': 720}
            )
            
            page = await context.new_page()
            
            try:
                # Navigate to Google Maps
                search_query = f"{business_type} {location}"
                maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
                
                self.logger.info(f"Scraping Google Maps: {maps_url}")
                await page.goto(maps_url, wait_until='networkidle')
                
                # Wait for results
                await page.wait_for_selector('[role="main"], .hfpxzc, [data-result-index]', timeout=10000)
                
                # Optimized scrolling
                await page.evaluate('document.querySelector("[role=main]")?.scrollTo(0, 2000)')
                await asyncio.sleep(0.5)
                await page.evaluate('document.querySelector("[role=main]")?.scrollTo(0, 4000)')
                await asyncio.sleep(0.5)
                
                # Find business listings
                selectors = [
                    '[role="article"]',
                    '[data-result-index]', 
                    'div[jsaction*="mouseover"]',
                    '.hfpxzc'
                ]
                
                listings = []
                for selector in selectors:
                    listings = await page.query_selector_all(selector)
                    if listings:
                        self.logger.info(f"Found {len(listings)} businesses with selector: {selector}")
                        break
                
                # Process listings asynchronously
                tasks = []
                for i, listing in enumerate(listings[:25]):  # Process up to 25 businesses
                    task = self.process_listing_async(page, listing, i)
                    tasks.append(task)
                
                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter successful results
                for result in results:
                    if isinstance(result, BusinessLead) and result.name:
                        leads.append(result)
                        if session_id:
                            await self.db.save_lead(session_id, result)
                        
                        # Progress callback
                        if self.progress_callback:
                            await self.progress_callback(len(leads), result)
                
            except Exception as e:
                self.logger.error(f"Error scraping Google Maps: {e}")
            
            finally:
                await browser.close()
        
        return leads
    
    async def process_listing_async(self, page, listing, index: int) -> Optional[BusinessLead]:
        """Process individual business listing"""
        try:
            lead_data = {
                'name': '',
                'website': '',
                'phone': '',
                'address': '',
                'email': '',
                'instagram': '',
                'facebook': '',
                'tiktok': '',
                'twitter': '',
                'owner_twitter': ''
            }
            
            # Extract name from listing card
            name_selectors = [
                '.qBF1Pd',
                '.NrDZNb', 
                '.fontHeadlineSmall',
                '.hfpxzc .fontHeadlineSmall'
            ]
            
            for selector in name_selectors:
                name_element = await listing.query_selector(selector)
                if name_element:
                    potential_name = await name_element.inner_text()
                    if potential_name and len(potential_name.strip()) > 2:
                        lead_data['name'] = potential_name.strip()
                        break
            
            if not lead_data['name']:
                return None
            
            # Click for details
            try:
                await listing.scroll_into_view_if_needed(timeout=2000)
                await asyncio.sleep(0.2)
                await listing.click(timeout=3000)
                await asyncio.sleep(1)
                
                # Extract contact details
                # Website
                website_selectors = [
                    'a[href*="http"]:has-text("Website")',
                    '[data-value="Website"] a',
                    'a[href*="http"]:not([href*="google"])'
                ]
                
                for selector in website_selectors:
                    website_element = await page.query_selector(selector)
                    if website_element:
                        href = await website_element.get_attribute('href')
                        if href and 'google' not in href and 'maps' not in href:
                            lead_data['website'] = href
                            break
                
                # Phone
                phone_selectors = [
                    'button[data-item-id*="phone"]',
                    '[data-value*="phone"] span',
                    'button:has-text("Call")'
                ]
                
                for selector in phone_selectors:
                    phone_element = await page.query_selector(selector)
                    if phone_element:
                        phone_text = await phone_element.inner_text()
                        if phone_text and len(phone_text.strip()) > 5:
                            lead_data['phone'] = phone_text.strip()
                            break
                
                # Address
                address_selectors = [
                    'button[data-item-id="address"]',
                    '[data-value="Address"] div',
                    'button:has-text("Directions")'
                ]
                
                for selector in address_selectors:
                    address_element = await page.query_selector(selector)
                    if address_element:
                        address_text = await address_element.inner_text()
                        if address_text:
                            lead_data['address'] = address_text.strip()
                            break
                            
            except Exception as e:
                self.logger.warning(f"Error extracting details for {lead_data['name']}: {e}")
            
            # Create and enrich lead
            return await self.enrich_lead_async(lead_data)
            
        except Exception as e:
            self.logger.warning(f"Error processing listing {index}: {e}")
            return None
    
    async def start_scraping(self, business_type: str, location: str, 
                           progress_callback=None) -> List[BusinessLead]:
        """Main scraping orchestrator"""
        self.progress_callback = progress_callback
        
        # Initialize database
        await self.db.init_db()
        
        # Create scrape session
        session_id = await self.db.create_session(business_type, location)
        
        # Create HTTP session
        self.session = await self.create_session()
        
        try:
            # Start scraping
            leads = await self.scrape_google_maps_async(business_type, location, session_id)
            
            # Complete session
            await self.db.complete_session(session_id, len(leads))
            
            # Filter and sort by quality
            high_quality_leads = [lead for lead in leads if lead.quality_score >= 6]
            high_quality_leads.sort(key=lambda x: x.quality_score, reverse=True)
            
            self.logger.info(f"Scraping complete: {len(leads)} total leads, {len(high_quality_leads)} high quality")
            
            return leads
            
        finally:
            await self.session.close()
    
    async def export_to_csv(self, leads: List[BusinessLead], business_type: str, location: str) -> str:
        """Export leads to CSV with quality metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}.csv"
        
        fieldnames = [
            'Business Name', 'Website', 'Email', 'Phone', 'Address',
            'Instagram', 'Facebook', 'TikTok', 'Twitter', 'Owner Twitter',
            'Quality Score', 'Data Completeness %', 'Scraped At'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for lead in leads:
                writer.writerow({
                    'Business Name': lead.name,
                    'Website': lead.website,
                    'Email': lead.email,
                    'Phone': lead.phone,
                    'Address': lead.address,
                    'Instagram': lead.instagram,
                    'Facebook': lead.facebook,
                    'TikTok': lead.tiktok,
                    'Twitter': lead.twitter,
                    'Owner Twitter': lead.owner_twitter,
                    'Quality Score': lead.quality_score,
                    'Data Completeness %': f"{lead.data_completeness:.1f}%",
                    'Scraped At': lead.scraped_at
                })
        
        return filename

# Example usage
async def main():
    """Example usage of the async scraper"""
    scraper = AsyncBusinessScraper()
    
    async def progress_update(count: int, lead: BusinessLead):
        print(f"Found lead #{count}: {lead.name} (Quality: {lead.quality_score}/10)")
    
    leads = await scraper.start_scraping("restaurant", "Dallas, TX", progress_update)
    filename = await scraper.export_to_csv(leads, "restaurant", "Dallas, TX")
    
    print(f"\nScraping complete!")
    print(f"Total leads: {len(leads)}")
    print(f"High quality leads (6+): {len([l for l in leads if l.quality_score >= 6])}")
    print(f"CSV exported: {filename}")

if __name__ == "__main__":
    asyncio.run(main())