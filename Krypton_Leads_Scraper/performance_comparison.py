#!/usr/bin/env python3
"""
Performance comparison between different scrapers
"""

import asyncio
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from turbo_scraper import turbo_scrape
from hyper_scraper import hyper_scrape

async def compare_scrapers():
    """Compare performance between turbo and hyper scrapers"""
    print("🏁 SCRAPER PERFORMANCE COMPARISON")
    print("=" * 50)
    
    test_query = "coffee shop"
    test_location = "Austin, TX"
    max_results = 10
    
    print(f"📋 Test query: {test_query}")
    print(f"📍 Test location: {test_location}")
    print(f"📊 Max results: {max_results}")
    print()
    
    # Test Turbo Scraper
    print("🔥 TESTING TURBO SCRAPER")
    print("-" * 30)
    
    start_time = time.time()
    try:
        turbo_leads = await turbo_scrape(test_query, test_location, max_results)
        turbo_duration = time.time() - start_time
        turbo_rate = len(turbo_leads) / turbo_duration if turbo_duration > 0 else 0
        
        print(f"✅ Turbo Results: {len(turbo_leads)} leads in {turbo_duration:.1f}s")
        print(f"📈 Turbo Rate: {turbo_rate:.1f} leads/second")
        
        # Quality analysis
        turbo_high_quality = [l for l in turbo_leads if l.quality_score >= 7]
        turbo_with_websites = [l for l in turbo_leads if l.website]
        turbo_with_emails = [l for l in turbo_leads if l.email]
        
        print(f"🏆 Turbo Quality: {len(turbo_high_quality)}/{len(turbo_leads)} high quality")
        print(f"🌐 Turbo Websites: {len(turbo_with_websites)}/{len(turbo_leads)}")
        print(f"📧 Turbo Emails: {len(turbo_with_emails)}/{len(turbo_leads)}")
        
    except Exception as e:
        print(f"❌ Turbo scraper failed: {e}")
        turbo_leads = []
        turbo_duration = 0
        turbo_rate = 0
    
    print()
    
    # Test Hyper Scraper
    print("⚡ TESTING HYPER SCRAPER")
    print("-" * 30)
    
    start_time = time.time()
    try:
        hyper_leads = await hyper_scrape(test_query, test_location, max_results)
        hyper_duration = time.time() - start_time
        hyper_rate = len(hyper_leads) / hyper_duration if hyper_duration > 0 else 0
        
        print(f"✅ Hyper Results: {len(hyper_leads)} leads in {hyper_duration:.1f}s")
        print(f"📈 Hyper Rate: {hyper_rate:.1f} leads/second")
        
        # Quality analysis
        hyper_high_quality = [l for l in hyper_leads if l.quality_score >= 7]
        hyper_with_websites = [l for l in hyper_leads if l.website]
        hyper_with_emails = [l for l in hyper_leads if l.email]
        
        print(f"🏆 Hyper Quality: {len(hyper_high_quality)}/{len(hyper_leads)} high quality")
        print(f"🌐 Hyper Websites: {len(hyper_with_websites)}/{len(hyper_leads)}")
        print(f"📧 Hyper Emails: {len(hyper_with_emails)}/{len(hyper_leads)}")
        
    except Exception as e:
        print(f"❌ Hyper scraper failed: {e}")
        hyper_leads = []
        hyper_duration = 0
        hyper_rate = 0
    
    print()
    
    # Performance Summary
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 50)
    
    if turbo_duration > 0 and hyper_duration > 0:
        speed_improvement = ((turbo_duration - hyper_duration) / turbo_duration) * 100 if turbo_duration > 0 else 0
        rate_improvement = ((hyper_rate - turbo_rate) / turbo_rate) * 100 if turbo_rate > 0 else 0
        
        print(f"⚡ Speed Improvement: {speed_improvement:.1f}%")
        print(f"📈 Rate Improvement: {rate_improvement:.1f}%")
        print(f"🏆 Winner: {'Hyper' if hyper_duration < turbo_duration else 'Turbo'} Scraper")
    else:
        print("❌ Unable to compare - one or both scrapers failed")
    
    print()
    print("🎯 OPTIMIZATION RECOMMENDATIONS:")
    print("- Hyper scraper uses SQLite caching for better performance")
    print("- Increased browser pool size (8 vs 5)")
    print("- Optimized HTTP connection pooling")
    print("- Smart selector performance tracking")
    print("- Parallel processing with higher concurrency")
    print("- Memory-efficient batch processing")

async def stress_test():
    """Stress test with larger datasets"""
    print("🚀 STRESS TEST")
    print("=" * 30)
    
    test_cases = [
        ("restaurant", "New York, NY", 25),
        ("coffee shop", "San Francisco, CA", 20),
        ("gym", "Los Angeles, CA", 15)
    ]
    
    total_leads = 0
    total_time = 0
    
    for business_type, location, max_results in test_cases:
        print(f"\n🧪 Testing: {business_type} in {location} ({max_results} results)")
        
        start_time = time.time()
        try:
            leads = await hyper_scrape(business_type, location, max_results)
            duration = time.time() - start_time
            
            total_leads += len(leads)
            total_time += duration
            
            print(f"✅ {len(leads)} leads in {duration:.1f}s ({len(leads)/duration:.1f} leads/sec)")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    if total_time > 0:
        avg_rate = total_leads / total_time
        print(f"\n📊 STRESS TEST RESULTS:")
        print(f"   Total leads: {total_leads}")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Average rate: {avg_rate:.1f} leads/second")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stress":
        asyncio.run(stress_test())
    else:
        asyncio.run(compare_scrapers())