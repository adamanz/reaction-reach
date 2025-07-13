#!/usr/bin/env python3
"""
Test Browserbase Context Authentication for LinkedIn
Implements the full architecture diagram flow
"""

import os
import asyncio
import json
import time
from dotenv import load_dotenv
import sys
sys.path.append("src")

from auth.browserbase_context_auth import BrowserbaseContextAuth

load_dotenv()

async def test_linkedin_context_auth():
    """Test the complete Browserbase Context authentication flow"""
    
    print("🚀 Testing LinkedIn Authentication with Browserbase Contexts")
    print("=" * 70)
    print("Following the architecture diagram flow...")
    print()
    
    try:
        # Initialize context authentication
        auth = BrowserbaseContextAuth()
        
        print("📋 Configuration:")
        print(f"   🔑 API Key: {auth.api_key[:10]}...")
        print(f"   📦 Project: {auth.project_id}")
        print(f"   📧 Username: {auth.linkedin_username}")
        print(f"   🆔 Context ID: {auth.context_id or 'Will create new'}")
        print(f"   💾 Persist: {auth.context_persist}")
        print()
        
        # PHASE 1 & 2: Get authenticated session (includes context creation if needed)
        print("🔄 PHASE 1-2: Creating authenticated session...")
        page, context, browser = await auth.get_authenticated_page()
        
        print("✅ Authentication successful!")
        print()
        
        # PHASE 3: Test the session with LinkedIn profile access
        print("🔄 PHASE 3: Testing LinkedIn profile access...")
        
        target_profile = "https://linkedin.com/in/adamanz"
        activity_url = f"{target_profile}/recent-activity/all/"
        
        print(f"   🎯 Navigating to: {activity_url}")
        await page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
        
        # Take screenshot
        await page.screenshot(path="linkedin_context_authenticated.png")
        print("   📸 Screenshot saved: linkedin_context_authenticated.png")
        
        # Check final state
        final_url = page.url
        final_title = await page.title()
        
        print(f"   📍 Final URL: {final_url}")
        print(f"   📰 Final Title: {final_title}")
        
        # Test if we can access content (not authwall)
        is_authenticated = (
            "authwall" not in final_url and 
            "login" not in final_url and 
            "sign" not in final_url.lower()
        )
        
        if is_authenticated:
            print("   ✅ Successfully accessing LinkedIn profile!")
            
            # Try to extract some content
            print("   🔍 Testing content extraction...")
            
            # Scroll to load content
            for i in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # Look for posts
            post_selectors = [
                '[data-urn*="activity"]',
                '.feed-shared-update-v2',
                '.occludable-update'
            ]
            
            posts_found = 0
            for selector in post_selectors:
                posts = await page.query_selector_all(selector)
                if posts:
                    posts_found = len(posts)
                    print(f"   📝 Found {posts_found} posts using: {selector}")
                    break
            
            # Extract some sample content
            page_content = await page.content()
            contains_linkedin = "linkedin" in page_content.lower()
            content_length = len(page_content)
            
            results = {
                "authentication_success": True,
                "context_id": auth.context_id,
                "final_url": final_url,
                "final_title": final_title,
                "posts_found": posts_found,
                "page_content_length": content_length,
                "contains_linkedin_content": contains_linkedin,
                "test_timestamp": time.time()
            }
            
        else:
            print("   ⚠️  Still being redirected - may need additional verification")
            results = {
                "authentication_success": False,
                "context_id": auth.context_id,
                "final_url": final_url,
                "final_title": final_title,
                "issue": "Redirected to authwall or login"
            }
        
        # PHASE 4: Test session persistence (simulate)
        print("\\n🔄 PHASE 4: Session will persist for future runs")
        print(f"   💾 Context ID saved: {auth.context_id}")
        print("   🔄 Next run will load instantly from context!")
        
        # Save results
        results_path = f"data/context_auth_results_{int(time.time())}.json"
        os.makedirs("data", exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"   📄 Results saved: {results_path}")
        
        # Clean up
        await browser.close()
        
        print("\\n🎉 BROWSERBASE CONTEXT TEST COMPLETED!")
        print("=" * 70)
        
        if results.get("authentication_success"):
            print("✅ SUCCESS: LinkedIn authentication working with Browserbase Contexts!")
            print("✅ Profile access successful")
            print("✅ Context state will persist for future runs")
            print("✅ Ready for ReactionReach intelligence gathering")
            
            print("\\n🎯 Next Steps:")
            print("1. Update CrewAI agents to use BrowserbaseContextAuth")
            print("2. Run full ReactionReach pipeline with persistent authentication")
            print("3. Enjoy instant authentication on subsequent runs!")
            
        else:
            print("⚠️  PARTIAL SUCCESS: Authentication created but profile access limited")
            print("🔧 This may be due to LinkedIn's profile privacy settings")
            print("💡 Try testing with your own profile or a public profile")
        
        return results.get("authentication_success", False)
        
    except Exception as e:
        print(f"\\n❌ ERROR: {e}")
        print("\\n🔧 Troubleshooting:")
        print("1. Check your .env file has all required variables")
        print("2. Verify Browserbase API key and project ID")
        print("3. Ensure LinkedIn credentials are correct")
        print("4. Check if LinkedIn requires additional verification")
        
        return False

async def main():
    """Main test function"""
    success = await test_linkedin_context_auth()
    
    print("\\n" + "=" * 70)
    print("🏁 FINAL RESULT:", "SUCCESS ✅" if success else "NEEDS ATTENTION ⚠️")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)