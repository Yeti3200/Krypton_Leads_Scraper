import streamlit as st
import subprocess
import os
import pandas as pd
import glob
from datetime import datetime
import sys
import time
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

st.set_page_config(
    page_title="Krypton Leads Scraper",
    page_icon="🔍",
    layout="wide"
)

def get_latest_csv():
    """Get the most recent CSV file in the current directory"""
    csv_files = glob.glob("leads_*.csv")
    if not csv_files:
        return None
    
    # Sort by modification time, most recent first
    csv_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return csv_files[0]

def export_to_google_sheets(df, business_type, location):
    """Export dataframe to Google Sheets"""
    if not GOOGLE_SHEETS_AVAILABLE:
        st.error("Google Sheets libraries not installed. Please install: pip install gspread google-auth")
        return None
    
    try:
        # Try to use OAuth authentication
        gc = gspread.oauth()
        
        # Create spreadsheet name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_name = f"Leads_{business_type.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_{timestamp}"
        
        # Create new spreadsheet
        spreadsheet = gc.create(sheet_name)
        
        # Get the first worksheet
        worksheet = spreadsheet.sheet1
        
        # Convert dataframe to list of lists for Google Sheets
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Update the worksheet
        worksheet.update('A1', data)
        
        # Make the spreadsheet shareable
        spreadsheet.share('', perm_type='anyone', role='reader')
        
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
        return sheet_url
        
    except Exception as e:
        st.error(f"Error creating Google Sheet: {e}")
        return None

def run_scraper(business_type, location):
    """Run the main.py scraper with given parameters"""
    try:
        # Run the scraper as a subprocess
        result = subprocess.run(
            [sys.executable, "main.py", business_type, location],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Scraper timed out after 5 minutes"
    except Exception as e:
        return False, "", str(e)

def main():
    st.title("🔍 Krypton Leads Scraper Dashboard")
    st.markdown("Generate business leads from Google Maps with website enrichment")
    
    # Create two columns for the input fields
    col1, col2 = st.columns(2)
    
    with col1:
        business_type = st.text_input(
            "Business Type",
            value="med spa",
            help="e.g., 'med spa', 'restaurant', 'dentist'"
        )
    
    with col2:
        location = st.text_input(
            "Location",
            value="Cleveland, OH",
            help="e.g., 'Cleveland, OH', 'Dallas, TX', 'New York, NY'"
        )
    
    # Center the button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        start_scraping = st.button("🚀 Start Scraping", type="primary", use_container_width=True)
    
    # Display current CSV file if it exists
    latest_csv = get_latest_csv()
    if latest_csv:
        st.markdown("---")
        st.subheader("📁 Latest Results")
        
        # Display file info
        file_stats = os.stat(latest_csv)
        file_size = file_stats.st_size / 1024  # Convert to KB
        modified_time = datetime.fromtimestamp(file_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File", latest_csv)
        with col2:
            st.metric("Size", f"{file_size:.1f} KB")
        with col3:
            st.metric("Modified", modified_time)
        
        # Load and display the CSV
        try:
            df = pd.read_csv(latest_csv)
            
            # Display summary statistics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Leads", len(df))
            with col2:
                st.metric("With Websites", len(df[df['Website'].notna() & (df['Website'] != '')]))
            with col3:
                st.metric("With Emails", len(df[df['Email'].notna() & (df['Email'] != '')]))
            with col4:
                st.metric("With Phone", len(df[df['Phone'].notna() & (df['Phone'] != '')]))
            
            # Display the data table
            st.subheader("📋 Lead Data")
            
            # Add filters
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
            
            # Display filtered data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Download and export buttons
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=latest_csv,
                    mime="text/csv",
                    type="primary",
                    use_container_width=True
                )
            
            with col2:
                if GOOGLE_SHEETS_AVAILABLE:
                    if st.button("📊 Export to Google Sheets", use_container_width=True):
                        with st.spinner("Creating Google Sheet..."):
                            sheet_url = export_to_google_sheets(filtered_df, "exported_leads", "dashboard")
                            if sheet_url:
                                st.success(f"✅ Google Sheet created successfully!")
                                st.markdown(f"[🔗 Open Google Sheet]({sheet_url})")
                else:
                    st.info("💡 Install Google Sheets support: pip install gspread google-auth")
            
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
    
    # Handle scraping button click
    if start_scraping:
        if not business_type.strip() or not location.strip():
            st.error("Please enter both business type and location")
            return
        
        # Show progress
        with st.spinner(f"🔍 Scraping '{business_type}' businesses in '{location}'..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress periodically
            for i in range(100):
                time.sleep(0.1)
                progress_bar.progress(i + 1)
                if i < 20:
                    status_text.text("🔍 Searching Google Maps...")
                elif i < 60:
                    status_text.text("📍 Extracting business information...")
                elif i < 90:
                    status_text.text("🌐 Scraping websites for contact info...")
                else:
                    status_text.text("💾 Saving results to CSV...")
            
            # Run the actual scraper
            success, stdout, stderr = run_scraper(business_type, location)
            
            progress_bar.empty()
            status_text.empty()
        
        if success:
            st.success("✅ Scraping completed successfully!")
            
            # Show output if available
            if stdout:
                with st.expander("📋 Scraper Output"):
                    st.text(stdout)
            
            # Refresh the page to show new results
            st.rerun()
        else:
            st.error("❌ Scraping failed!")
            
            if stderr:
                with st.expander("⚠️ Error Details"):
                    st.text(stderr)
            
            if stdout:
                with st.expander("📋 Scraper Output"):
                    st.text(stdout)

if __name__ == "__main__":
    main()