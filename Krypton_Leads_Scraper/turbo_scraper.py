#!/usr/bin/env python3
"""
Turbo Lead Scraper - Maximum Efficiency Implementation
- Browser instance reuse
- Intelligent caching
- Parallel processing
- Memory optimizations
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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging

# Browser pool for reuse
class BrowserPool:
    """Manages a pool of reusable browser instances"""
    
    def __init__(self, pool_size: int = 3):
        self.pool_size = pool_size
        self.browsers = []
        self.contexts = []
        self.available_contexts = asyncio.Queue()
        self.playwright = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize browser pool"""
        if self.initialized:
            return
            
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().__aenter__()
        
        # Create browser pool
        for i in range(self.pool_size):
            browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox', '--disable-dev-shm-usage', '--disable-images',
                    '--disable-gpu', '--disable-extensions', '--disable-plugins',
                    '--disable-web-security', '--disable-features=TranslateUI',
                    '--memory-pressure-off', '--max_old_space_size=2048',
                    '--aggressive-cache-discard', '--disable-background-networking'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                java_script_enabled=True,
                ignore_https_errors=True,
                bypass_csp=True
            )
            
            self.browsers.append(browser)
            self.contexts.append(context)
            await self.available_contexts.put(context)
        
        self.initialized = True
        print(f"🚀 Initialized {self.pool_size} browser instances")
    
    async def get_context(self):
        """Get available browser context"""
        return await self.available_contexts.get()
    
    async def return_context(self, context):
        """Return browser context to pool"""
        # Clear any existing pages except one
        pages = context.pages
        for page in pages[1:]:  # Keep first page, close others
            try:
                await page.close()
            except:
                pass
        await self.available_contexts.put(context)
    
    async def cleanup(self):
        """Cleanup browser pool"""
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

# Intelligent caching system
class SmartCache:
    """Advanced caching with expiration and intelligent invalidation"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0}
    
    def _get_cache_key(self, data: str) -> str:
        """Generate cache key from data"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{key}.cache"
    
    def _is_expired(self, cache_path: Path, ttl_hours: int = 24) -> bool:
        """Check if cache is expired"""
        if not cache_path.exists():
            return True
        
        file_age = time.time() - cache_path.stat().st_mtime
        return file_age > (ttl_hours * 3600)
    
    async def get(self, key: str, ttl_hours: int = 24) -> Optional[Dict]:
        """Get cached data"""
        # Check memory cache first
        if key in self.memory_cache:
            self.cache_stats["hits"] += 1
            return self.memory_cache[key]
        
        # Check disk cache
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        if not self._is_expired(cache_path, ttl_hours):
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                    self.memory_cache[key] = data  # Store in memory for faster access
                    self.cache_stats["hits"] += 1
                    return data
            except:
                pass
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set(self, key: str, data: Dict):
        """Set cached data"""
        # Store in memory
        self.memory_cache[key] = data
        
        # Store on disk
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"⚠️ Cache write failed: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total * 100) if total > 0 else 0
        return {
            **self.cache_stats,
            "hit_rate": f"{hit_rate:.1f}%",
            "memory_items": len(self.memory_cache)
        }

# Optimized selectors with failover chains
class SelectorEngine:
    """Pre-compiled selectors with intelligent failover"""
    
    def __init__(self):
        self.selector_chains = {
            "business_listings": [
                '[role="article"]',
                '[data-result-index]',
                'div[jsaction*="mouseover"]',
                '.hfpxzc',
                '.Nv2PK',
                'div[data-feature-id]'
            ],
            "business_name": [
                '.qBF1Pd',
                '.NrDZNb',
                '.fontHeadlineSmall',
                '.hfpxzc .fontHeadlineSmall',
                'h1[data-attrid="title"]'
            ],
            "website": [
                'a[href*="http"]:has-text("Website")',
                '[data-value="Website"] a',
                'a[data-item-id*="authority"]',
                'a[href*="http"]:not([href*="google"]):not([href*="maps"])'
            ],
            "phone": [
                'button[data-item-id*="phone"]',
                '[data-value*="phone"] span',
                'button:has-text("Call")',
                '.z5jxId'
            ],
            "address": [
                'button[data-item-id="address"]',
                '[data-value="Address"] div',
                'button:has-text("Directions")',
                '.rogA2c'
            ]
        }
        self.selector_performance = {}
    
    async def find_element_fast(self, page, selector_type: str, timeout: int = 3000):
        """Find element using optimized selector chain"""
        selectors = self.selector_chains.get(selector_type, [])
        
        # Try selectors in order of performance
        if selector_type in self.selector_performance:
            # Sort by success rate
            selectors = sorted(selectors, 
                             key=lambda s: self.selector_performance[selector_type].get(s, 0), 
                             reverse=True)
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    # Update performance stats
                    if selector_type not in self.selector_performance:
                        self.selector_performance[selector_type] = {}
                    self.selector_performance[selector_type][selector] = \
                        self.selector_performance[selector_type].get(selector, 0) + 1
                    return element
            except:
                continue
        
        return None
    
    async def find_elements_fast(self, page, selector_type: str):
        """Find multiple elements using optimized selectors"""
        selectors = self.selector_chains.get(selector_type, [])
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    return elements
            except:
                continue
        
        return []

@dataclass
class TurboLead:
    """Optimized lead data structure"""
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
    
    def calculate_quality(self):
        """Fast quality calculation"""
        score = 0
        if self.name: score += 2
        if self.website: score += 2
        if self.phone: score += 2
        if self.email: score += 2
        if self.address: score += 1
        if self.instagram or self.facebook or self.twitter: score += 1
        self.quality_score = min(score, 10)

class TurboScraper:
    """Maximum efficiency scraper with all optimizations"""
    
    def __init__(self):
        self.browser_pool = BrowserPool(pool_size=5)
        self.cache = SmartCache()
        self.selector_engine = SelectorEngine()
        self.session = None
        self.results = []
        self.stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "errors": 0,
            "start_time": None
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize all systems"""
        await self.browser_pool.initialize()
        
        # Create optimized HTTP session
        connector = aiohttp.TCPConnector(
            limit=150,
            limit_per_host=50,
            ttl_dns_cache=900,
            use_dns_cache=True,
            keepalive_timeout=90,
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=5, connect=2),
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
        )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
        await self.browser_pool.cleanup()
    
    def get_user_agents(self) -> List[str]:
        """Get rotating user agents"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    async def extract_social_links_fast(self, html: str) -> Dict[str, str]:
        """Fast social media extraction"""
        patterns = {
            'instagram': r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+',
            'facebook': r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_.]+',
            'twitter': r'https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+',
            'tiktok': r'https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.]+',
        }
        
        results = {}
        for platform, pattern in patterns.items():
            match = re.search(pattern, html, re.IGNORECASE)
            results[platform] = match.group(0) if match else ""
            if platform == 'twitter' and results[platform]:
                results[platform] = results[platform].replace('twitter.com', 'x.com')
        
        return results
    
    async def scrape_website_turbo(self, url: str) -> Dict[str, str]:
        """Turbo website scraping with caching"""
        if not url:
            return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
        
        # Check cache first
        cache_key = f"website_{url}"
        cached = await self.cache.get(cache_key, ttl_hours=48)
        if cached:
            self.stats["cache_hits"] += 1
            return cached
        
        try:
            headers = {'User-Agent': random.choice(self.get_user_agents())}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
                
                # Read only first 30KB for speed
                content = await response.content.read(30000)
                html = content.decode('utf-8', errors='ignore')
                
                # Fast email extraction
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', html)
                email = email_match.group(0) if email_match else ""
                
                # Fast social media extraction
                social = await self.extract_social_links_fast(html)
                
                result = {
                    "email": email,
                    "instagram": social.get("instagram", ""),
                    "facebook": social.get("facebook", ""),
                    "twitter": social.get("twitter", ""),
                    "tiktok": social.get("tiktok", "")
                }
                
                # Cache result
                await self.cache.set(cache_key, result)
                return result
                
        except Exception as e:
            self.logger.warning(f"Website scrape failed {url}: {e}")
            return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
    
    async def process_listing_turbo(self, context, listing, index: int) -> Optional[TurboLead]:
        """Process individual listing with maximum efficiency"""
        try:
            page = await context.new_page()
            
            lead = TurboLead()
            
            # Extract name from listing card (fast)
            name_element = await self.selector_engine.find_element_fast(listing, "business_name")
            if name_element:
                lead.name = (await name_element.inner_text()).strip()
            
            if not lead.name:
                await page.close()
                return None
            
            # Click for details (with timeout)
            try:
                await listing.scroll_into_view_if_needed(timeout=1000)
                await listing.click(timeout=2000)
                await asyncio.sleep(0.5)  # Minimal wait
                
                # Extract details in parallel
                tasks = [
                    self.extract_website_fast(page),
                    self.extract_phone_fast(page),
                    self.extract_address_fast(page)
                ]
                
                website, phone, address = await asyncio.gather(*tasks, return_exceptions=True)
                
                lead.website = website if isinstance(website, str) else ""
                lead.phone = phone if isinstance(phone, str) else ""
                lead.address = address if isinstance(address, str) else ""
                
            except Exception as e:
                self.logger.warning(f"Detail extraction failed for {lead.name}: {e}")
            
            await page.close()
            
            # Website scraping in background if we have a website
            if lead.website:
                website_data = await self.scrape_website_turbo(lead.website)
                lead.email = website_data.get("email", "")
                lead.instagram = website_data.get("instagram", "")
                lead.facebook = website_data.get("facebook", "")
                lead.twitter = website_data.get("twitter", "")
                lead.tiktok = website_data.get("tiktok", "")
            
            lead.calculate_quality()
            return lead
            
        except Exception as e:
            self.logger.warning(f"Listing processing failed {index}: {e}")
            self.stats["errors"] += 1
            return None
    
    async def extract_website_fast(self, page) -> str:
        """Fast website extraction"""
        element = await self.selector_engine.find_element_fast(page, "website")
        if element:
            href = await element.get_attribute('href')
            if href and 'google' not in href and 'maps' not in href:
                return href
        return ""
    
    async def extract_phone_fast(self, page) -> str:
        """Fast phone extraction"""
        element = await self.selector_engine.find_element_fast(page, "phone")
        if element:
            text = await element.inner_text()
            if text and len(text.strip()) > 5:
                return text.strip()
        return ""
    
    async def extract_address_fast(self, page) -> str:
        """Fast address extraction"""
        element = await self.selector_engine.find_element_fast(page, "address")
        if element:
            text = await element.inner_text()
            if text:
                return text.strip()
        return ""
    
    async def scrape_google_maps_turbo(self, business_type: str, location: str, 
                                     max_results: int = 25) -> List[TurboLead]:
        """Turbo Google Maps scraping"""
        self.stats["start_time"] = time.time()
        
        # Check cache for this exact search
        cache_key = f"maps_{business_type}_{location}"
        cached_results = await self.cache.get(cache_key, ttl_hours=12)
        if cached_results:
            print(f"📋 Using cached results for {business_type} in {location}")
            return [TurboLead(**lead) for lead in cached_results]
        
        context = await self.browser_pool.get_context()
        
        try:
            page = context.pages[0] if context.pages else await context.new_page()
            
            # Navigate with minimal waiting
            search_query = f"{business_type} {location}"
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            print(f"🔍 Turbo scraping: {maps_url}")
            await page.goto(maps_url, wait_until='domcontentloaded', timeout=15000)
            
            # Wait for listings (optimized)
            await page.wait_for_selector('[role="main"], .hfpxzc', timeout=8000)
            
            # Minimal scrolling for speed
            await page.evaluate('document.querySelector("[role=main]")?.scrollTo(0, 1500)')
            await asyncio.sleep(0.3)
            
            # Find listings fast
            listings = await self.selector_engine.find_elements_fast(page, "business_listings")
            
            if not listings:
                print("❌ No listings found")
                return []
            
            print(f"📍 Found {len(listings)} listings, processing {min(len(listings), max_results)}...")
            
            # Process listings with controlled concurrency
            semaphore = asyncio.Semaphore(8)  # Increased concurrent processing
            
            async def process_with_semaphore(listing, index):
                async with semaphore:
                    return await self.process_listing_turbo(context, listing, index)
            
            # Process in batches for memory efficiency
            batch_size = 15
            results = []
            
            for i in range(0, min(len(listings), max_results), batch_size):
                batch = listings[i:i+batch_size]
                tasks = [process_with_semaphore(listing, i+j) for j, listing in enumerate(batch)]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter successful results
                for result in batch_results:
                    if isinstance(result, TurboLead) and result.name:
                        results.append(result)
                        self.stats["total_processed"] += 1
                        print(f"✅ {len(results)}: {result.name} (Q: {result.quality_score}/10)")
                
                # Yield control and small delay between batches
                await asyncio.sleep(0.1)
            
            # Cache results for future use
            cached_data = [asdict(lead) for lead in results]
            await self.cache.set(cache_key, cached_data)
            
            return results
            
        finally:
            await self.browser_pool.return_context(context)
    
    async def export_results_fast(self, leads: List[TurboLead], business_type: str, location: str) -> str:
        """Fast CSV export with quality metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"turbo_leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}.csv"
        
        # Sort by quality score
        leads.sort(key=lambda x: x.quality_score, reverse=True)
        
        fieldnames = [
            'Business Name', 'Website', 'Email', 'Phone', 'Address',
            'Instagram', 'Facebook', 'Twitter', 'TikTok', 'Quality Score'
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
                    'Quality Score': lead.quality_score
                })
        
        return filename
    
    def print_stats(self):
        """Print performance statistics"""
        if self.stats["start_time"]:
            duration = time.time() - self.stats["start_time"]
            rate = self.stats["total_processed"] / duration if duration > 0 else 0
            
            print(f"\n📊 TURBO SCRAPER STATS:")
            print(f"   ⏱️  Duration: {duration:.1f}s")
            print(f"   🔥 Processing rate: {rate:.1f} leads/second")
            print(f"   ✅ Total processed: {self.stats['total_processed']}")
            print(f"   💾 Cache hits: {self.stats['cache_hits']}")
            print(f"   ❌ Errors: {self.stats['errors']}")
            
            cache_stats = self.cache.get_stats()
            print(f"   📋 Cache hit rate: {cache_stats['hit_rate']}")

# Main scraper function
async def turbo_scrape(business_type: str, location: str, max_results: int = 25) -> List[TurboLead]:
    """Main turbo scraping function"""
    scraper = TurboScraper()
    
    try:
        await scraper.initialize()
        
        print(f"🚀 TURBO SCRAPER STARTING")
        print(f"🎯 Target: {business_type} in {location}")
        print(f"📊 Max results: {max_results}")
        
        leads = await scraper.scrape_google_maps_turbo(business_type, location, max_results)
        
        scraper.print_stats()
        
        if leads:
            filename = await scraper.export_results_fast(leads, business_type, location)
            print(f"\n💾 Results exported to: {filename}")
            
            # Quality breakdown
            high_quality = [l for l in leads if l.quality_score >= 7]
            medium_quality = [l for l in leads if 4 <= l.quality_score < 7]
            low_quality = [l for l in leads if l.quality_score < 4]
            
            print(f"\n🏆 QUALITY BREAKDOWN:")
            print(f"   🟢 High quality (7-10): {len(high_quality)}")
            print(f"   🟡 Medium quality (4-6): {len(medium_quality)}")
            print(f"   🔴 Low quality (1-3): {len(low_quality)}")
        
        return leads
        
    finally:
        await scraper.cleanup()

# Example usage
async def main():
    """Example usage"""
    leads = await turbo_scrape("coffee shop", "Austin, TX", max_results=20)
    print(f"\n🎉 Turbo scraping complete! Found {len(leads)} leads")

if __name__ == "__main__":
    asyncio.run(main())