import streamlit as st
import subprocess
import os
import pandas as pd
import glob
from datetime import datetime
import sys
import time
import json
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
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
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

def run_scraper_with_output(business_type, location, output_format):
    """Run the scraper and show real-time output"""
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
        stdout, stderr = process.communicate(timeout=300)
        
        return process.returncode == 0, stdout, stderr
        
    except subprocess.TimeoutExpired:
        return False, "", "Scraper timed out after 5 minutes"
    except Exception as e:
        return False, "", str(e)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Krypton Leads Scraper</h1>
        <p>Generate high-quality business leads from Google Maps</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content in tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Scrape Leads", "📊 View Results", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Generate New Leads")
        
        # Input form
        with st.form("scraper_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                business_type = st.text_input(
                    "Business Type",
                    value="restaurant",
                    placeholder="e.g., restaurant, med spa, dentist",
                    help="Enter the type of business you want to find"
                )
            
            with col2:
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
        
        # Handle form submission
        if submitted:
            if not business_type.strip() or not location.strip():
                st.error("Please enter both business type and location")
            else:
                # Convert format to number for main.py
                format_map = {"CSV Only": "1", "Google Sheets": "2", "Both": "3"}
                format_choice = format_map[output_format]
                
                # Show progress
                progress_container = st.container()
                with progress_container:
                    st.info(f"🔍 Scraping '{business_type}' businesses in '{location}'...")
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate progress
                    for i in range(100):
                        time.sleep(0.05)
                        progress_bar.progress(i + 1)
                        if i < 20:
                            status_text.text("🔍 Searching Google Maps...")
                        elif i < 60:
                            status_text.text("📍 Extracting business information...")
                        elif i < 90:
                            status_text.text("🌐 Scraping websites for contact info...")
                        else:
                            status_text.text("💾 Saving results...")
                    
                    # Run the actual scraper
                    success, stdout, stderr = run_scraper_with_output(business_type, location, format_choice)
                    
                    progress_bar.empty()
                    status_text.empty()
                
                if success:
                    st.success("✅ Scraping completed successfully!")
                    
                    # Extract Google Sheets URL from output if available
                    if "Sheet URL:" in stdout:
                        sheet_url = stdout.split("Sheet URL: ")[1].split("\\n")[0].strip()
                        if sheet_url:
                            st.markdown(f"### 🔗 [Open Google Sheet]({sheet_url})")
                    
                    # Show basic stats from output
                    if "Total leads collected:" in stdout:
                        leads_count = stdout.split("Total leads collected: ")[1].split("\\n")[0].strip()
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
                    st.metric("🌐 With Websites", len(df[df['Website'].notna() & (df['Website'] != '')]))
                with col3:
                    st.metric("📧 With Emails", len(df[df['Email'].notna() & (df['Email'] != '')]))
                with col4:
                    st.metric("📱 With Phone", len(df[df['Phone'].notna() & (df['Phone'] != '')]))
                
                # Filters
                st.subheader("🔍 Filter Results")
                col1, col2 = st.columns(2)
                with col1:
                    show_with_website = st.checkbox("Show only leads with websites", value=False)
                with col2:
                    show_with_email = st.checkbox("Show only leads with emails", value=False)
                
                # Apply filters
                filtered_df = df.copy()
                if show_with_website:
                    filtered_df = filtered_df[filtered_df['Website'].notna() & (filtered_df['Website'] != '')]
                if show_with_email:
                    filtered_df = filtered_df[filtered_df['Email'].notna() & (filtered_df['Email'] != '')]
                
                # Display data
                st.subheader("📋 Lead Data")
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                # Export options
                st.subheader("💾 Export Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = filtered_df.to_csv(index=False)
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
                                sheet_url = export_to_google_sheets(filtered_df, "filtered_leads", "export")
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
        - 📊 Google Sheets integration
        - 💾 CSV export with timestamps
        - 🎯 Social media link extraction
        - 🛡️ Robust error handling
        """)

if __name__ == "__main__":
    main()