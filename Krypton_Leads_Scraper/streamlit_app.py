import streamlit as st
import subprocess
import os
import pandas as pd
import glob
from datetime import datetime
import sys
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="Krypton Leads Scraper",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sleek dark mode with high-end tech vibes
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Global styles */
    [data-testid="stAppViewContainer"] {
        background: #1a1b26;  /* Deep blue-gray */
        color: #e0e0e0;  /* Light text */
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        background: #2a2d3a;
        border: 1px solid #444;
        color: #e0e0e0;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(42, 45, 58, 0.7);
        border: 1px solid #444;
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #444;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #2a2d3a;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #e0e0e0;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(42, 45, 58, 0.5);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #444;
    }
    
    /* Success/Error boxes */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1);
        border: 1px solid #4CAF50;
        border-radius: 10px;
    }
    
    .stError {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid #f44336;
        border-radius: 10px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #1a1b26;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #888;
        font-size: 0.9rem;
        border-top: 1px solid #333;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

def get_latest_csv():
    """Get the most recent CSV file in the current directory"""
    csv_files = glob.glob("leads_*.csv")
    if not csv_files:
        return None
    csv_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return csv_files[0]

def export_to_google_sheets(df, business_type, location):
    """Export dataframe to Google Sheets"""
    if not GOOGLE_SHEETS_AVAILABLE:
        st.error("Google Sheets libraries not installed. Please install: pip install gspread google-auth")
        return None
    
    try:
        gc = gspread.oauth()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_name = f"Leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}"
        
        spreadsheet = gc.create(sheet_name)
        worksheet = spreadsheet.sheet1
        
        # Convert dataframe to list of lists for Google Sheets
        data = [df.columns.tolist()] + df.values.tolist()
        worksheet.update('A1', data)
        
        # Make the spreadsheet shareable
        spreadsheet.share('', perm_type='anyone', role='reader')
        
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        return sheet_url
        
    except Exception as e:
        st.error(f"Error creating Google Sheet: {e}")
        return None

def run_scraper_with_realtime_output(business_type, location, output_format):
    """Run the scraper and return results"""
    try:
        # Prepare the command
        cmd = [sys.executable, "main.py", business_type, location]
        
        # Create process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Send the output format choice
        process.stdin.write(f"{output_format}\n")
        process.stdin.flush()
        
        # Wait for completion
        stdout, stderr = process.communicate()
        
        return process.returncode == 0, stdout, stderr
        
    except Exception as e:
        return False, "", str(e)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Krypton Leads Scraper</h1>
        <p>Professional Lead Generation from Google Maps</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Scrape Leads", "📊 View Results", "⚙️ Settings"])
    
    with tab1:
        # Create main layout with columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎯 Lead Generation")
            
            # Form for input
            with st.form("scraper_form"):
                # Input fields in columns
                input_col1, input_col2 = st.columns(2)
                
                with input_col1:
                    business_type = st.text_input(
                        "Business Type",
                        value="restaurant",
                        placeholder="e.g., restaurant, med spa, dentist",
                        help="Enter the type of business you want to find"
                    )
                
                with input_col2:
                    location = st.text_input(
                        "Location",
                        value="Dallas, TX",
                        placeholder="e.g., Dallas, TX, New York, NY",
                        help="Enter the city and state to search"
                    )
                
                # Output format
                output_format = st.radio(
                    "Output Format",
                    options=["CSV Only", "Google Sheets", "Both"],
                    index=0,
                    horizontal=True,
                    help="Choose how you want to receive your leads"
                )
                
                # Submit button
                submitted = st.form_submit_button("🚀 Start Scraping", use_container_width=True)
        
        with col2:
            st.subheader("💡 Tips")
            st.info("""
            **Best Practices:**
            - Use specific business types
            - Include city and state
            - Start with smaller areas
            - Check results regularly
            """)
        
        # Handle form submission
        if submitted:
            if not business_type.strip() or not location.strip():
                st.error("Please enter both business type and location")
            else:
                # Convert format to number for main.py
                format_map = {"CSV Only": "1", "Google Sheets": "2", "Both": "3"}
                format_choice = format_map[output_format]
                
                # Show progress
                with st.container():
                    st.info(f"🔍 Scraping '{business_type}' businesses in '{location}'...")
                    
                    # Simple progress indication
                    progress_text = st.empty()
                    progress_text.text("🚀 Starting scraper...")
                    
                    # Run the actual scraper
                    success, stdout, stderr = run_scraper_with_realtime_output(business_type, location, format_choice)
                    
                    # Clear progress
                    progress_text.empty()
                
                if success:
                    st.success("✅ Scraping completed successfully!")
                    
                    # Extract Google Sheets URL from output if available
                    if "Sheet URL:" in stdout:
                        sheet_url = stdout.split("Sheet URL: ")[1].split("\n")[0].strip()
                        if sheet_url:
                            st.markdown(f"### 🔗 [Open Google Sheet]({sheet_url})")
                    
                    # Show basic stats from output
                    if "Total leads collected:" in stdout:
                        leads_count = stdout.split("Total leads collected: ")[1].split("\n")[0].strip()
                        st.metric("Total Leads Found", leads_count)
                    
                    st.rerun()
                else:
                    st.error("❌ Scraping failed!")
                    if stderr:
                        st.text_area("Error Details", stderr, height=200)
    
    with tab2:
        st.subheader("📊 Latest Results")
        
        # Check for latest CSV
        latest_csv = get_latest_csv()
        if latest_csv:
            try:
                df = pd.read_csv(latest_csv)
                
                # File info
                file_stats = os.stat(latest_csv)
                file_size = file_stats.st_size / 1024
                modified_time = datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📋 Total Leads", len(df))
                with col2:
                    website_col = 'Website' if 'Website' in df.columns else 'website'
                    if website_col in df.columns:
                        st.metric("🌐 With Websites", len(df[df[website_col].notna() & (df[website_col] != '')]))
                    else:
                        st.metric("🌐 With Websites", 0)
                with col3:
                    email_col = 'Email' if 'Email' in df.columns else 'email'
                    if email_col in df.columns:
                        st.metric("📧 With Emails", len(df[df[email_col].notna() & (df[email_col] != '')]))
                    else:
                        st.metric("📧 With Emails", 0)
                with col4:
                    phone_col = 'Phone' if 'Phone' in df.columns else 'phone'
                    if phone_col in df.columns:
                        st.metric("📱 With Phone", len(df[df[phone_col].notna() & (df[phone_col] != '')]))
                    else:
                        st.metric("📱 With Phone", 0)
                
                # Add second row of metrics for social media
                col5, col6, col7, col8 = st.columns(4)
                with col5:
                    instagram_col = 'Instagram' if 'Instagram' in df.columns else 'instagram'
                    if instagram_col in df.columns:
                        st.metric("📷 Instagram", len(df[df[instagram_col].notna() & (df[instagram_col] != '')]))
                    else:
                        st.metric("📷 Instagram", 0)
                with col6:
                    facebook_col = 'Facebook' if 'Facebook' in df.columns else 'facebook'
                    if facebook_col in df.columns:
                        st.metric("📵 Facebook", len(df[df[facebook_col].notna() & (df[facebook_col] != '')]))
                    else:
                        st.metric("📵 Facebook", 0)
                with col7:
                    twitter_col = 'Twitter' if 'Twitter' in df.columns else 'twitter'
                    if twitter_col in df.columns:
                        st.metric("🐦 Twitter/X", len(df[df[twitter_col].notna() & (df[twitter_col] != '')]))
                    else:
                        st.metric("🐦 Twitter/X", 0)
                with col8:
                    owner_twitter_col = 'Owner Twitter' if 'Owner Twitter' in df.columns else 'owner_twitter'
                    if owner_twitter_col in df.columns:
                        st.metric("👤 Owner Twitter", len(df[df[owner_twitter_col].notna() & (df[owner_twitter_col] != '')]))
                    else:
                        st.metric("👤 Owner Twitter", 0)
                
                # Display data
                st.subheader("📋 Lead Data")
                st.dataframe(df, use_container_width=True, height=400)
                
                # Export options
                st.subheader("💾 Export Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"filtered_{latest_csv}",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    if GOOGLE_SHEETS_AVAILABLE:
                        if st.button("📊 Export to Google Sheets", use_container_width=True):
                            with st.spinner("Creating Google Sheet..."):
                                sheet_url = export_to_google_sheets(df, "exported_leads", "export")
                                if sheet_url:
                                    st.success("✅ Google Sheet created successfully!")
                                    st.markdown(f"### 🔗 [Open Google Sheet]({sheet_url})")
                    else:
                        st.info("💡 Install Google Sheets support: pip install gspread google-auth")
                
                # File details
                st.subheader("📄 File Details")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.text(f"📁 File: {latest_csv}")
                with col2:
                    st.text(f"📊 Size: {file_size:.1f} KB")
                with col3:
                    st.text(f"🕒 Modified: {modified_time}")
                
            except Exception as e:
                st.error(f"Error loading data: {e}")
        else:
            st.info("No lead data found. Start by scraping some leads in the 'Scrape Leads' tab!")
    
    with tab3:
        st.subheader("⚙️ Settings & Configuration")
        
        
        # Google Sheets setup
        st.markdown("### 🔗 Google Sheets Integration")
        if GOOGLE_SHEETS_AVAILABLE:
            st.success("✅ Google Sheets integration is available")
            st.markdown("""
            **How to set up Google Sheets authentication:**
            1. Go to [Google Cloud Console](https://console.cloud.google.com/)
            2. Create a new project or select existing
            3. Enable Google Sheets API
            4. Create OAuth 2.0 credentials
            5. Download the credentials file to this directory
            """)
        else:
            st.warning("⚠️ Google Sheets integration not available")
            st.code("pip install gspread google-auth")
        
        # System info
        st.markdown("### 🖥️ System Information")
        col1, col2 = st.columns(2)
        with col1:
            st.text(f"Python: {sys.version.split()[0]}")
            st.text(f"Working Directory: {os.getcwd()}")
        with col2:
            st.text(f"Streamlit: {st.__version__}")
            st.text(f"Google Sheets: {'Available' if GOOGLE_SHEETS_AVAILABLE else 'Not Available'}")
        
        # About
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Krypton Leads Scraper** is a powerful tool for generating business leads from Google Maps.
        It extracts business information including names, websites, emails, phone numbers, and social media links.
        
        **Features:**
        - 🔍 Google Maps scraping with advanced selectors
        - 🌐 Website scraping for contact information
        - 🐦 Twitter/X account discovery (business + owner accounts)
        - 📊 Google Sheets integration
        - 💾 CSV export with timestamps
        - 🎯 Social media link extraction (Instagram, Facebook, TikTok, Twitter/X)
        - 🛡️ Robust error handling
        """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>🚀 Krypton Leads Scraper v2.0 | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()