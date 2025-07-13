#!/usr/bin/env python3
"""
LinkedIn Authentication with Cookie Storage Pattern
Exactly following the Browserbase cookie storage example pattern
"""

import json
import os
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

load_dotenv()

# LinkedIn URLs
LINKEDIN_BASE = "https://www.linkedin.com"
LINKEDIN_LOGIN_URL = f"{LINKEDIN_BASE}/login"
LINKEDIN_FEED_URL = f"{LINKEDIN_BASE}/feed"
LINKEDIN_PROFILE_URL = "https://www.linkedin.com/in/adamanz/recent-activity/all/"

# Credentials from environment
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Cookie storage file - ensure these are well secured!
COOKIE_FILE = "./data/linkedin_cookies.json"

async def store_cookies(browser_tab: Page):
    """Store all LinkedIn cookies to file"""
    # Retrieve all the cookies for LinkedIn
    all_cookies = await browser_tab.context.cookies(LINKEDIN_BASE)
    
    # Ensure data directory exists
    Path(COOKIE_FILE).parent.mkdir(exist_ok=True)
    
    # Store cookies with metadata
    cookie_data = {
        "cookies": all_cookies,
        "timestamp": time.time(),
        "username": LINKEDIN_USERNAME,
        "stored_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(COOKIE_FILE, "w") as cookie_file:
        json.dump(cookie_data, cookie_file, indent=4, default=str)
    
    print(f"✅ Saved {len(all_cookies)} cookie(s) from LinkedIn")
    return len(all_cookies)

async def restore_cookies(browser_tab: Page):
    """Restore cookies from file to browser context"""
    try:
        with open(COOKIE_FILE) as cookie_file:
            cookie_data = json.load(cookie_file)
        
        cookies = cookie_data.get("cookies", [])
        stored_time = cookie_data.get("timestamp", 0)
        
        # Check if cookies are still fresh (within 24 hours)
        age_hours = (time.time() - stored_time) / 3600
        if age_hours > 24:
            print(f"⚠️  Cookies are {age_hours:.1f} hours old - may need refresh")
        
        await browser_tab.context.add_cookies(cookies)
        print(f"✅ Restored {len(cookies)} cookie(s) to browser context")
        return len(cookies)
        
    except FileNotFoundError:
        print("📝 No stored cookies found - will need to authenticate")
        return 0

async def authenticate(browser_tab: Page):
    """Navigate to LinkedIn login page and authenticate"""
    print("🔐 Starting LinkedIn authentication...")
    
    # Navigate to the sign-in page
    await browser_tab.goto(LINKEDIN_LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
    print("📄 Navigated to LinkedIn login page")
    
    # Wait for login form
    await browser_tab.wait_for_selector("#username", timeout=30000)
    
    # Fill credentials
    print("📝 Filling login credentials...")
    await browser_tab.fill("#username", LINKEDIN_USERNAME)
    await asyncio.sleep(1)  # Human-like delay
    await browser_tab.fill("#password", LINKEDIN_PASSWORD)
    await asyncio.sleep(1)
    
    # Take screenshot before submitting
    await browser_tab.screenshot(path="linkedin_login_filled.png")
    print("📸 Login form screenshot saved")
    
    # Submit login form
    print("🚀 Submitting login form...")
    await browser_tab.click('button[type="submit"]')
    
    # Wait for navigation after login
    await asyncio.sleep(5)
    
    # Take screenshot after login attempt
    await browser_tab.screenshot(path="linkedin_after_login.png")
    print("📸 Post-login screenshot saved")
    
    # Check if we need app verification
    current_url = browser_tab.url
    if "challenge" in current_url or "checkpoint" in current_url:
        print("📱 LinkedIn app verification required!")
        print("⏳ Please check your LinkedIn mobile app and approve the sign-in")
        print("🔄 Waiting for verification completion...")
        
        # Wait for verification (check every 10 seconds)
        for attempt in range(30):  # 5 minutes max
            await asyncio.sleep(10)
            current_url = browser_tab.url
            
            if "challenge" not in current_url and "checkpoint" not in current_url:
                print(f"✅ Verification completed after {(attempt + 1) * 10} seconds!")
                break
            
            print(f"⏳ Still waiting... ({attempt + 1}/30)")
        else:
            print("❌ Verification timeout - please try again")
            return False
    
    # Store the cookies after successful authentication
    cookie_count = await store_cookies(browser_tab)
    
    print(f"🎉 Authentication successful! Stored {cookie_count} cookies")
    return True

async def run(browser_tab: Page):
    """Main execution function following the Browserbase pattern"""
    print("🚀 Starting LinkedIn session...")
    
    # Load up any stored cookies first
    restored_count = await restore_cookies(browser_tab)
    
    # Try to access a protected LinkedIn page (feed)
    print("📊 Attempting to access LinkedIn feed...")
    await browser_tab.goto(LINKEDIN_FEED_URL, wait_until="domcontentloaded", timeout=60000)
    
    current_url = browser_tab.url
    page_title = await browser_tab.title()
    
    print(f"📍 Current URL: {current_url}")
    print(f"📰 Page Title: {page_title}")
    
    # Check if we were redirected to login (authentication needed)
    if ("login" in current_url or "authwall" in current_url or 
        "sign" in current_url.lower() or page_title == "LinkedIn Login, Sign in | LinkedIn"):
        
        print("🔑 Authentication required - redirected to login")
        
        # Authenticate
        auth_success = await authenticate(browser_tab)
        if not auth_success:
            print("❌ Authentication failed")
            return False
        
        # Try accessing the feed again
        print("🔄 Retrying feed access after authentication...")
        await browser_tab.goto(LINKEDIN_FEED_URL, wait_until="domcontentloaded", timeout=60000)
        
        current_url = browser_tab.url
        page_title = await browser_tab.title()
    
    # Now try to access the target profile
    print(f"🎯 Accessing target profile: {LINKEDIN_PROFILE_URL}")
    await browser_tab.goto(LINKEDIN_PROFILE_URL, wait_until="domcontentloaded", timeout=60000)
    
    final_url = browser_tab.url
    final_title = await browser_tab.title()
    
    # Take final screenshot
    await browser_tab.screenshot(path="linkedin_final_page.png")
    
    print(f"🏁 Final URL: {final_url}")
    print(f"📰 Final Title: {final_title}")
    
    # Check for posts on the page
    print("🔍 Looking for posts...")
    
    # Scroll to load content
    for i in range(3):
        await browser_tab.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
    
    # Try different post selectors
    post_selectors = [
        '[data-urn*="activity"]',
        '.feed-shared-update-v2', 
        '.occludable-update',
        'article[data-id]'
    ]
    
    posts_found = 0
    for selector in post_selectors:
        posts = await browser_tab.query_selector_all(selector)
        if posts:
            posts_found = len(posts)
            print(f"📝 Found {posts_found} posts using selector: {selector}")
            break
    
    if posts_found == 0:
        print("⚠️  No posts found - may need different approach or authentication")
    
    # Save results
    results = {
        "success": True,
        "final_url": final_url,
        "final_title": final_title,
        "posts_found": posts_found,
        "cookies_restored": restored_count,
        "timestamp": time.time()
    }
    
    results_path = f"data/linkedin_session_results_{int(time.time())}.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Results saved to: {results_path}")
    return True

async def main():
    """Main function using Browserbase connection"""
    print("🌐 Connecting to Browserbase...")
    
    # Get Browserbase credentials
    api_key = os.getenv("BROWSERBASE_API_KEY")
    project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    
    if not api_key or not project_id:
        print("❌ Missing Browserbase credentials in .env file")
        return False
    
    if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
        print("❌ Missing LinkedIn credentials in .env file")
        return False
    
    # Connect to Browserbase with stealth mode
    connect_url = f"wss://connect.browserbase.com?apiKey={api_key}&projectId={project_id}&enableProxy=true"
    
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.connect_over_cdp(connect_url)
            
            print(f"✅ Connected to Browserbase - {browser.browser_type.name} version {browser.version}")
            
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            browser_tab = await context.new_page() if not context.pages else context.pages[0]
            
            # Set extended timeout
            browser_tab.set_default_timeout(60000)
            
            try:
                # Perform our LinkedIn operations
                success = await run(browser_tab)
                
                if success:
                    print("\\n🎉 LinkedIn session completed successfully!")
                    print("✅ Cookies stored for future use")
                    print("📊 Ready for ReactionReach intelligence gathering")
                else:
                    print("\\n❌ LinkedIn session failed")
                
                return success
                
            finally:
                # Clean up
                await browser_tab.close()
                await browser.close()
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)