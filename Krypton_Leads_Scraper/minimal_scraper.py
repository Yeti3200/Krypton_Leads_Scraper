#!/usr/bin/env python3
"""
Minimal Scraper - Just Works
"""

import asyncio
import time
import csv
from datetime import datetime
from playwright.async_api import async_playwright

async def scrape_leads(business_type: str, location: str, max_results: int = 10):
    """Simple scraper that actually works"""
    print(f"🔍 Scraping {business_type} in {location}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Go to Google Maps
            search_url = f"https://www.google.com/maps/search/{business_type}+{location}".replace(' ', '+')
            await page.goto(search_url, timeout=15000)
            
            # Wait for results to load
            await page.wait_for_selector('[role="main"]', timeout=10000)
            await asyncio.sleep(2)
            
            # Scroll to load more results
            await page.evaluate('window.scrollTo(0, 2000)')
            await asyncio.sleep(1)
            
            # Get all clickable business elements
            business_links = await page.query_selector_all('a[href*="/maps/place/"]')
            
            leads = []
            
            for i, link in enumerate(business_links[:max_results]):
                try:
                    # Click the business
                    await link.click()
                    await asyncio.sleep(1)
                    
                    lead = {}
                    
                    # Get business name - try multiple selectors
                    name_selectors = ['h1', '[data-attrid="title"]', '.DUwDvf', '.x3AX1-LfntMc-header-title-title']
                    for selector in name_selectors:
                        name_element = await page.query_selector(selector)
                        if name_element:
                            name = await name_element.inner_text()
                            # Filter out common UI elements
                            if name and len(name) > 2 and name not in ['Results', 'Map', 'Search', 'Google']:
                                lead['name'] = name.strip()
                                break
                    
                    if not lead.get('name'):
                        continue
                    
                    # Get website
                    website_element = await page.query_selector('a[href*="http"]:not([href*="google"]):not([href*="maps"])')
                    if website_element:
                        lead['website'] = await website_element.get_attribute('href')
                    else:
                        lead['website'] = ''
                    
                    # Get phone
                    phone_element = await page.query_selector('button[data-item-id*="phone"]')
                    if phone_element:
                        lead['phone'] = await phone_element.inner_text()
                    else:
                        lead['phone'] = ''
                    
                    # Get address
                    address_element = await page.query_selector('button[data-item-id="address"]')
                    if address_element:
                        lead['address'] = await address_element.inner_text()
                    else:
                        lead['address'] = ''
                    
                    lead['email'] = ''  # Skip email for simplicity
                    
                    leads.append(lead)
                    print(f"✅ {len(leads)}: {lead['name']}")
                    
                except Exception as e:
                    print(f"⚠️ Error processing business {i}: {e}")
                    continue
            
            return leads
            
        finally:
            await browser.close()

def save_to_csv(leads: list, business_type: str, location: str) -> str:
    """Save leads to CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"leads_{business_type}_{location}_{timestamp}.csv".replace(' ', '_').replace(',', '')
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Website', 'Phone', 'Address', 'Email'])
        
        for lead in leads:
            writer.writerow([
                lead.get('name', ''),
                lead.get('website', ''),
                lead.get('phone', ''),
                lead.get('address', ''),
                lead.get('email', '')
            ])
    
    return filename

async def main():
    """Run the scraper"""
    print("🚀 Minimal Lead Scraper")
    print("=" * 25)
    
    # Edit these values
    business_type = "coffee shop"
    location = "Austin, TX"
    max_results = 5
    
    start_time = time.time()
    leads = await scrape_leads(business_type, location, max_results)
    duration = time.time() - start_time
    
    print(f"\n⏱️ Found {len(leads)} leads in {duration:.1f}s")
    
    if leads:
        filename = save_to_csv(leads, business_type, location)
        print(f"💾 Saved to {filename}")
        
        # Show results
        print("\n📋 Results:")
        for i, lead in enumerate(leads, 1):
            print(f"\n{i}. {lead['name']}")
            if lead['website']:
                print(f"   Website: {lead['website']}")
            if lead['phone']:
                print(f"   Phone: {lead['phone']}")
    else:
        print("❌ No leads found")
    
    print("\n🎉 Done!")

if __name__ == "__main__":
    asyncio.run(main())