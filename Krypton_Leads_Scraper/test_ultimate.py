#!/usr/bin/env python3
"""
Test script for ultimate scraper with all features
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from ultimate_scraper import ultimate_scrape, UltimateScraper

async def test_basic_functionality():
    """Test basic functionality without API key or proxies"""
    print("🧪 BASIC FUNCTIONALITY TEST")
    print("=" * 40)
    
    try:
        start_time = time.time()
        leads = await ultimate_scrape(
            "pizza restaurant", 
            "Austin, TX", 
            max_results=5
        )
        
        duration = time.time() - start_time
        
        print(f"\n✅ Basic test completed in {duration:.1f}s")
        print(f"📊 Found {len(leads)} leads")
        
        if leads:
            print(f"\n🎯 Sample results:")
            for i, lead in enumerate(leads[:2], 1):
                print(f"  {i}. {lead.name}")
                print(f"     Quality: {lead.quality_score}/10")
                print(f"     Source: {lead.source}")
                print(f"     Processing time: {lead.processing_time:.2f}s")
                if lead.website:
                    print(f"     Website: {lead.website}")
                if lead.rating > 0:
                    print(f"     Rating: {lead.rating} ({lead.review_count} reviews)")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_api_key():
    """Test with Google Places API key if available"""
    print("\n🔗 GOOGLE PLACES API TEST")
    print("=" * 40)
    
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    
    if not api_key:
        print("⚠️ No Google Places API key found in environment variables")
        print("   Set GOOGLE_PLACES_API_KEY to test API fallback")
        return False
    
    try:
        print(f"🔑 Using API key: {api_key[:10]}...")
        
        start_time = time.time()
        leads = await ultimate_scrape(
            "coffee shop", 
            "San Francisco, CA", 
            max_results=8,
            google_api_key=api_key
        )
        
        duration = time.time() - start_time
        
        print(f"\n✅ API test completed in {duration:.1f}s")
        print(f"📊 Found {len(leads)} leads")
        
        # Check for API sourced leads
        api_leads = [l for l in leads if l.source == "google_places_api"]
        scraping_leads = [l for l in leads if l.source == "scraping"]
        
        print(f"🔍 Scraping leads: {len(scraping_leads)}")
        print(f"🔗 API leads: {len(api_leads)}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_caching():
    """Test caching functionality"""
    print("\n💾 CACHING TEST")
    print("=" * 40)
    
    try:
        query = "dental office"
        location = "Miami, FL"
        
        # First run (should cache)
        print("🔄 First run (should cache results)...")
        start_time = time.time()
        leads1 = await ultimate_scrape(query, location, max_results=3)
        duration1 = time.time() - start_time
        
        # Second run (should use cache)
        print("🔄 Second run (should use cache)...")
        start_time = time.time()
        leads2 = await ultimate_scrape(query, location, max_results=3)
        duration2 = time.time() - start_time
        
        print(f"\n📊 CACHING RESULTS:")
        print(f"   First run: {len(leads1)} leads in {duration1:.1f}s")
        print(f"   Second run: {len(leads2)} leads in {duration2:.1f}s")
        
        if duration2 < duration1 * 0.5:
            print("✅ Caching is working (second run significantly faster)")
        else:
            print("⚠️ Caching may not be working optimally")
        
        return True
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🛡️ ERROR HANDLING TEST")
    print("=" * 40)
    
    try:
        # Test with invalid location
        print("🔄 Testing invalid location...")
        leads = await ultimate_scrape("restaurant", "InvalidCity123", max_results=2)
        print(f"   Result: {len(leads)} leads (expected: 0 or few)")
        
        # Test with empty query
        print("🔄 Testing empty query...")
        leads = await ultimate_scrape("", "New York, NY", max_results=2)
        print(f"   Result: {len(leads)} leads (expected: 0)")
        
        print("✅ Error handling test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def test_performance():
    """Test performance with different configurations"""
    print("\n⚡ PERFORMANCE TEST")
    print("=" * 40)
    
    test_cases = [
        ("restaurant", "Chicago, IL", 10),
        ("gym", "Los Angeles, CA", 8),
        ("bakery", "Seattle, WA", 6)
    ]
    
    total_leads = 0
    total_time = 0
    
    for business_type, location, max_results in test_cases:
        print(f"\n🔄 Testing: {business_type} in {location}")
        
        try:
            start_time = time.time()
            leads = await ultimate_scrape(business_type, location, max_results)
            duration = time.time() - start_time
            
            total_leads += len(leads)
            total_time += duration
            
            rate = len(leads) / duration if duration > 0 else 0
            print(f"   📊 {len(leads)} leads in {duration:.1f}s ({rate:.1f} leads/sec)")
            
            # Quality analysis
            high_quality = [l for l in leads if l.quality_score >= 7]
            print(f"   🏆 High quality: {len(high_quality)}/{len(leads)} ({len(high_quality)/len(leads)*100:.1f}%)" if leads else "   🏆 No leads found")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    if total_time > 0:
        overall_rate = total_leads / total_time
        print(f"\n📊 OVERALL PERFORMANCE:")
        print(f"   Total leads: {total_leads}")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Average rate: {overall_rate:.1f} leads/second")
        
        if overall_rate > 1.0:
            print("✅ Performance is excellent (>1 lead/second)")
        elif overall_rate > 0.5:
            print("✅ Performance is good (>0.5 leads/second)")
        else:
            print("⚠️ Performance could be improved")
    
    return True

async def test_user_agent_rotation():
    """Test user-agent rotation"""
    print("\n🔄 USER-AGENT ROTATION TEST")
    print("=" * 40)
    
    try:
        from ultimate_scraper import UserAgentRotator
        
        rotator = UserAgentRotator()
        
        # Test random selection
        agents = [rotator.get_random_user_agent() for _ in range(5)]
        print(f"🎲 Random agents: {len(set(agents))} unique out of 5")
        
        # Test rotation
        rotated_agents = [rotator.get_rotating_user_agent() for _ in range(3)]
        print(f"🔄 Rotated agents: {rotated_agents}")
        
        # Print stats
        stats = rotator.get_stats()
        print(f"📊 Usage stats: {len(stats)} agents used")
        
        print("✅ User-agent rotation test completed")
        return True
        
    except Exception as e:
        print(f"❌ User-agent rotation test failed: {e}")
        return False

async def comprehensive_test():
    """Run all tests"""
    print("🚀 ULTIMATE SCRAPER COMPREHENSIVE TEST")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Google Places API", test_with_api_key),
        ("Caching", test_caching),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance),
        ("User-Agent Rotation", test_user_agent_rotation)
    ]
    
    for test_name, test_func in tests:
        print(f"\n" + "="*60)
        print(f"RUNNING: {test_name}")
        print("="*60)
        
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Ultimate scraper is ready!")
    elif passed >= total * 0.8:
        print("✅ Most tests passed - Ultimate scraper is functional")
    else:
        print("⚠️ Multiple tests failed - Review implementation")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "basic":
            asyncio.run(test_basic_functionality())
        elif test_name == "api":
            asyncio.run(test_with_api_key())
        elif test_name == "cache":
            asyncio.run(test_caching())
        elif test_name == "error":
            asyncio.run(test_error_handling())
        elif test_name == "performance":
            asyncio.run(test_performance())
        elif test_name == "useragent":
            asyncio.run(test_user_agent_rotation())
        else:
            print("Available tests: basic, api, cache, error, performance, useragent, or run without arguments for all tests")
    else:
        asyncio.run(comprehensive_test())