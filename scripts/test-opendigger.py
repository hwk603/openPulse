#!/usr/bin/env python3
"""
Test OpenDigger API connectivity and data fetching
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_collection.opendigger_client import OpenDiggerClient


async def test_opendigger():
    """Test OpenDigger API"""
    print("🔍 Testing OpenDigger API Connection")
    print("=" * 50)
    print("")

    client = OpenDiggerClient()

    # Test repository
    test_repo = {
        "platform": "github",
        "owner": "apache",
        "repo": "iotdb"
    }

    print(f"📦 Testing with repository: {test_repo['owner']}/{test_repo['repo']}")
    print("")

    # Test OpenRank
    print("1️⃣  Fetching OpenRank data...")
    try:
        openrank = await client.get_openrank(**test_repo)
        if openrank:
            latest_date = max(openrank.keys())
            latest_value = openrank[latest_date]
            print(f"   ✅ OpenRank: {latest_value:.2f} (as of {latest_date})")
        else:
            print("   ⚠️  No OpenRank data available")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Activity
    print("2️⃣  Fetching Activity data...")
    try:
        activity = await client.get_activity(**test_repo)
        if activity:
            latest_date = max(activity.keys())
            latest_value = activity[latest_date]
            print(f"   ✅ Activity: {latest_value:.2f} (as of {latest_date})")
        else:
            print("   ⚠️  No Activity data available")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Contributors
    print("3️⃣  Fetching Contributors data...")
    try:
        contributors = await client.get_contributors(**test_repo)
        if contributors:
            print(f"   ✅ Found {len(contributors)} contributors")
            # Show top 5
            sorted_contributors = sorted(
                contributors.items(),
                key=lambda x: sum(x[1].values()) if ince(x[1], dict) else 0,
                reverse=True
            )[:5]
            print("   Top 5 contributors:")
            for username, data in sorted_contributors:
                if isinstance(data, dict):
                    total = sum(data.values())
                    print(f"      - {username}: {total:.0f} contributions")
        else:
            print("   ⚠️  No Contributors data available")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Stars
    print("4️⃣  Fetching Stars data...")
    try:
        stars = await client.get_stars(**test_repo)
        if stars:
            latest_date = max(stars.keys())
            latest_value = stars[latest_date]
            print(f"   ✅ Stars: {latest_value:.0f} (as of {latest_date})")
        else:
            print("   ⚠️  No Stars data available")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Forks
    print("5️⃣  Fetching Forks data...")
    try:
        forks = await client.get_forks(**test_repo)
        if forks:
            latest_date = max(forks.keys(n            latest_value = forks[latest_date]
            print(f"   ✅ Forks: {latest_value:.0f} (as of {latest_date})")
        else:
            print("   ⚠️  No Forks data available")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Issue Response Time
    print("6️⃣  Fetching Issue Response Time...")
    try:
        response_time = await client.get_issue_response_time(**test_repo)
        if response_time:
            latest_date = max(response_time.keys())
            latest_value = response_time[latest_date]
            print(f"   ✅ Avg Response Tiest_value:.2f} hours (as of {latest_date})")
        else:
            print("   ⚠️  No Response Time data available")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("")
    print("=" * 50)
    print("🎉 OpenDigger API test completed!")
    print("")
    print("If all tests passed, OpenDigger integration is working correctly.")
    print("If some tests failed, check:")
    print("  1. Internet connectivity")
    print("  2. OpenDigger API status: https://oss.x-lab.info/open_digger")
    print("  3. Repository exists and has data")


if __name__ == "__main__":
    asyncio.run(test_opendigger())
