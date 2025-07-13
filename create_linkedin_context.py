#!/usr/bin/env python3
"""
Create a new LinkedIn Browserbase context with authentication
Based on Browserbase cookie persistence pattern
"""

import os
import json
import time
from dotenv import load_dotenv
from browserbase import Browserbase
from playwright.sync_api import sync_playwright, Page

load_dotenv()

# Environment variables
API_KEY = os.environ["BROWSERBASE_API_KEY"]
PROJECT_ID = os.environ["BROWSERBASE_PROJECT_ID"]
LINKEDIN_USERNAME = os.environ["LINKEDIN_USERNAME"]
LINKEDIN_PASSWORD = os.environ["LINKEDIN_PASSWORD"]

# LinkedIn URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
LINKEDIN_PROFILE_URL = "https://www.linkedin.com/in/adamanz/recent-activity/all/"

def authenticate_linkedin(page: Page):
    """Authenticate with LinkedIn and handle any verification challenges"""
    print("🔐 Starting LinkedIn authentication...")
    
    # Navigate to login page
    print("   📍 Navigating to login page...")
    page.goto(LINKEDIN_LOGIN_URL)
    
    # Wait for and fill login form
    print("   📝 Filling credentials...")
    page.wait_for_selector("#username", timeout=15000)
    page.fill("#username", LINKEDIN_USERNAME)
    page.fill("#password", LINKEDIN_PASSWORD)
    
    # Submit login
    print("   🚀 Submitting login...")
    page.click('button[type="submit"]')
    
    # Wait for response
    time.sleep(3)  # Give it a moment to process
    
    current_url = page.url
    print(f"   📍 After login URL: {current_url}")
    
    # Handle verification if needed
    if "challenge" in current_url or "checkpoint" in current_url:
        print("   📱 LinkedIn verification required!")
        print("   ⏳ Please complete verification on your LinkedIn mobile app...")
        print("   🔄 Waiting up to 5 minutes for verification...")
        
        # Wait for verification (up to 5 minutes)
        for attempt in range(30):  # 30 * 10 seconds = 5 minutes
            time.sleep(10)
            current_url = page.url
            
            if "challenge" not in current_url and "checkpoint" not in current_url:
                print(f"   ✅ Verification completed after {(attempt + 1) * 10} seconds!")
                break
                
            if attempt % 3 == 0:  # Every 30 seconds
                print(f"   ⏳ Still waiting... ({attempt + 1}/30)")
        else:
            print("   ❌ Verification timeout - you may need to complete it manually")
            return False
    
    # Test authentication by going to feed
    print("   🔍 Testing authentication...")
    page.goto(LINKEDIN_FEED_URL)
    time.sleep(3)  # Wait for page to load
    
    final_url = page.url
    final_title = page.title()
    
    print(f"   📍 Final URL: {final_url}")
    print(f"   📰 Final Title: {final_title}")
    
    # Check if successfully authenticated
    if ("feed" in final_url and "login" not in final_url and 
        "authwall" not in final_url and "sign" not in final_url.lower()):
        print("   ✅ Authentication successful!")
        return True
    else:
        print("   ❌ Authentication failed")
        return False

def test_linkedin_access(page: Page, context_id: str):
    """Test accessing Adam's LinkedIn profile"""
    print("🎯 Testing LinkedIn profile access...")
    
    try:
        # Navigate to Adam's recent activity page
        print(f"   📍 Navigating to: {LINKEDIN_PROFILE_URL}")
        page.goto(LINKEDIN_PROFILE_URL)
        time.sleep(3)  # Wait for page to load
        
        final_url = page.url
        final_title = page.title()
        
        print(f"   📍 Final URL: {final_url}")
        print(f"   📰 Final Title: {final_title}")
        
        # Check if we can access the profile
        if ("authwall" not in final_url and "login" not in final_url and 
            "sign" not in final_url.lower()):
            print("   ✅ Successfully accessing LinkedIn profile!")
            
            # Take a screenshot for verification
            screenshot_path = f"linkedin_authenticated_{int(time.time())}.png"
            page.screenshot(path=screenshot_path)
            print(f"   📸 Screenshot saved: {screenshot_path}")
            
            # Try to scroll and load some content
            print("   📜 Loading page content...")
            for i in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
            
            return True
        else:
            print("   ⚠️  Access limited - may be redirected to authwall")
            return False
            
    except Exception as e:
        print(f"   ❌ Error accessing profile: {e}")
        return False

def main():
    """Main function to create authenticated LinkedIn context"""
    print("🚀 Creating New LinkedIn Browserbase Context")
    print("=" * 60)
    
    try:
        # Initialize Browserbase
        bb = Browserbase(api_key=API_KEY)
        
        # Create a new context
        print("🔧 Creating new Browserbase context...")
        context = bb.contexts.create(project_id=PROJECT_ID)
        context_id = context.id
        
        print(f"✅ Created context: {context_id}")
        print(f"💡 Add to your .env file: LINKEDIN_CONTEXT_ID={context_id}")
        
        # Create session with the new context
        print("🌐 Creating session with context...")
        session = bb.sessions.create(
            project_id=PROJECT_ID,
            browser_settings={
                "context": {
                    "id": context_id,
                    "persist": True  # Important: Save authentication state
                }
            },
            proxies=True  # Enable stealth mode
        )
        
        print(f"✅ Created session: {session.id}")
        
        # Connect with Playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(session.connectUrl)
            context = browser.contexts[0]
            page = context.pages[0]
            
            print(f"🔗 Connected to browser: {browser.browser_type.name} {browser.version}")
            
            # Authenticate with LinkedIn
            auth_success = authenticate_linkedin(page)
            
            if auth_success:
                print("🎉 LinkedIn authentication successful!")
                
                # Test profile access
                profile_access = test_linkedin_access(page, context_id)
                
                # Save results
                results = {
                    "context_id": context_id,
                    "session_id": session.id,
                    "authentication_successful": auth_success,
                    "profile_access_successful": profile_access,
                    "timestamp": time.time(),
                    "linkedin_username": LINKEDIN_USERNAME,
                    "test_url": LINKEDIN_PROFILE_URL
                }
                
                # Save to file
                os.makedirs("data", exist_ok=True)
                results_path = f"data/new_context_results_{int(time.time())}.json"
                with open(results_path, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                
                print(f"📄 Results saved: {results_path}")
                
                print("\n🎯 SUCCESS! Your new LinkedIn context is ready:")
                print(f"📋 Context ID: {context_id}")
                print("💾 Authentication state persisted in Browserbase")
                print("🔄 Future sessions will load instantly!")
                
                print("\n📝 Next Steps:")
                print(f"1. Update your .env file: LINKEDIN_CONTEXT_ID={context_id}")
                print("2. Use this context ID in your ReactionReach application")
                print("3. The context will maintain your LinkedIn session across runs")
                
            else:
                print("❌ LinkedIn authentication failed")
                print("🔧 Please check your credentials and try again")
            
            # Clean up
            browser.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has correct Browserbase credentials")
        print("2. Verify LinkedIn username and password")
        print("3. Ensure you have a stable internet connection")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    print("🏁 RESULT:", "SUCCESS ✅" if success else "FAILED ❌")
    print("=" * 60)