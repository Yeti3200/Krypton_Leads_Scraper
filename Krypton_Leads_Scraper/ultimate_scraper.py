#!/usr/bin/env python3
"""
Ultimate Lead Scraper - Beyond Enterprise Grade
- User-agent rotation with real browser fingerprints
- Proxy rotation support
- Google Places API fallback
- Advanced error handling with exponential backoff
- All previous optimizations + Grok's suggestions
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

# User-Agent rotation system
class UserAgentRotator:
    """Advanced user-agent rotation with real browser fingerprints"""
    
    def __init__(self):
        self.user_agents = [
            # Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            
            # Firefox on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
            
            # Safari on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        ]
        
        self.usage_stats = {}
        self.current_index = 0
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        agent = random.choice(self.user_agents)
        self.usage_stats[agent] = self.usage_stats.get(agent, 0) + 1
        return agent
    
    def get_rotating_user_agent(self) -> str:
        """Get user agent with round-robin rotation"""
        agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        self.usage_stats[agent] = self.usage_stats.get(agent, 0) + 1
        return agent
    
    def get_stats(self) -> Dict:
        """Get usage statistics"""
        return self.usage_stats

# Proxy rotation system
class ProxyRotator:
    """Advanced proxy rotation with health checking"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxies = proxy_list or []
        self.working_proxies = []
        self.failed_proxies = []
        self.current_index = 0
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = 0
    
    def add_proxy(self, proxy: str):
        """Add a proxy to the rotation"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
    
    def add_proxies(self, proxies: List[str]):
        """Add multiple proxies"""
        for proxy in proxies:
            self.add_proxy(proxy)
    
    async def health_check_proxy(self, proxy: str) -> bool:
        """Check if proxy is working"""
        try:
            connector = aiohttp.TCPConnector()
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    'https://httpbin.org/ip',
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True
        except Exception as e:
            logging.debug(f"Proxy {proxy} failed health check: {e}")
        return False
    
    async def refresh_working_proxies(self):
        """Refresh the list of working proxies"""
        if not self.proxies:
            return
        
        current_time = time.time()
        if current_time - self.last_health_check < self.health_check_interval:
            return
        
        print("🔄 Checking proxy health...")
        
        working = []
        failed = []
        
        # Test proxies in parallel
        tasks = [self.health_check_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for proxy, result in zip(self.proxies, results):
            if isinstance(result, bool) and result:
                working.append(proxy)
            else:
                failed.append(proxy)
        
        self.working_proxies = working
        self.failed_proxies = failed
        self.last_health_check = current_time
        
        print(f"✅ {len(working)} working proxies, {len(failed)} failed")
    
    def get_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return proxy

# Google Places API integration
class GooglePlacesAPI:
    """Google Places API fallback integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        self.session = None
        self.usage_stats = {'requests': 0, 'successes': 0, 'errors': 0}
    
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def search_places(self, query: str, location: str = None, radius: int = 5000) -> List[Dict]:
        """Search places using Google Places API"""
        if not self.api_key:
            print("⚠️ Google Places API key not configured")
            return []
        
        await self.initialize()
        
        try:
            # Construct search query
            search_query = f"{query}"
            if location:
                search_query += f" in {location}"
            
            # API request
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                'query': search_query,
                'key': self.api_key,
                'fields': 'place_id,name,formatted_address,formatted_phone_number,website,rating,user_ratings_total'
            }
            
            if location:
                # Try to geocode location first
                geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
                geocode_params = {'address': location, 'key': self.api_key}
                
                async with self.session.get(geocode_url, params=geocode_params) as response:
                    if response.status == 200:
                        geocode_data = await response.json()
                        if geocode_data.get('results'):
                            location_data = geocode_data['results'][0]['geometry']['location']
                            params['location'] = f"{location_data['lat']},{location_data['lng']}"
                            params['radius'] = radius
            
            self.usage_stats['requests'] += 1
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'OK':
                        self.usage_stats['successes'] += 1
                        return self.parse_places_response(data.get('results', []))
                    else:
                        print(f"⚠️ Google Places API error: {data.get('status')}")
                        self.usage_stats['errors'] += 1
                else:
                    print(f"⚠️ Google Places API HTTP error: {response.status}")
                    self.usage_stats['errors'] += 1
        
        except Exception as e:
            print(f"⚠️ Google Places API exception: {e}")
            self.usage_stats['errors'] += 1
        
        return []
    
    def parse_places_response(self, places: List[Dict]) -> List[Dict]:
        """Parse Google Places API response"""
        results = []
        
        for place in places:
            result = {
                'name': place.get('name', ''),
                'address': place.get('formatted_address', ''),
                'phone': place.get('formatted_phone_number', ''),
                'website': place.get('website', ''),
                'rating': place.get('rating', 0),
                'review_count': place.get('user_ratings_total', 0),
                'place_id': place.get('place_id', ''),
                'source': 'google_places_api'
            }
            results.append(result)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get API usage statistics"""
        return self.usage_stats

# Enhanced error handling with exponential backoff
class EnhancedErrorHandler:
    """Advanced error handling with exponential backoff and circuit breaker"""
    
    def __init__(self, max_retries: int = 5, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.error_stats = {}
        self.circuit_breaker = {'failures': 0, 'last_failure': 0, 'threshold': 10}
    
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Check circuit breaker
                if self.is_circuit_open():
                    raise Exception("Circuit breaker is open - too many failures")
                
                result = await func(*args, **kwargs)
                
                # Reset circuit breaker on success
                self.circuit_breaker['failures'] = 0
                return result
                
            except Exception as e:
                last_exception = e
                error_type = type(e).__name__
                self.error_stats[error_type] = self.error_stats.get(error_type, 0) + 1
                
                # Update circuit breaker
                self.circuit_breaker['failures'] += 1
                self.circuit_breaker['last_failure'] = time.time()
                
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"❌ All {self.max_retries} attempts failed")
        
        raise last_exception
    
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.circuit_breaker['failures'] >= self.circuit_breaker['threshold']:
            # Check if enough time has passed to try again
            if time.time() - self.circuit_breaker['last_failure'] > 300:  # 5 minutes
                self.circuit_breaker['failures'] = 0
                return False
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get error statistics"""
        return {
            'error_stats': self.error_stats,
            'circuit_breaker': self.circuit_breaker
        }

# Ultimate browser manager with all features
class UltimateBrowserManager:
    """Ultimate browser management with all optimizations"""
    
    def __init__(self, pool_size: int = 8):
        self.pool_size = pool_size
        self.browsers = []
        self.contexts = []
        self.context_queue = asyncio.Queue()
        self.playwright = None
        self.initialized = False
        self.user_agent_rotator = UserAgentRotator()
        self.proxy_rotator = ProxyRotator()
        self.error_handler = EnhancedErrorHandler()
        self.usage_stats = {}
    
    def add_proxies(self, proxies: List[str]):
        """Add proxies to rotation"""
        self.proxy_rotator.add_proxies(proxies)
    
    async def initialize(self):
        """Initialize browser pool with all optimizations"""
        if self.initialized:
            return
        
        # Refresh proxy list
        await self.proxy_rotator.refresh_working_proxies()
        
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
            '--disable-domain-reliability', '--disable-background-tasks',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage', '--disable-features=VizDisplayCompositor'
        ]
        
        # Create browser pool
        for i in range(self.pool_size):
            # Get proxy if available
            proxy = self.proxy_rotator.get_proxy()
            proxy_config = {'server': proxy} if proxy else None
            
            browser = await self.playwright.chromium.launch(
                headless=True,
                args=launch_args,
                proxy=proxy_config
            )
            
            # Get rotating user agent
            user_agent = self.user_agent_rotator.get_rotating_user_agent()
            
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1024, 'height': 768},
                java_script_enabled=True,
                ignore_https_errors=True,
                bypass_csp=True,
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            self.browsers.append(browser)
            self.contexts.append(context)
            await self.context_queue.put(context)
            self.usage_stats[f'context_{i}'] = {'used': 0, 'errors': 0, 'user_agent': user_agent, 'proxy': proxy}
        
        self.initialized = True
        print(f"🚀 Ultimate browser pool initialized with {self.pool_size} contexts")
        print(f"🔄 Using {len(self.proxy_rotator.working_proxies)} proxies")
    
    async def get_context(self):
        """Get available browser context"""
        return await self.context_queue.get()
    
    async def return_context(self, context):
        """Return browser context to pool after cleanup"""
        # Enhanced cleanup
        pages = context.pages
        for page in pages[1:]:
            try:
                await page.close()
            except:
                pass
        
        # Clear storage and cookies
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
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        return {
            'usage_stats': self.usage_stats,
            'user_agent_stats': self.user_agent_rotator.get_stats(),
            'proxy_stats': {
                'working_proxies': len(self.proxy_rotator.working_proxies),
                'failed_proxies': len(self.proxy_rotator.failed_proxies)
            },
            'error_stats': self.error_handler.get_stats()
        }

# Enhanced Lead data structure
@dataclass
class UltimateLead:
    """Ultimate lead data structure with all fields"""
    name: str = ""
    website: str = ""
    phone: str = ""
    address: str = ""
    email: str = ""
    instagram: str = ""
    facebook: str = ""
    tiktok: str = ""
    twitter: str = ""
    rating: float = 0.0
    review_count: int = 0
    place_id: str = ""
    source: str = "scraping"
    quality_score: int = 0
    processing_time: float = 0.0
    
    def calculate_quality(self):
        """Enhanced quality calculation"""
        score = 0
        if self.name: score += 2
        if self.website: score += 3
        if self.phone: score += 2
        if self.email: score += 3
        if self.address: score += 1
        if self.rating > 0: score += 1
        if self.review_count > 0: score += 1
        if any([self.instagram, self.facebook, self.twitter]): score += 1
        self.quality_score = min(score, 10)

# Main Ultimate Scraper class
class UltimateScraper:
    """Ultimate scraper with all enterprise features"""
    
    def __init__(self, proxies: List[str] = None, google_api_key: str = None):
        self.browser_manager = UltimateBrowserManager(pool_size=10)
        self.google_places = GooglePlacesAPI(google_api_key)
        self.error_handler = EnhancedErrorHandler()
        
        # Add proxies if provided
        if proxies:
            self.browser_manager.add_proxies(proxies)
        
        # Initialize caching (SQLite)
        self.cache_db = "ultimate_cache.db"
        self.init_cache_db()
        
        # HTTP session for website scraping
        self.session = None
        
        # Statistics
        self.stats = {
            "total_processed": 0,
            "cache_hits": 0,
            "api_fallbacks": 0,
            "scraping_successes": 0,
            "errors": 0,
            "start_time": None,
            "website_scrapes": 0
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def init_cache_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT,
                location TEXT,
                data TEXT,
                timestamp REAL,
                source TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    async def initialize(self):
        """Initialize all systems"""
        await self.browser_manager.initialize()
        await self.google_places.initialize()
        
        # Ultra-optimized HTTP session
        connector = aiohttp.TCPConnector(
            limit=300,
            limit_per_host=100,
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
                'Connection': 'keep-alive'
            }
        )
    
    async def cleanup(self):
        """Cleanup all resources"""
        if self.session:
            await self.session.close()
        await self.browser_manager.cleanup()
        await self.google_places.cleanup()
    
    def get_cache_key(self, business_type: str, location: str, max_results: int) -> str:
        """Generate cache key"""
        query_str = f"{business_type}_{location}_{max_results}"
        return hashlib.md5(query_str.encode()).hexdigest()
    
    async def get_cached_results(self, business_type: str, location: str, max_results: int) -> Optional[List[UltimateLead]]:
        """Get cached results"""
        cache_key = self.get_cache_key(business_type, location, max_results)
        
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT data, timestamp FROM leads_cache WHERE query_hash = ?',
            (cache_key,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data, timestamp = row
            # Check if cache is still valid (6 hours)
            if time.time() - timestamp < 21600:
                try:
                    leads_data = json.loads(data)
                    return [UltimateLead(**lead) for lead in leads_data]
                except:
                    pass
        
        return None
    
    async def cache_results(self, business_type: str, location: str, max_results: int, 
                           leads: List[UltimateLead], source: str = "scraping"):
        """Cache results"""
        cache_key = self.get_cache_key(business_type, location, max_results)
        leads_data = [asdict(lead) for lead in leads]
        
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO leads_cache 
            (query_hash, query, location, data, timestamp, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cache_key, business_type, location, json.dumps(leads_data), time.time(), source))
        conn.commit()
        conn.close()
    
    async def scrape_with_fallback(self, business_type: str, location: str, 
                                  max_results: int = 50) -> List[UltimateLead]:
        """Scrape with Google Places API fallback"""
        self.stats["start_time"] = time.time()
        
        # Check cache first
        cached_results = await self.get_cached_results(business_type, location, max_results)
        if cached_results:
            print(f"📋 Using cached results for {business_type} in {location}")
            self.stats["cache_hits"] += 1
            return cached_results
        
        # Try scraping first
        try:
            print(f"🔍 Attempting scraping for {business_type} in {location}")
            leads = await self.scrape_google_maps_ultimate(business_type, location, max_results)
            
            if leads and len(leads) >= max_results * 0.5:  # If we got at least 50% of requested results
                print(f"✅ Scraping successful: {len(leads)} leads")
                self.stats["scraping_successes"] += 1
                await self.cache_results(business_type, location, max_results, leads, "scraping")
                return leads
            else:
                print(f"⚠️ Scraping returned few results ({len(leads)}), trying API fallback...")
                
        except Exception as e:
            print(f"⚠️ Scraping failed: {e}, trying API fallback...")
            self.stats["errors"] += 1
        
        # Fallback to Google Places API
        try:
            print(f"🔄 Using Google Places API fallback...")
            api_results = await self.google_places.search_places(business_type, location)
            
            if api_results:
                # Convert API results to UltimateLead objects
                leads = []
                for result in api_results[:max_results]:
                    lead = UltimateLead(
                        name=result.get('name', ''),
                        address=result.get('address', ''),
                        phone=result.get('phone', ''),
                        website=result.get('website', ''),
                        rating=result.get('rating', 0),
                        review_count=result.get('review_count', 0),
                        place_id=result.get('place_id', ''),
                        source="google_places_api"
                    )
                    lead.calculate_quality()
                    leads.append(lead)
                
                print(f"✅ API fallback successful: {len(leads)} leads")
                self.stats["api_fallbacks"] += 1
                await self.cache_results(business_type, location, max_results, leads, "api")
                return leads
            
        except Exception as e:
            print(f"❌ API fallback also failed: {e}")
            self.stats["errors"] += 1
        
        # If both fail, return empty list
        print("❌ Both scraping and API fallback failed")
        return []
    
    async def scrape_google_maps_ultimate(self, business_type: str, location: str, 
                                         max_results: int = 50) -> List[UltimateLead]:
        """Ultimate Google Maps scraping with all optimizations"""
        
        async def scrape_attempt():
            context = await self.browser_manager.get_context()
            
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                
                # Navigate
                search_query = f"{business_type} {location}"
                maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
                
                await page.goto(maps_url, wait_until='domcontentloaded', timeout=15000)
                
                # Wait for listings
                await page.wait_for_selector('[role="main"], .hfpxzc', timeout=8000)
                
                # Scroll to load more results
                await page.evaluate('document.querySelector("[role=main]")?.scrollTo(0, 3000)')
                await asyncio.sleep(0.3)
                
                # Find listings
                selectors = ['[role="article"]', '[data-result-index]', 'div[jsaction*="mouseover"]', '.hfpxzc']
                listings = []
                
                for selector in selectors:
                    listings = await page.query_selector_all(selector)
                    if listings:
                        break
                
                if not listings:
                    raise Exception("No listings found")
                
                # Process listings with ultra-high concurrency
                semaphore = asyncio.Semaphore(15)
                
                async def process_with_semaphore(listing, index):
                    async with semaphore:
                        return await self.process_listing_ultimate(context, listing, index)
                
                # Process in batches
                batch_size = 25
                results = []
                
                for i in range(0, min(len(listings), max_results), batch_size):
                    batch = listings[i:i+batch_size]
                    tasks = [process_with_semaphore(listing, i+j) for j, listing in enumerate(batch)]
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in batch_results:
                        if isinstance(result, UltimateLead) and result.name:
                            results.append(result)
                            self.stats["total_processed"] += 1
                
                return results
                
            finally:
                await self.browser_manager.return_context(context)
        
        # Use error handler with retry
        return await self.error_handler.execute_with_retry(scrape_attempt)
    
    async def process_listing_ultimate(self, context, listing, index: int) -> Optional[UltimateLead]:
        """Process listing with all optimizations"""
        start_time = time.time()
        
        try:
            page = await context.new_page()
            lead = UltimateLead()
            
            # Extract name from listing
            name_selectors = ['.qBF1Pd', '.NrDZNb', '.fontHeadlineSmall']
            for selector in name_selectors:
                name_element = await listing.query_selector(selector)
                if name_element:
                    lead.name = (await name_element.inner_text()).strip()
                    break
            
            if not lead.name:
                await page.close()
                return None
            
            # Click for details
            try:
                await listing.scroll_into_view_if_needed(timeout=1000)
                await listing.click(timeout=2000)
                await asyncio.sleep(0.3)
                
                # Extract all details in parallel
                tasks = [
                    self.extract_website_ultimate(page),
                    self.extract_phone_ultimate(page),
                    self.extract_address_ultimate(page),
                    self.extract_rating_ultimate(page)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                lead.website = results[0] if isinstance(results[0], str) else ""
                lead.phone = results[1] if isinstance(results[1], str) else ""
                lead.address = results[2] if isinstance(results[2], str) else ""
                
                if isinstance(results[3], dict):
                    lead.rating = results[3].get('rating', 0)
                    lead.review_count = results[3].get('review_count', 0)
                
            except Exception as e:
                self.logger.warning(f"Detail extraction failed: {e}")
            
            await page.close()
            
            # Website scraping if available
            if lead.website:
                website_data = await self.scrape_website_ultimate(lead.website)
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
            return None
    
    async def extract_website_ultimate(self, page) -> str:
        """Extract website with multiple selectors"""
        selectors = [
            'a[href*="http"]:has-text("Website")',
            '[data-value="Website"] a',
            'a[data-item-id*="authority"]',
            'a[href*="http"]:not([href*="google"]):not([href*="maps"])'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    href = await element.get_attribute('href')
                    if href and 'google' not in href and 'maps' not in href:
                        return href
            except:
                continue
        return ""
    
    async def extract_phone_ultimate(self, page) -> str:
        """Extract phone with multiple selectors"""
        selectors = [
            'button[data-item-id*="phone"]',
            '[data-value*="phone"] span',
            'button:has-text("Call")',
            '.z5jxId'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text and len(text.strip()) > 5:
                        return text.strip()
            except:
                continue
        return ""
    
    async def extract_address_ultimate(self, page) -> str:
        """Extract address with multiple selectors"""
        selectors = [
            'button[data-item-id="address"]',
            '[data-value="Address"] div',
            'button:has-text("Directions")',
            '.rogA2c'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text:
                        return text.strip()
            except:
                continue
        return ""
    
    async def extract_rating_ultimate(self, page) -> Dict:
        """Extract rating and review count"""
        try:
            # Try to find rating
            rating_element = await page.query_selector('[data-value="Rating"] span')
            if rating_element:
                rating_text = await rating_element.inner_text()
                rating = float(rating_text.split()[0]) if rating_text else 0
            else:
                rating = 0
            
            # Try to find review count
            review_element = await page.query_selector('[data-value="Reviews"] span')
            if review_element:
                review_text = await review_element.inner_text()
                review_count = int(re.search(r'(\d+)', review_text).group(1)) if review_text else 0
            else:
                review_count = 0
            
            return {'rating': rating, 'review_count': review_count}
            
        except Exception as e:
            return {'rating': 0, 'review_count': 0}
    
    async def scrape_website_ultimate(self, url: str) -> Dict[str, str]:
        """Ultimate website scraping with user-agent rotation"""
        if not url:
            return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
        
        try:
            # Use rotating user agent
            user_agent = self.browser_manager.user_agent_rotator.get_random_user_agent()
            headers = {'User-Agent': user_agent}
            
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
                
                # Read only first 15KB for speed
                content = await response.content.read(15000)
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
                
                self.stats["website_scrapes"] += 1
                return result
                
        except Exception as e:
            self.logger.warning(f"Website scrape failed {url}: {e}")
            return {"email": "", "instagram": "", "facebook": "", "twitter": "", "tiktok": ""}
    
    async def export_results_ultimate(self, leads: List[UltimateLead], business_type: str, location: str) -> str:
        """Export results with enhanced CSV format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ultimate_leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}.csv"
        
        # Sort by quality and rating
        leads.sort(key=lambda x: (x.quality_score, x.rating), reverse=True)
        
        fieldnames = [
            'Business Name', 'Website', 'Email', 'Phone', 'Address',
            'Instagram', 'Facebook', 'Twitter', 'TikTok', 
            'Rating', 'Review Count', 'Quality Score', 'Source', 'Processing Time'
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
                    'Rating': lead.rating,
                    'Review Count': lead.review_count,
                    'Quality Score': lead.quality_score,
                    'Source': lead.source,
                    'Processing Time': f"{lead.processing_time:.2f}s"
                })
        
        return filename
    
    def print_ultimate_stats(self):
        """Print comprehensive statistics"""
        if self.stats["start_time"]:
            duration = time.time() - self.stats["start_time"]
            rate = self.stats["total_processed"] / duration if duration > 0 else 0
            
            print(f"\n🚀 ULTIMATE SCRAPER STATS:")
            print(f"   ⏱️  Duration: {duration:.1f}s")
            print(f"   💨 Processing rate: {rate:.1f} leads/second")
            print(f"   ✅ Total processed: {self.stats['total_processed']}")
            print(f"   📋 Cache hits: {self.stats['cache_hits']}")
            print(f"   🔄 API fallbacks: {self.stats['api_fallbacks']}")
            print(f"   🎯 Scraping successes: {self.stats['scraping_successes']}")
            print(f"   🌐 Website scrapes: {self.stats['website_scrapes']}")
            print(f"   ❌ Errors: {self.stats['errors']}")
            
            # Browser stats
            browser_stats = self.browser_manager.get_stats()
            print(f"   🔄 User agents used: {len(browser_stats['user_agent_stats'])}")
            print(f"   🌍 Working proxies: {browser_stats['proxy_stats']['working_proxies']}")
            
            # API stats
            api_stats = self.google_places.get_stats()
            print(f"   🔗 API requests: {api_stats['requests']}")
            print(f"   ✅ API successes: {api_stats['successes']}")

# Main ultimate scraper function
async def ultimate_scrape(business_type: str, location: str, max_results: int = 50,
                         proxies: List[str] = None, google_api_key: str = None) -> List[UltimateLead]:
    """Ultimate scraping function with all features"""
    scraper = UltimateScraper(proxies=proxies, google_api_key=google_api_key)
    
    try:
        await scraper.initialize()
        
        print(f"🚀 ULTIMATE SCRAPER STARTING")
        print(f"🎯 Target: {business_type} in {location}")
        print(f"📊 Max results: {max_results}")
        print(f"🔄 Features: User-agent rotation, Proxy support, API fallback, Advanced caching")
        
        leads = await scraper.scrape_with_fallback(business_type, location, max_results)
        
        scraper.print_ultimate_stats()
        
        if leads:
            filename = await scraper.export_results_ultimate(leads, business_type, location)
            print(f"\n💾 Results exported to: {filename}")
            
            # Quality breakdown
            high_quality = [l for l in leads if l.quality_score >= 7]
            medium_quality = [l for l in leads if 4 <= l.quality_score < 7]
            low_quality = [l for l in leads if l.quality_score < 4]
            
            print(f"\n🏆 QUALITY BREAKDOWN:")
            print(f"   🟢 High quality (7-10): {len(high_quality)}")
            print(f"   🟡 Medium quality (4-6): {len(medium_quality)}")
            print(f"   🔴 Low quality (1-3): {len(low_quality)}")
            
            # Source breakdown
            scraping_leads = [l for l in leads if l.source == "scraping"]
            api_leads = [l for l in leads if l.source == "google_places_api"]
            
            print(f"\n📊 SOURCE BREAKDOWN:")
            print(f"   🔍 From scraping: {len(scraping_leads)}")
            print(f"   🔗 From API: {len(api_leads)}")
        
        return leads
        
    finally:
        await scraper.cleanup()

# Example usage
async def main():
    """Example usage with all features"""
    # Example proxies (replace with real ones)
    proxies = [
        # "http://proxy1:port",
        # "http://proxy2:port",
    ]
    
    # Set your Google Places API key
    google_api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    
    leads = await ultimate_scrape(
        "coffee shop", 
        "Austin, TX", 
        max_results=20,
        proxies=proxies,
        google_api_key=google_api_key
    )
    
    print(f"\n🎉 Ultimate scraping complete! Found {len(leads)} leads")

if __name__ == "__main__":
    asyncio.run(main())