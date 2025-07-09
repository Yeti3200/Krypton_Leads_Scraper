# Krypton Leads Scraper

A comprehensive local Python scraping tool that extracts business leads from Google Maps and enriches them with contact information from their websites.

## Features

- 🔍 **Google Maps Scraping**: Automatically searches and extracts business listings
- 🌐 **Website Scraping**: Extracts emails and social media links from business websites
- 📊 **CSV Export**: Saves all data in a structured CSV format
- 🛡️ **Anti-Detection**: Rotates user agents and includes rate limiting
- 📱 **Social Media**: Extracts Instagram, Facebook, and TikTok links
- 🎯 **Targeted Search**: Search by business type and location
- 📈 **Progress Tracking**: Real-time progress updates and statistics

## Installation

### 1. Clone or Download

Download the project folder to your local machine.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

**IMPORTANT**: After installing the Python packages, you must install the Playwright browser dependencies:

```bash
playwright install
```

## Usage

### Quick Start

1. Navigate to the project directory:
```bash
cd Krypton_Leads_Scraper
```

2. Run the scraper:
```bash
python main.py
```

3. Enter your search parameters when prompted:
   - **Business Type**: e.g., "med spa", "restaurant", "dentist"
   - **Location**: e.g., "Dallas, TX", "New York, NY", "Los Angeles, CA"

### Example Usage

```
🔍 KRYPTON LEADS SCRAPER
==================================================
Enter business type (e.g., 'med spa', 'restaurant'): med spa
Enter location (e.g., 'Dallas, TX', 'New York, NY'): Dallas, TX
```

## Output

The scraper will create a CSV file with the following columns:

- **Business Name**: The name of the business
- **Website**: Business website URL
- **Email**: Primary email address found
- **Phone**: Phone number
- **Address**: Business address
- **Instagram**: Instagram profile URL
- **Facebook**: Facebook page URL
- **TikTok**: TikTok profile URL

### Sample Output File

```
leads_med_spa_Dallas_TX_20240109_143022.csv
```

## Features in Detail

### Google Maps Scraping
- Searches Google Maps for your specified business type and location
- Extracts up to 20 businesses from search results
- Collects basic business information (name, address, phone, website)

### Website Enrichment
- Visits each business website (if available)
- Scrapes homepage and contact/about pages
- Extracts email addresses using regex patterns
- Finds social media links (Instagram, Facebook, TikTok)

### Anti-Detection Features
- Rotates user agents to avoid detection
- Implements random delays between requests
- Uses headless browser for Google Maps
- Respects rate limits

### Error Handling
- Graceful handling of missing information
- Timeout protection for slow websites
- Continues processing even if individual sites fail
- Detailed error logging

## Troubleshooting

### Common Issues

1. **"Missing required packages" error**
   - Run: `pip install -r requirements.txt`

2. **"Playwright browsers not installed" error**
   - Run: `playwright install`

3. **Permission denied errors**
   - Make sure you have write permissions in the directory
   - Try running with `sudo` on Mac/Linux if needed

4. **No results found**
   - Try different search terms
   - Check your internet connection
   - Verify the location format (e.g., "City, State")

### Dependencies

- **Python 3.7+**: Required for the script
- **playwright**: For automated browser interaction
- **beautifulsoup4**: For HTML parsing
- **requests**: For HTTP requests
- **pandas**: For data handling

## Legal and Ethical Considerations

- This tool is for educational and legitimate business purposes only
- Respect website terms of service
- Use responsibly and don't overload servers
- Consider reaching out to businesses directly when possible
- Be mindful of privacy and data protection regulations

## Rate Limiting

The scraper includes built-in rate limiting to be respectful to websites:
- 1-3 second delays between website requests
- 1-2 second delays between Google Maps interactions
- Random user agent rotation

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify your internet connection
4. Try with different search terms

## Future Enhancements

Potential improvements for future versions:
- Multi-threading for faster processing
- Database storage options
- Advanced filtering options
- Export to other formats (JSON, Excel)
- GUI interface
- Additional social media platforms