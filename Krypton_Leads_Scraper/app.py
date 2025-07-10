import streamlit as st
import asyncio
import pandas as pd
import time
import re
import io
from datetime import datetime
from playwright.async_api import async_playwright

# Page config
st.set_page_config(
    page_title="Krypton Leads Scraper",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Ultra-modern styling with glowing effects
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Global theme */
    .stApp {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
        color: #F0F6FC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Perfect centering */
    .main .block-container {
        max-width: 750px;
        padding: 4rem 2rem;
        margin: 0 auto;
    }
    
    /* Modern title with glow */
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #58A6FF 0%, #F78166 50%, #A5A5A5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.03em;
        text-shadow: 0 0 40px rgba(88, 166, 255, 0.3);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        text-align: center;
        color: #8B949E;
        margin-bottom: 4rem;
        letter-spacing: -0.01em;
    }
    
    /* Form container with glass effect */
    .input-container {
        background: rgba(33, 38, 45, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Modern input fields */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #F0F6FC;
        font-size: 1.1rem;
        padding: 1rem 1.2rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #58A6FF;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #30363D 0%, #21262D 100%);
    }
    
    .stTextInput > label {
        color: #F0F6FC;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Slider styling */
    .stSlider > label {
        color: #F0F6FC;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 0.8rem;
    }
    
    .stSlider [data-baseweb="slider"] {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] {
        background: linear-gradient(135deg, #58A6FF 0%, #79C0FF 100%);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.4);
    }
    
    /* Glowing gradient button */
    .stButton > button {
        background: linear-gradient(135deg, #58A6FF 0%, #79C0FF 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 16px;
        padding: 1rem 2.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        width: 100%;
        height: 3.5rem;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.01em;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(88, 166, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(88, 166, 255, 0.5);
        background: linear-gradient(135deg, #79C0FF 0%, #58A6FF 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 4px 16px rgba(88, 166, 255, 0.4);
    }
    
    /* Animated stats cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1.5rem;
        margin: 3rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #58A6FF, #79C0FF, #A5A5A5);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(88, 166, 255, 0.2);
        border-color: rgba(88, 166, 255, 0.3);
    }
    
    .stat-card:hover::before {
        opacity: 1;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #58A6FF;
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #8B949E;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, rgba(35, 134, 54, 0.2) 0%, rgba(35, 134, 54, 0.1) 100%);
        border: 1px solid #238636;
        border-radius: 12px;
        color: #7EE787;
        padding: 1rem 1.5rem;
        font-weight: 500;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(218, 54, 51, 0.2) 0%, rgba(218, 54, 51, 0.1) 100%);
        border: 1px solid #DA3633;
        border-radius: 12px;
        color: #FF7B72;
        padding: 1rem 1.5rem;
        font-weight: 500;
    }
    
    /* Modern dataframe styling */
    .stDataFrame {
        margin: 2rem 0;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        overflow: hidden;
    }
    
    /* Download buttons */
    .download-buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #F0F6FC;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #30363D 0%, #21262D 100%);
        border-color: #58A6FF;
        box-shadow: 0 4px 16px rgba(88, 166, 255, 0.2);
        transform: translateY(-1px);
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #58A6FF !important;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #F0F6FC;
        margin: 3rem 0 1.5rem 0;
        text-align: center;
        letter-spacing: -0.02em;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #F0F6FC;
        font-weight: 600;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #58A6FF;
        box-shadow: 0 4px 16px rgba(88, 166, 255, 0.1);
    }
    
    .streamlit-expanderContent {
        background: linear-gradient(135deg, #161B22 0%, #21262D 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem;
    }
    
    /* How to use styling */
    .how-to-step {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin: 1.5rem 0;
        padding: 1rem;
        background: rgba(33, 38, 45, 0.3);
        border-radius: 12px;
        border-left: 3px solid #58A6FF;
    }
    
    .step-number {
        background: linear-gradient(135deg, #58A6FF 0%, #79C0FF 100%);
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 0.5rem 0.8rem;
        border-radius: 8px;
        min-width: 2rem;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-weight: 600;
        color: #F0F6FC;
        margin-bottom: 0.3rem;
    }
    
    .step-description {
        color: #8B949E;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .input-container {
            padding: 1.5rem;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .download-buttons {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'scraping' not in st.session_state:
    st.session_state.scraping = False

# Common US cities for autocomplete
MAJOR_CITIES = [
    "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ",
    "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX", "San Jose, CA",
    "Austin, TX", "Jacksonville, FL", "Fort Worth, TX", "Columbus, OH", "Charlotte, NC",
    "San Francisco, CA", "Indianapolis, IN", "Seattle, WA", "Denver, CO", "Washington, DC",
    "Boston, MA", "El Paso, TX", "Detroit, MI", "Nashville, TN", "Portland, OR",
    "Memphis, TN", "Oklahoma City, OK", "Las Vegas, NV", "Louisville, KY", "Baltimore, MD",
    "Milwaukee, WI", "Albuquerque, NM", "Tucson, AZ", "Fresno, CA", "Sacramento, CA",
    "Long Beach, CA", "Kansas City, MO", "Mesa, AZ", "Virginia Beach, VA", "Atlanta, GA",
    "Colorado Springs, CO", "Omaha, NE", "Raleigh, NC", "Miami, FL", "Oakland, CA",
    "Minneapolis, MN", "Tulsa, OK", "Cleveland, OH", "Wichita, KS", "Arlington, TX",
    "Tampa, FL", "New Orleans, LA", "Honolulu, HI", "Anaheim, CA", "Santa Ana, CA",
    "St. Louis, MO", "Riverside, CA", "Corpus Christi, TX", "Lexington, KY", "Pittsburgh, PA",
    "Anchorage, AK", "Stockton, CA", "Cincinnati, OH", "St. Paul, MN", "Toledo, OH",
    "Greensboro, NC", "Newark, NJ", "Plano, TX", "Henderson, NV", "Lincoln, NE",
    "Buffalo, NY", "Jersey City, NJ", "Chula Vista, CA", "Fort Wayne, IN", "Orlando, FL",
    "St. Petersburg, FL", "Chandler, AZ", "Laredo, TX", "Norfolk, VA", "Durham, NC",
    "Madison, WI", "Lubbock, TX", "Irvine, CA", "Winston-Salem, NC", "Glendale, AZ",
    "Garland, TX", "Hialeah, FL", "Reno, NV", "Chesapeake, VA", "Gilbert, AZ",
    "Baton Rouge, LA", "Irving, TX", "Scottsdale, AZ", "North Las Vegas, NV", "Fremont, CA",
    "Boise, ID", "Richmond, VA", "San Bernardino, CA", "Birmingham, AL", "Spokane, WA",
    "Rochester, NY", "Des Moines, IA", "Modesto, CA", "Fayetteville, NC", "Tacoma, WA",
    "Oxnard, CA", "Fontana, CA", "Columbus, GA", "Montgomery, AL", "Moreno Valley, CA",
    "Shreveport, LA", "Aurora, IL", "Yonkers, NY", "Akron, OH", "Huntington Beach, CA",
    "Little Rock, AR", "Augusta, GA", "Amarillo, TX", "Glendale, CA", "Mobile, AL",
    "Grand Rapids, MI", "Salt Lake City, UT", "Tallahassee, FL", "Huntsville, AL", "Grand Prairie, TX",
    "Knoxville, TN", "Worcester, MA", "Newport News, VA", "Brownsville, TX", "Overland Park, KS",
    "Santa Clarita, CA", "Providence, RI", "Garden Grove, CA", "Chattanooga, TN", "Oceanside, CA",
    "Jackson, MS", "Fort Lauderdale, FL", "Santa Rosa, CA", "Rancho Cucamonga, CA", "Port St. Lucie, FL",
    "Tempe, AZ", "Ontario, CA", "Vancouver, WA", "Cape Coral, FL", "Sioux Falls, SD",
    "Springfield, MO", "Peoria, AZ", "Pembroke Pines, FL", "Elk Grove, CA", "Salem, OR",
    "Lancaster, CA", "Corona, CA", "Eugene, OR", "Palmdale, CA", "Salinas, CA",
    "Springfield, MA", "Pasadena, CA", "Fort Collins, CO", "Hayward, CA", "Pomona, CA",
    "Cary, NC", "Rockford, IL", "Alexandria, VA", "Escondido, CA", "McKinney, TX",
    "Kansas City, KS", "Bridgeport, CT", "Dayton, OH", "Hollywood, FL", "Paterson, NJ",
    "Sunnyvale, CA", "Torrance, CA", "Lakewood, CO", "Miami Beach, FL", "Killeen, TX"
]


async def scrape_leads(business_type: str, location: str, max_results: int):
    """Scrape leads from Google Maps"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to Google Maps
            search_url = f"https://www.google.com/maps/search/{business_type}+{location}".replace(' ', '+')
            await page.goto(search_url, timeout=15000)
            
            # Wait for results
            await page.wait_for_selector('[role="main"]', timeout=10000)
            await asyncio.sleep(2)
            
            # Scroll to load more results
            await page.evaluate('window.scrollTo(0, 2000)')
            await asyncio.sleep(1)
            
            # Get business links
            business_links = await page.query_selector_all('a[href*="/maps/place/"]')
            
            leads = []
            
            for i, link in enumerate(business_links[:max_results]):
                try:
                    # Click the business
                    await link.click()
                    await asyncio.sleep(1)
                    
                    lead = {}
                    
                    # Get business name
                    name_selectors = ['h1', '[data-attrid="title"]', '.DUwDvf']
                    for selector in name_selectors:
                        name_element = await page.query_selector(selector)
                        if name_element:
                            name = await name_element.inner_text()
                            if name and len(name) > 2 and name not in ['Results', 'Map', 'Search', 'Google']:
                                lead['Business Name'] = name.strip()
                                break
                    
                    if not lead.get('Business Name'):
                        continue
                    
                    # Get website
                    website_element = await page.query_selector('a[href*="http"]:not([href*="google"]):not([href*="maps"])')
                    lead['Website'] = await website_element.get_attribute('href') if website_element else ''
                    
                    # Get phone
                    phone_element = await page.query_selector('button[data-item-id*="phone"]')
                    lead['Phone'] = (await phone_element.inner_text()).strip() if phone_element else ''
                    
                    # Get address
                    address_element = await page.query_selector('button[data-item-id="address"]')
                    lead['Address'] = (await address_element.inner_text()).strip() if address_element else ''
                    
                    # Get rating
                    rating_element = await page.query_selector('[data-value="Rating"] span')
                    if rating_element:
                        try:
                            rating_text = await rating_element.inner_text()
                            lead['Rating'] = float(rating_text.split()[0])
                        except:
                            lead['Rating'] = 0
                    else:
                        lead['Rating'] = 0
                    
                    # Get reviews count
                    reviews_element = await page.query_selector('[data-value="Reviews"] span')
                    if reviews_element:
                        try:
                            reviews_text = await reviews_element.inner_text()
                            lead['Reviews'] = int(re.search(r'(\d+)', reviews_text).group(1))
                        except:
                            lead['Reviews'] = 0
                    else:
                        lead['Reviews'] = 0
                    
                    # Calculate quality score
                    quality = 0
                    if lead['Business Name']: quality += 2
                    if lead['Website']: quality += 3
                    if lead['Phone']: quality += 2
                    if lead['Address']: quality += 1
                    if lead['Rating'] > 0: quality += 1
                    if lead['Reviews'] > 0: quality += 1
                    lead['Quality'] = quality
                    
                    leads.append(lead)
                    
                except Exception:
                    continue
            
            return pd.DataFrame(leads)
            
        finally:
            await browser.close()

# Main header
st.markdown('<div class="main-title">Krypton Leads Scraper</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Professional lead generation from Google Maps</div>', unsafe_allow_html=True)

# Input form with glass effect
st.markdown('<div class="input-container">', unsafe_allow_html=True)

# Business type input with icon
business_type = st.text_input(
    "🏢 Business Type",
    placeholder="restaurant, coffee shop, gym, dentist...",
    help="What type of business are you looking for?",
    key="business_type"
)

# Location input - simple and works
location = st.selectbox(
    "📍 Location",
    options=["Choose a city..."] + sorted(MAJOR_CITIES),
    index=0,
    help="Select your city and state"
)

# Don't use the placeholder text
if location == "Choose a city...":
    location = ""

# Number of results slider
max_results = st.slider(
    "📊 Number of Results",
    min_value=5,
    max_value=50,
    value=20,
    help="How many leads to scrape"
)

st.markdown("<br>", unsafe_allow_html=True)

# Glowing start button
if st.button("🚀 Start Scraping", type="primary", disabled=st.session_state.scraping):
    if not business_type or not location:
        st.error("Please enter both business type and location")
    else:
        st.session_state.scraping = True
        
        with st.spinner("Scraping leads..."):
            start_time = time.time()
            
            # Run scraper
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            df = loop.run_until_complete(scrape_leads(business_type, location, max_results))
            
            duration = time.time() - start_time
            st.session_state.results = df
            st.session_state.scraping = False
            
            if len(df) > 0:
                st.success(f"✅ Found {len(df)} leads in {duration:.1f} seconds")
            else:
                st.error("No leads found. Try different search terms.")

st.markdown('</div>', unsafe_allow_html=True)

# Results section
if st.session_state.results is not None and len(st.session_state.results) > 0:
    df = st.session_state.results
    
    # Animated stats cards
    st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{len(df)}</div>
            <div class="stat-label">Total Leads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        with_websites = len(df[df['Website'] != ''])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{with_websites}</div>
            <div class="stat-label">With Websites</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        with_phones = len(df[df['Phone'] != ''])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{with_phones}</div>
            <div class="stat-label">With Phones</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_quality = df['Quality'].mean()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{avg_quality:.1f}</div>
            <div class="stat-label">Avg Quality</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results table
    st.markdown('<div class="section-header">📋 Results</div>', unsafe_allow_html=True)
    
    # Sort by quality
    df_sorted = df.sort_values('Quality', ascending=False)
    
    st.dataframe(
        df_sorted,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Website": st.column_config.LinkColumn("Website"),
            "Rating": st.column_config.NumberColumn("Rating", format="%.1f"),
            "Reviews": st.column_config.NumberColumn("Reviews", format="%d"),
            "Quality": st.column_config.ProgressColumn("Quality", min_value=0, max_value=10)
        }
    )
    
    # Download buttons
    st.markdown('<div class="download-buttons">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV",
            csv_data,
            file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        st.download_button(
            "📊 Download Excel",
            excel_buffer.getvalue(),
            file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# How to use section (expandable)
st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander("💡 How to Use"):
    st.markdown("""
    <div class="how-to-step">
        <div class="step-number">1</div>
        <div class="step-content">
            <div class="step-title">🏢 Enter Business Type</div>
            <div class="step-description">Examples: restaurant, coffee shop, gym, dentist, law firm, salon</div>
        </div>
    </div>
    
    <div class="how-to-step">
        <div class="step-number">2</div>
        <div class="step-content">
            <div class="step-title">📍 Enter Location</div>
            <div class="step-description">Be specific with city and state: "Austin, TX" or "New York, NY"</div>
        </div>
    </div>
    
    <div class="how-to-step">
        <div class="step-number">3</div>
        <div class="step-content">
            <div class="step-title">📊 Set Number of Results</div>
            <div class="step-description">Start with 10-20 for testing, increase to 50 for larger datasets</div>
        </div>
    </div>
    
    <div class="how-to-step">
        <div class="step-number">4</div>
        <div class="step-content">
            <div class="step-title">🚀 Start Scraping</div>
            <div class="step-description">Click the button and wait for results to appear automatically</div>
        </div>
    </div>
    
    <div class="how-to-step">
        <div class="step-number">5</div>
        <div class="step-content">
            <div class="step-title">💾 Download Results</div>
            <div class="step-description">Choose CSV or Excel format, results are sorted by quality score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer spacing
st.markdown('<div style="margin-top: 4rem;"></div>', unsafe_allow_html=True)