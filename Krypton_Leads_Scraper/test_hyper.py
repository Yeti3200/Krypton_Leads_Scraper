#!/usr/bin/env python3
"""
Test script for hyper-optimized scraper
"""

import asyncio
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from hyper_scraper import hyper_scrape

async def performance_test():
    """Performance test comparing different configurations"""
    print("⚡ HYPER SCRAPER PERFORMANCE TEST")
    print("=" * 50)
    
    test_cases = [
        ("pizza", "Austin, TX", 10),
        ("coffee shop", "San Francisco, CA", 15),
        ("dental office", "Miami, FL", 8)
    ]
    
    for business_type, location, max_results in test_cases:
        print(f"\n🧪 Testing: {business_type} in {location}")
        print(f"📊 Max results: {max_results}")
        
        start_time = time.time()
        
        try:
            leads = await hyper_scrape(business_type, location, max_results)
            
            duration = time.time() - start_time
            rate = len(leads) / duration if duration > 0 else 0
            
            print(f"✅ Results: {len(leads)} leads in {duration:.1f}s")
            print(f"📈 Rate: {rate:.1f} leads/second")
            
            # Quality analysis
            high_quality = [l for l in leads if l.quality_score >= 7]
            with_websites = [l for l in leads if l.website]
            with_emails = [l for l in leads if l.email]
            
            print(f"🏆 High quality: {len(high_quality)}/{len(leads)} ({len(high_quality)/len(leads)*100:.1f}%)")
            print(f"🌐 With websites: {len(with_websites)}/{len(leads)} ({len(with_websites)/len(leads)*100:.1f}%)")
            print(f"📧 With emails: {len(with_emails)}/{len(leads)} ({len(with_emails)/len(leads)*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)

async def quick_test():
    """Quick functionality test"""
    print("⚡ QUICK HYPER SCRAPER TEST")
    print("=" * 30)
    
    try:
        leads = await hyper_scrape("restaurant", "New York, NY", max_results=5)
        
        print(f"\n🎉 SUCCESS: Found {len(leads)} leads")
        
        for i, lead in enumerate(leads[:3], 1):
            print(f"\n{i}. {lead.name}")
            print(f"   Quality: {lead.quality_score}/10")
            print(f"   Processing time: {lead.processing_time:.2f}s")
            if lead.website:
                print(f"   Website: {lead.website}")
            if lead.phone:
                print(f"   Phone: {lead.phone}")
            if lead.email:
                print(f"   Email: {lead.email}")
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "performance":
        asyncio.run(performance_test())
    else:
        asyncio.run(quick_test())