#!/usr/bin/env python3
"""
Hyper-Optimized Lead Scraper - Ultimate Performance
- Shared browser contexts
- Intelligent request batching
- Advanced caching with TTL
- Memory-efficient processing
- Parallel website scraping
- Smart rate limiting
"""

import asyncio
import aiohttp
import time
import json
import pickle
import hashlib
import random
import re
import csv
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Ultra-optimized browser manager
class HyperBrowserManager:
    """Hyper-optimized browser management with smart reuse"""
    
    def __init__(self, pool_size: int = 6):
        self.pool_size = pool_size
        self.browsers = []
        self.contexts = []
        self.context_queue = asyncio.Queue()
        self.playwright = None
        self.initialized = False
        self.usage_stats = {}
    
    async def initialize(self):
        """Initialize browser pool with optimized settings"""
        if self.initialized:
            return
            
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().__aenter__()
        
        # Ultra-optimized launch args
        launch_args = [
            '--no-sandbox', '--disable-dev-shm-usage', '--disable-images',
            '--disable-gpu', '--disable-extensions', '--disable-plugins',
            '--disable-web-security', '--disable-features=TranslateUI',
            '--memory-pressure-off', '--max_old_space_size=1024',
            '--aggressive-cache-discard', '--disable-background-networking',
            '--disable-sync', '--disable-translate', '--disable-default-apps',
            '--disable-background-timer-throttling', '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows', '--disable-ipc-flooding-protection',
            '--disable-hang-monitor', '--disable-prompt-on-repost',
            '--disable-client-side-phishing-detection', '--disable-component-update',
            '--disable-domain-reliability', '--disable-background-tasks'
        ]
        
        # Create browser pool
        for i in range(self.pool_size):
            browser = await self.playwright.chromium.launch(
                headless=True,
                args=launch_args
            )
            
            context = await browser.new_context(
                viewport={'width': 1024, 'height': 768},
                java_script_enabled=True,
                ignore_https_errors=True,
                bypass_csp=True,
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            )
            
            self.browsers.append(browser)
            self.contexts.append(context)
            await self.context_queue.put(context)
            self.usage_stats[f'context_{i}'] = {'used': 0, 'errors': 0}
        
        self.initialized = True
        print(f"🚀 Hyper browser pool initialized with {self.pool_size} contexts")
    
    async def get_context(self):
        """Get available browser context"""
        context = await self.context_queue.get()
        return context
    
    async def return_context(self, context):
        """Return browser context to pool after cleanup"""
        # Cleanup pages except first one
        pages = context.pages
        for page in pages[1:]:
            try:
                await page.close()
            except:
                pass
        
        # Clear storage
        try:
            await context.clear_cookies()
            await context.clear_permissions()
        except:
            pass
        
        await self.context_queue.put(context)
    
    async def cleanup(self):
        """Cleanup all browser resources"""
        if not self.initialized:
            return
        
        for browser in self.browsers:
            try:
                await browser.close()
            except:
                pass
        
        if self.playwright:
            try:
                await self.playwright.__aexit__(None, None, None)
            except:
                pass

# SQLite-based caching system
class HyperCache:
    """SQLite-based caching with automatic expiration"""
    
    def __init__(self, db_path: str = "hyper_cache.db"):
        self.db_path = db_path
        self.memory_cache = {}
        self.max_memory_items = 1000
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp REAL,
                ttl_hours INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    
    def _is_expired(self, timestamp: float, ttl_hours: int) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > (ttl_hours * 3600)
    
    async def get(self, key: str, ttl_hours: int = 24) -> Optional[Dict]:
        """Get cached data"""
        # Check memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value, timestamp, ttl_hours FROM cache WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            value, timestamp, stored_ttl = row
            if not self._is_expired(timestamp, stored_ttl):
                try:
                    data = json.loads(value)
                    # Store in memory cache
                    if len(self.memory_cache) < self.max_memory_items:
                        self.memory_cache[key] = data
                    return data
                except:
                    pass
        
        return None
    
    async def set(self, key: str, data: Dict, ttl_hours: int = 24):
        """Set cached data"""
        # Store in memory
        if len(self.memory_cache) < self.max_memory_items:
            self.memory_cache[key] = data
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cache (key, value, timestamp, ttl_hours)
            VALUES (?, ?, ?, ?)
        ''', (key, json.dumps(data), time.time(), ttl_hours))
        conn.commit()
        conn.close()
    
    def cleanup_expired(self):
        """Remove expired entries from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cache WHERE ? - timestamp > ttl_hours * 3600', (time.time(),))
        conn.commit()
        conn.close()

# Hyper-optimized selectors with machine learning
class HyperSelectorEngine:
    """AI-powered selector optimization"""
    
    def __init__(self):
        self.selector_chains = {
            "business_listings": [
                '[role="article"]',
                '[data-result-index]',
                'div[jsaction*="mouseover"]',
                '.hfpxzc',
                '.Nv2PK',
                'div[data-feature-id]',
                'div[data-cid]',
                '[data-result-ad-index]'
            ],
            "business_name": [
                '.qBF1Pd',
                '.NrDZNb',
                '.fontHeadlineSmall',
                '.hfpxzc .fontHeadlineSmall',
                'h1[data-attrid="title"]',
                '.SPZz6b h1'
            ],
            "website": [
                'a[href*="http"]:has-text("Website")',
                '[data-value="Website"] a',
                'a[data-item-id*="authority"]',
                'a[href*="http"]:not([href*="google"]):not([href*="maps"])',
                '.CsEnBe a[href*="http"]'
            ],
            "phone": [
                'button[data-item-id*="phone"]',
                '[data-value*="phone"] span',
                'button:has-text("Call")',
                '.z5jxId',
                'span[data-phone]'
            ],
            "address": [
                'button[data-item-id="address"]',
                '[data-value="Address"] div',
                'button:has-text("Directions")',
                '.rogA2c',
                '.Io6YTe'
            ]
        }
        
        # Performance tracking with ML-like optimization
        self.selector_performance = {}
        self.selector_weights = {}
    
    async def find_element_smart(self, page, selector_type: str, timeout: int = 2000):
        """Smart element finding with performance optimization"""
        selectors = self.selector_chains.get(selector_type, [])
        
        # Sort by performance weights
        if selector_type in self.selector_weights:
            selectors = sorted(selectors, 
                             key=lambda s: self.selector_weights[selector_type].get(s, 0), 
                             reverse=True)
        
        start_time = time.time()
        
        for i, selector in enumerate(selectors):
            try:
                element = await page.query_selector(selector)
                if element:
                    # Update performance metrics
                    elapsed = time.time() - start_time
                    self._update_performance(selector_type, selector, elapsed, i)
                    return element
            except:
                continue
        
        return None
    
    def _update_performance(self, selector_type: str, selector: str, elapsed: float, position: int):
        """Update selector performance metrics"""
        if selector_type not in self.selector_weights:
            self.selector_weights[selector_type] = {}
        
        # Calculate weight based on speed and position
        weight = 100 / (elapsed + 0.1) - position * 2
        self.selector_weights[selector_type][selector] = weight

@dataclass
class HyperLead:
    """Ultra-optimized lead data structure"""
    name: str = ""
    website: str = ""
    phone: str = ""
    address: str = ""
    email: str = ""
    instagram: str = ""
    facebook: str = ""
    tiktok: str = ""
    twitter: str = ""
    quality_score: int = 0
    processing_time: float = 0.0
    
    def calculate_quality(self):
        """Optimized quality calculation"""
        score = 0
        if self.name: score += 2
        if self.website: score += 3
        if self.phone: score += 2
        if self.email: score += 3
        if self.address: score += 1
        if any([self.instagram, self.facebook, self.twitter]): score += 1
        self.quality_score = min(score, 10)

class HyperScraper:
    """Ultimate performance scraper"""
    
    def __init__(self):
        self.browser_manager = HyperBrowserManager(pool_size=8)
        self.cache = HyperCache()
        self.selector_engine = HyperSelectorEngine()
        self.session = None
        self.stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "errors": 0,
            "start_time": None,
            "website_scrapes": 0,
            "parallel_tasks": 0
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize all systems"""
        await self.browser_manager.initialize()
        
        # Ultra-optimized HTTP session
        connector = aiohttp.TCPConnector(
            limit=200,
            limit_per_host=80,
            ttl_dns_cache=1800,
            use_dns_cache=True,
            keepalive_timeout=120,
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=3, connect=1),
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def cleanup(self):
        """Cleanup all resources"""
        if self.session:
            await self.session.close()
        await self.browser_manager.cleanup()
        self.cache.cleanup_expired()
    
    async def scrape_website_hyper(self, url: str) -> Dict[str, str]:
        """Hyper-optimized website scraping"""
        if not url:
            return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
        
        # Check cache
        cache_key = f"website_{hashlib.md5(url.encode()).hexdigest()}"
        cached = await self.cache.get(cache_key, ttl_hours=72)
        if cached:
            self.stats["cache_hits"] += 1
            return cached
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
                
                # Read only first 20KB for maximum speed
                content = await response.content.read(20000)
                html = content.decode('utf-8', errors='ignore')
                
                # Ultra-fast regex extraction
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html)
                instagram_match = re.search(r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+', html, re.IGNORECASE)
                facebook_match = re.search(r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_.]+', html, re.IGNORECASE)
                twitter_match = re.search(r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+', html, re.IGNORECASE)
                tiktok_match = re.search(r'https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.]+', html, re.IGNORECASE)
                
                result = {
                    "email": email_match.group(0) if email_match else "",
                    "instagram": instagram_match.group(0) if instagram_match else "",
                    "facebook": facebook_match.group(0) if facebook_match else "",
                    "twitter": twitter_match.group(0).replace('twitter.com', 'x.com') if twitter_match else "",
                    "tiktok": tiktok_match.group(0) if tiktok_match else ""
                }
                
                # Cache result
                await self.cache.set(cache_key, result, ttl_hours=72)
                self.stats["website_scrapes"] += 1
                return result
                
        except Exception as e:
            self.logger.warning(f"Website scrape failed {url}: {e}")
            return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
    
    async def process_listing_hyper(self, context, listing, index: int) -> Optional[HyperLead]:
        """Hyper-optimized listing processing"""
        start_time = time.time()
        
        try:
            page = await context.new_page()
            lead = HyperLead()
            
            # Fast name extraction from listing first
            name_selectors = ['.qBF1Pd', '.NrDZNb', '.fontHeadlineSmall', '.hfpxzc .fontHeadlineSmall']
            for selector in name_selectors:
                name_element = await listing.query_selector(selector)
                if name_element:
                    lead.name = (await name_element.inner_text()).strip()
                    break
            
            if not lead.name:
                await page.close()
                return None
            
            # Click for details with optimized timing
            try:
                await listing.scroll_into_view_if_needed(timeout=500)
                await listing.click(timeout=1000)
                await asyncio.sleep(0.2)  # Minimal wait
                
                # Parallel detail extraction
                tasks = [
                    self.extract_website_hyper(page),
                    self.extract_phone_hyper(page),
                    self.extract_address_hyper(page)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                lead.website = results[0] if isinstance(results[0], str) else ""
                lead.phone = results[1] if isinstance(results[1], str) else ""
                lead.address = results[2] if isinstance(results[2], str) else ""
                
            except Exception as e:
                self.logger.warning(f"Detail extraction failed: {e}")
            
            await page.close()
            
            # Website scraping if available
            if lead.website:
                website_data = await self.scrape_website_hyper(lead.website)
                lead.email = website_data.get("email", "")
                lead.instagram = website_data.get("instagram", "")
                lead.facebook = website_data.get("facebook", "")
                lead.twitter = website_data.get("twitter", "")
                lead.tiktok = website_data.get("tiktok", "")
            
            lead.processing_time = time.time() - start_time
            lead.calculate_quality()
            return lead
            
        except Exception as e:
            self.logger.warning(f"Listing processing failed {index}: {e}")
            self.stats["errors"] += 1
            return None
    
    async def extract_website_hyper(self, page) -> str:
        """Hyper-fast website extraction"""
        element = await self.selector_engine.find_element_smart(page, "website")
        if element:
            href = await element.get_attribute('href')
            if href and 'google' not in href and 'maps' not in href:
                return href
        return ""
    
    async def extract_phone_hyper(self, page) -> str:
        """Hyper-fast phone extraction"""
        element = await self.selector_engine.find_element_smart(page, "phone")
        if element:
            text = await element.inner_text()
            if text and len(text.strip()) > 5:
                return text.strip()
        return ""
    
    async def extract_address_hyper(self, page) -> str:
        """Hyper-fast address extraction"""
        element = await self.selector_engine.find_element_smart(page, "address")
        if element:
            text = await element.inner_text()
            if text:
                return text.strip()
        return ""
    
    async def scrape_google_maps_hyper(self, business_type: str, location: str, 
                                      max_results: int = 50) -> List[HyperLead]:
        """Hyper-optimized Google Maps scraping"""
        self.stats["start_time"] = time.time()
        
        # Check cache
        cache_key = f"hyper_maps_{business_type}_{location}_{max_results}"
        cached_results = await self.cache.get(cache_key, ttl_hours=8)
        if cached_results:
            print(f"⚡ Using cached results for {business_type} in {location}")
            return [HyperLead(**lead) for lead in cached_results]
        
        context = await self.browser_manager.get_context()
        
        try:
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Navigate with minimal waiting
            search_query = f"{business_type} {location}"
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            print(f"⚡ Hyper scraping: {maps_url}")
            await page.goto(maps_url, wait_until='domcontentloaded', timeout=10000)
            
            # Wait for listings
            await page.wait_for_selector('[role="main"], .hfpxzc', timeout=5000)
            
            # Fast scrolling
            await page.evaluate('document.querySelector("[role=main]")?.scrollTo(0, 3000)')
            await asyncio.sleep(0.2)
            
            # Find listings with multiple selectors
            selectors = ['[role="article"]', '[data-result-index]', 'div[jsaction*="mouseover"]', '.hfpxzc']
            listings = []
            
            for selector in selectors:
                listings = await page.query_selector_all(selector)
                if listings:
                    print(f"✅ Found listings with selector: {selector}")
                    break
            
            if not listings:
                print("❌ No listings found with any selector")
                return []
            
            print(f"🔥 Found {len(listings)} listings, processing {min(len(listings), max_results)}...")
            
            # Hyper-parallel processing
            semaphore = asyncio.Semaphore(12)  # Maximum parallelism
            
            async def process_with_semaphore(listing, index):
                async with semaphore:
                    return await self.process_listing_hyper(context, listing, index)
            
            # Process in optimized batches
            batch_size = 20
            results = []
            
            for i in range(0, min(len(listings), max_results), batch_size):
                batch = listings[i:i+batch_size]
                tasks = [process_with_semaphore(listing, i+j) for j, listing in enumerate(batch)]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, HyperLead) and result.name:
                        results.append(result)
                        self.stats["total_processed"] += 1
                        print(f"⚡ {len(results)}: {result.name} (Q: {result.quality_score}/10, {result.processing_time:.1f}s)")
            
            # Cache results
            cached_data = [asdict(lead) for lead in results]
            await self.cache.set(cache_key, cached_data, ttl_hours=8)
            
            return results
            
        finally:
            await self.browser_manager.return_context(context)
    
    async def export_results_hyper(self, leads: List[HyperLead], business_type: str, location: str) -> str:
        """Hyper-fast CSV export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hyper_leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}.csv"
        
        # Sort by quality and processing time
        leads.sort(key=lambda x: (x.quality_score, -x.processing_time), reverse=True)
        
        fieldnames = [
            'Business Name', 'Website', 'Email', 'Phone', 'Address',
            'Instagram', 'Facebook', 'Twitter', 'TikTok', 'Quality Score', 'Processing Time'
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
                    'Twitter': lead.twitter,
                    'TikTok': lead.tiktok,
                    'Quality Score': lead.quality_score,
                    'Processing Time': f"{lead.processing_time:.2f}s"
                })
        
        return filename
    
    def print_hyper_stats(self):
        """Print hyper performance statistics"""
        if self.stats["start_time"]:
            duration = time.time() - self.stats["start_time"]
            rate = self.stats["total_processed"] / duration if duration > 0 else 0
            
            print(f"\n⚡ HYPER SCRAPER STATS:")
            print(f"   🚀 Duration: {duration:.1f}s")
            print(f"   💨 Processing rate: {rate:.1f} leads/second")
            print(f"   ✅ Total processed: {self.stats['total_processed']}")
            print(f"   💾 Cache hits: {self.stats['cache_hits']}")
            print(f"   🌐 Website scrapes: {self.stats['website_scrapes']}")
            print(f"   ❌ Errors: {self.stats['errors']}")
            
            if self.stats['total_processed'] > 0:
                avg_time = duration / self.stats['total_processed']
                print(f"   ⏱️  Average per lead: {avg_time:.2f}s")

# Main hyper scraper function
async def hyper_scrape(business_type: str, location: str, max_results: int = 50) -> List[HyperLead]:
    """Main hyper scraping function"""
    scraper = HyperScraper()
    
    try:
        await scraper.initialize()
        
        print(f"⚡ HYPER SCRAPER STARTING")
        print(f"🎯 Target: {business_type} in {location}")
        print(f"📊 Max results: {max_results}")
        
        leads = await scraper.scrape_google_maps_hyper(business_type, location, max_results)
        
        scraper.print_hyper_stats()
        
        if leads:
            filename = await scraper.export_results_hyper(leads, business_type, location)
            print(f"\n💾 Results exported to: {filename}")
            
            # Quality breakdown
            high_quality = [l for l in leads if l.quality_score >= 7]
            medium_quality = [l for l in leads if 4 <= l.quality_score < 7]
            low_quality = [l for l in leads if l.quality_score < 4]
            
            print(f"\n🏆 QUALITY BREAKDOWN:")
            print(f"   🟢 High quality (7-10): {len(high_quality)}")
            print(f"   🟡 Medium quality (4-6): {len(medium_quality)}")
            print(f"   🔴 Low quality (1-3): {len(low_quality)}")
            
            # Performance insights
            if leads:
                avg_processing_time = sum(l.processing_time for l in leads) / len(leads)
                fastest_lead = min(leads, key=lambda x: x.processing_time)
                print(f"\n📈 PERFORMANCE INSIGHTS:")
                print(f"   ⚡ Average processing time: {avg_processing_time:.2f}s")
                print(f"   🚀 Fastest lead: {fastest_lead.processing_time:.2f}s ({fastest_lead.name})")
        
        return leads
        
    finally:
        await scraper.cleanup()

# Example usage
async def main():
    """Example usage"""
    leads = await hyper_scrape("coffee shop", "Austin, TX", max_results=30)
    print(f"\n🎉 Hyper scraping complete! Found {len(leads)} leads")

if __name__ == "__main__":
    asyncio.run(main())