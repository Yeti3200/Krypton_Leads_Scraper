#!/usr/bin/env python3
"""
Quick test of turbo scraper
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from turbo_scraper import turbo_scrape

async def quick_test():
    """Test turbo scraper with minimal search"""
    print("⚡ TESTING TURBO SCRAPER...")
    
    try:
        # Quick test with small search
        leads = await turbo_scrape("pizza", "Austin, TX", max_results=5)
        
        print(f"\n🎉 TEST RESULTS:")
        print(f"Found {len(leads)} leads")
        
        for i, lead in enumerate(leads[:3], 1):
            print(f"\n{i}. {lead.name}")
            print(f"   Quality: {lead.quality_score}/10")
            if lead.website:
                print(f"   Website: {lead.website}")
            if lead.phone:
                print(f"   Phone: {lead.phone}")
            if lead.email:
                print(f"   Email: {lead.email}")
        
        print("✅ Turbo scraper test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_test())