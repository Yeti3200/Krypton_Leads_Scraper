# Google Sheets Integration Setup

## Overview
The Krypton Leads Scraper now supports exporting leads directly to Google Sheets. This feature allows you to automatically create and populate Google Sheets with your scraped lead data.

## Setup Instructions

### 1. Install Required Libraries
```bash
pip install gspread google-auth
```

### 2. Set Up Google Sheets API Access

#### Option A: OAuth 2.0 (Recommended for Personal Use)
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Select "Desktop application"
   - Download the credentials JSON file
5. The first time you run the scraper with Google Sheets option, it will open a browser window for authentication

#### Option B: Service Account (For Automated/Production Use)
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API (same as above)
4. Create a service account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create
5. Generate a key:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select JSON format and download
6. Place the JSON file in your project directory

## Usage

### Command Line Scraper
When running the main scraper, you'll be prompted to choose an output format:
1. CSV file (default)
2. Google Sheets
3. Both CSV and Google Sheets

### Streamlit Dashboard
The dashboard now includes an "Export to Google Sheets" button that will:
1. Create a new Google Sheet with your lead data
2. Make it shareable with a public link
3. Display the link for easy access

## Features

- **Automatic Authentication**: Uses OAuth 2.0 for seamless login
- **Shared Sheets**: Created sheets are automatically made shareable
- **Real-time Export**: Export existing CSV data to Google Sheets from the dashboard
- **Timestamped Names**: Each sheet gets a unique timestamp for organization

## Troubleshooting

### Common Issues:
1. **Authentication Error**: Make sure you've enabled the Google Sheets API in your Google Cloud project
2. **Permission Denied**: Ensure your OAuth credentials are correctly configured
3. **Import Errors**: Run `pip install gspread google-auth` to install required libraries

### If Google Sheets isn't working:
- The scraper will still work and save to CSV files
- You can manually import CSV files to Google Sheets
- Check that your Google Cloud project has the Sheets API enabled

## Security Notes
- OAuth credentials are stored locally and encrypted
- Service account keys should be kept secure
- Created sheets are public by default but can be modified for restricted access