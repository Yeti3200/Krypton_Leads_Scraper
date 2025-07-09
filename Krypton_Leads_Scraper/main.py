#!/usr/bin/env python3
"""
Krypton Leads Scraper
A comprehensive lead generation tool that scrapes Google Maps and extracts business information
"""

import sys
import subprocess
import importlib
import re
import time
import random
import csv
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

def check_and_install_dependencies():
    """Check if required packages are installed and prompt user to install if missing"""
    required_packages = [
        'playwright',
        'beautifulsoup4', 
        'requests',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                importlib.import_module('bs4')
            else:
                importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        
        print("\n📦 Please install missing packages:")
        print("   pip install " + " ".join(missing_packages))
        print("\n🌐 After installation, run:")
        print("   playwright install")
        print("\nThen restart this script.")
        sys.exit(1)
    
    # Check if playwright browsers are installed
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
            except Exception:
                print("❌ Playwright browsers not installed.")
                print("🌐 Please run: playwright install")
                sys.exit(1)
    except Exception as e:
        print(f"❌ Playwright setup issue: {e}")
        print("🌐 Please run: playwright install")
        sys.exit(1)

def get_user_input():
    """Get business type and location from user or command line arguments"""
    # Check if command line arguments are provided
    if len(sys.argv) >= 3:
        business_type = sys.argv[1].strip()
        location = sys.argv[2].strip()
        
        if not business_type or not location:
            print("❌ Both business type and location are required!")
            sys.exit(1)
        
        print(f"\n🔍 KRYPTON LEADS SCRAPER")
        print("=" * 50)
        print(f"📋 Business Type: {business_type}")
        print(f"📍 Location: {location}")
        
        return business_type, location
    
    # Fall back to manual input if no command line arguments
    print("\n🔍 KRYPTON LEADS SCRAPER")
    print("=" * 50)
    
    business_type = input("Enter business type (e.g., 'med spa', 'restaurant'): ").strip()
    location = input("Enter location (e.g., 'Dallas, TX', 'New York, NY'): ").strip()
    
    if not business_type or not location:
        print("❌ Both business type and location are required!")
        sys.exit(1)
    
    return business_type, location

def get_random_user_agent():
    """Return a random user agent to avoid detection"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    ]
    return random.choice(user_agents)

def scrape_google_maps(business_type, location):
    """Scrape Google Maps for business listings"""
    from playwright.sync_api import sync_playwright
    
    businesses = []
    
    print(f"\n🔍 Searching Google Maps for '{business_type}' in '{location}'...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(
            user_agent=get_random_user_agent(),
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )
        page = context.new_page()
        
        try:
            # Navigate to Google Maps
            search_query = f"{business_type} {location}"
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            page.goto(maps_url, wait_until='domcontentloaded', timeout=60000)
            time.sleep(5)
            
            # Wait for results to load
            try:
                page.wait_for_selector('[role="main"]', timeout=15000)
            except:
                # Try alternative selector if main fails
                page.wait_for_selector('[data-value="Directions"]', timeout=15000)
            
            # Scroll to load more results
            print("📜 Loading more results...")
            for i in range(5):  # Scroll 5 times to load more results
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(2)
            
            # Find all business listings
            listings = page.query_selector_all('[role="article"]')
            
            # Try alternative selectors if no listings found
            if not listings:
                listings = page.query_selector_all('[data-result-index]')
            if not listings:
                listings = page.query_selector_all('div[jsaction*="mouseover"]')
            
            print(f"📍 Found {len(listings)} potential businesses")
            
            for i, listing in enumerate(listings[:20]):  # Limit to first 20 results
                try:
                    print(f"🔍 Processing business {i+1}/20...")
                    
                    # Click on the listing to get details with retry logic
                    clicked = False
                    for attempt in range(2):  # Try up to 2 times
                        try:
                            # Scroll element into view first
                            listing.scroll_into_view_if_needed()
                            time.sleep(0.5)
                            
                            # Try to click
                            listing.click(timeout=10000)
                            time.sleep(2)
                            clicked = True
                            break
                        except Exception as click_error:
                            if attempt == 0:
                                print(f"⚠️ Click attempt {attempt + 1} failed for business {i+1}, retrying...")
                                time.sleep(1)
                            else:
                                print(f"⚠️ Failed to click business {i+1} after {attempt + 1} attempts: {str(click_error)[:100]}...")
                                time.sleep(1)
                    
                    if not clicked:
                        continue
                    
                    # Extract business information
                    business_data = {
                        'name': '',
                        'website': '',
                        'phone': '',
                        'address': '',
                        'email': '',
                        'instagram': '',
                        'facebook': '',
                        'tiktok': ''
                    }
                    
                    # Get business name
                    name_element = page.query_selector('h1')
                    if name_element:
                        business_data['name'] = name_element.inner_text().strip()
                    
                    # Get website
                    website_element = page.query_selector('a[href*="http"]:has-text("Website")')
                    if not website_element:
                        website_element = page.query_selector('[data-value="Website"] a')
                    if website_element:
                        business_data['website'] = website_element.get_attribute('href')
                    
                    # Get phone number
                    phone_element = page.query_selector('button[data-item-id*="phone"]')
                    if not phone_element:
                        phone_element = page.query_selector('[data-value*="phone"] span')
                    if phone_element:
                        business_data['phone'] = phone_element.inner_text().strip()
                    
                    # Get address
                    address_element = page.query_selector('button[data-item-id="address"]')
                    if not address_element:
                        address_element = page.query_selector('[data-value="Address"] div')
                    if address_element:
                        business_data['address'] = address_element.inner_text().strip()
                    
                    if business_data['name']:
                        businesses.append(business_data)
                        print(f"✅ Added: {business_data['name']}")
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"⚠️ Error processing business {i+1}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error scraping Google Maps: {e}")
        
        finally:
            browser.close()
    
    return businesses

def extract_emails_from_text(text):
    """Extract email addresses from text using regex"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Remove duplicates

def extract_social_media_links(text, base_url):
    """Extract social media links from text"""
    social_links = {
        'instagram': '',
        'facebook': '',
        'tiktok': ''
    }
    
    # Instagram patterns
    instagram_patterns = [
        r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+/?',
        r'instagram\.com/[a-zA-Z0-9_.]+/?',
        r'@[a-zA-Z0-9_.]+(?=\s|$)'
    ]
    
    # Facebook patterns
    facebook_patterns = [
        r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9_.]+/?',
        r'facebook\.com/[a-zA-Z0-9_.]+/?'
    ]
    
    # TikTok patterns
    tiktok_patterns = [
        r'https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.]+/?',
        r'tiktok\.com/@[a-zA-Z0-9_.]+/?'
    ]
    
    # Extract Instagram
    for pattern in instagram_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            link = matches[0]
            if not link.startswith('http'):
                if link.startswith('@'):
                    link = f"https://instagram.com/{link[1:]}"
                else:
                    link = f"https://{link}"
            social_links['instagram'] = link
            break
    
    # Extract Facebook
    for pattern in facebook_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            link = matches[0]
            if not link.startswith('http'):
                link = f"https://{link}"
            social_links['facebook'] = link
            break
    
    # Extract TikTok
    for pattern in tiktok_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            link = matches[0]
            if not link.startswith('http'):
                link = f"https://{link}"
            social_links['tiktok'] = link
            break
    
    return social_links

def scrape_website_info(url):
    """Scrape website for email and social media information"""
    import requests
    from bs4 import BeautifulSoup
    
    if not url or not url.startswith('http'):
        return {'email': '', 'instagram': '', 'facebook': '', 'tiktok': ''}
    
    try:
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        # Try to get the main page
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all text content
        text_content = soup.get_text()
        html_content = str(soup)
        
        # Extract emails
        emails = extract_emails_from_text(text_content)
        
        # Extract social media links
        social_links = extract_social_media_links(html_content, url)
        
        # Try to find contact page
        contact_urls = []
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            if any(word in href for word in ['contact', 'about', 'connect']):
                contact_urls.append(urljoin(url, link['href']))
        
        # Scrape contact pages for additional info
        for contact_url in contact_urls[:2]:  # Only check first 2 contact pages
            try:
                time.sleep(1)  # Rate limiting
                contact_response = session.get(contact_url, timeout=10)
                contact_response.raise_for_status()
                
                contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                contact_text = contact_soup.get_text()
                contact_html = str(contact_soup)
                
                # Extract additional emails
                additional_emails = extract_emails_from_text(contact_text)
                emails.extend(additional_emails)
                
                # Extract additional social links
                additional_social = extract_social_media_links(contact_html, contact_url)
                for platform, link in additional_social.items():
                    if link and not social_links[platform]:
                        social_links[platform] = link
                
            except Exception as e:
                print(f"⚠️ Error scraping contact page {contact_url}: {e}")
                continue
        
        # Clean up emails and remove duplicates
        emails = list(set([email.lower() for email in emails if email]))
        
        return {
            'email': emails[0] if emails else '',
            'instagram': social_links['instagram'],
            'facebook': social_links['facebook'],
            'tiktok': social_links['tiktok']
        }
        
    except Exception as e:
        print(f"⚠️ Error scraping website {url}: {e}")
        return {'email': '', 'instagram': '', 'facebook': '', 'tiktok': ''}

def enrich_business_data(businesses):
    """Enrich business data with website information"""
    print(f"\n🌐 Scraping websites for {len(businesses)} businesses...")
    
    for i, business in enumerate(businesses):
        if business['website']:
            print(f"🔍 Scraping website {i+1}/{len(businesses)}: {business['name']}")
            
            website_info = scrape_website_info(business['website'])
            
            business['email'] = website_info['email']
            business['instagram'] = website_info['instagram']
            business['facebook'] = website_info['facebook']
            business['tiktok'] = website_info['tiktok']
            
            # Rate limiting
            time.sleep(random.uniform(1, 3))
        else:
            print(f"⚠️ No website found for: {business['name']}")
    
    return businesses

def save_to_csv(businesses, business_type, location):
    """Save business data to CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}.csv"
    
    # Remove any characters that might cause issues in filename
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    
    fieldnames = ['Business Name', 'Website', 'Email', 'Phone', 'Address', 'Instagram', 'Facebook', 'TikTok']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for business in businesses:
            writer.writerow({
                'Business Name': business['name'],
                'Website': business['website'],
                'Email': business['email'],
                'Phone': business['phone'],
                'Address': business['address'],
                'Instagram': business['instagram'],
                'Facebook': business['facebook'],
                'TikTok': business['tiktok']
            })
    
    return filename

def save_to_google_sheets(businesses, business_type, location, credentials_file=None):
    """Save business data to Google Sheets"""
    if not GOOGLE_SHEETS_AVAILABLE:
        print("❌ Google Sheets libraries not installed. Please install: pip install gspread google-auth")
        return None
    
    try:
        # Set up credentials
        if credentials_file and os.path.exists(credentials_file):
            # Use service account credentials
            scope = ['https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
        else:
            # Try to use default credentials or OAuth
            try:
                import gspread
                gc = gspread.oauth()
            except Exception as e:
                print(f"❌ Google Sheets authentication failed: {e}")
                print("📋 Please set up Google Sheets authentication:")
                print("   1. Go to https://console.cloud.google.com/")
                print("   2. Create a new project or select existing")
                print("   3. Enable Google Sheets API")
                print("   4. Create credentials (OAuth 2.0 or Service Account)")
                print("   5. Download the credentials file")
                return None
        
        if credentials_file and os.path.exists(credentials_file):
            gc = gspread.authorize(creds)
        
        # Create spreadsheet name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_name = f"Leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}"
        
        # Create new spreadsheet
        print(f"📊 Creating Google Sheet: {sheet_name}")
        spreadsheet = gc.create(sheet_name)
        
        # Get the first worksheet
        worksheet = spreadsheet.sheet1
        
        # Prepare data
        headers = ['Business Name', 'Website', 'Email', 'Phone', 'Address', 'Instagram', 'Facebook', 'TikTok']
        data = [headers]
        
        for business in businesses:
            row = [
                business['name'],
                business['website'],
                business['email'],
                business['phone'],
                business['address'],
                business['instagram'],
                business['facebook'],
                business['tiktok']
            ]
            data.append(row)
        
        # Update the worksheet
        worksheet.update('A1', data)
        
        # Make the spreadsheet shareable
        spreadsheet.share('', perm_type='anyone', role='reader')
        
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        print(f"✅ Google Sheet created successfully!")
        print(f"🔗 Sheet URL: {sheet_url}")
        
        return sheet_url
        
    except Exception as e:
        print(f"❌ Error creating Google Sheet: {e}")
        return None

def main():
    """Main function to run the scraper"""
    print("🚀 Starting Krypton Leads Scraper...")
    
    # Check dependencies
    check_and_install_dependencies()
    
    # Get user input
    business_type, location = get_user_input()
    
    # Ask user for output format
    print("\n📤 Choose output format:")
    print("1. CSV file (default)")
    if GOOGLE_SHEETS_AVAILABLE:
        print("2. Google Sheets")
        print("3. Both CSV and Google Sheets")
    
    output_choice = input("Enter your choice (1-3): ").strip()
    
    # Scrape Google Maps
    businesses = scrape_google_maps(business_type, location)
    
    if not businesses:
        print("❌ No businesses found. Please try different search terms.")
        return
    
    # Enrich with website data
    businesses = enrich_business_data(businesses)
    
    # Save to CSV (always create CSV as backup)
    filename = save_to_csv(businesses, business_type, location)
    
    # Handle Google Sheets if requested
    sheet_url = None
    if GOOGLE_SHEETS_AVAILABLE and output_choice in ['2', '3']:
        print("\n📊 Creating Google Sheet...")
        sheet_url = save_to_google_sheets(businesses, business_type, location)
    
    # Print results
    print(f"\n✅ SCRAPING COMPLETE!")
    print("=" * 50)
    print(f"📊 Total leads collected: {len(businesses)}")
    print(f"📁 CSV file saved to: {filename}")
    
    if sheet_url:
        print(f"📊 Google Sheet URL: {sheet_url}")
    
    # Print summary statistics
    with_websites = sum(1 for b in businesses if b['website'])
    with_emails = sum(1 for b in businesses if b['email'])
    with_phone = sum(1 for b in businesses if b['phone'])
    with_instagram = sum(1 for b in businesses if b['instagram'])
    with_facebook = sum(1 for b in businesses if b['facebook'])
    with_tiktok = sum(1 for b in businesses if b['tiktok'])
    
    print(f"\n📈 SUMMARY:")
    print(f"   • Businesses with websites: {with_websites}")
    print(f"   • Businesses with emails: {with_emails}")
    print(f"   • Businesses with phone numbers: {with_phone}")
    print(f"   • Businesses with Instagram: {with_instagram}")
    print(f"   • Businesses with Facebook: {with_facebook}")
    print(f"   • Businesses with TikTok: {with_tiktok}")
    
    print(f"\n🎉 Your leads are ready!")
    if sheet_url:
        print(f"📊 Google Sheet: {sheet_url}")
    print(f"📁 CSV file: {filename}")

if __name__ == "__main__":
    main()