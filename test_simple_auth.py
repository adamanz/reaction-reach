#!/usr/bin/env python3
"""
Simplified LinkedIn Authentication Test with Extended Timeouts
Focus on connection and cookie storage
"""

import os
import json
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

class SimpleLinkedInAuth:
    """Simplified LinkedIn authentication test"""
    
    def __init__(self):
        self.results = {}
        self.session_path = "./data/linkedin_session.json"
        Path(self.session_path).parent.mkdir(exist_ok=True)
    
    async def test_connection(self):
        """Test basic Browserbase connection"""
        print("🌐 Testing Browserbase Connection...")
        
        try:
            browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
            browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
            
            # Build connection URL with extended timeouts
            connect_url = f"wss://connect.browserbase.com?apiKey={browserbase_api_key}&projectId={browserbase_project_id}&enableProxy=true"
            
            async with async_playwright() as playwright:
                print("   🚀 Connecting to Browserbase...")
                browser = await playwright.chromium.connect_over_cdp(connect_url)
                
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page() if not context.pages else context.pages[0]
                
                # Set extended timeout
                page.set_default_timeout(60000)  # 60 seconds
                
                print("   📄 Testing navigation to LinkedIn...")
                
                # Try simple LinkedIn homepage first
                try:
                    await page.goto("https://www.linkedin.com", wait_until="domcontentloaded", timeout=60000)
                    print("   ✅ Successfully reached LinkedIn homepage")
                    
                    # Take screenshot
                    await page.screenshot(path="linkedin_homepage.png")
                    print("   📸 Screenshot saved: linkedin_homepage.png")
                    
                    # Get page info
                    title = await page.title()
                    url = page.url
                    
                    print(f"   📰 Page Title: {title}")
                    print(f"   🔗 Final URL: {url}")
                    
                    # Try to navigate to login page
                    print("   🔑 Navigating to login page...")
                    await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=60000)
                    
                    # Take login page screenshot
                    await page.screenshot(path="linkedin_login.png")
                    print("   📸 Login page screenshot saved: linkedin_login.png")
                    
                    # Try to fill credentials with more time
                    print("   📝 Looking for login form...")
                    await page.wait_for_selector("#username", timeout=30000)
                    
                    username = os.getenv("LINKEDIN_USERNAME")
                    password = os.getenv("LINKEDIN_PASSWORD")
                    
                    print("   ✍️ Filling credentials...")
                    await page.fill("#username", username)
                    await asyncio.sleep(2)  # Human-like delay
                    await page.fill("#password", password)
                    await asyncio.sleep(2)
                    
                    # Take screenshot before submitting
                    await page.screenshot(path="linkedin_before_submit.png")
                    print("   📸 Pre-submit screenshot saved")
                    
                    print("   🚀 Submitting login form...")
                    await page.click('button[type="submit"]')
                    
                    # Wait longer for login to process
                    print("   ⏳ Waiting for login to process...")
                    await asyncio.sleep(10)
                    
                    # Take screenshot after submit
                    await page.screenshot(path="linkedin_after_submit.png")
                    print("   📸 Post-submit screenshot saved")
                    
                    # Check final URL and title
                    final_url = page.url
                    final_title = await page.title()
                    
                    print(f"   📰 Final Title: {final_title}")
                    print(f"   🔗 Final URL: {final_url}")
                    
                    # Check if we're authenticated (not on login page)
                    is_authenticated = "login" not in final_url and "sign-in" not in final_url
                    
                    if is_authenticated:
                        print("   ✅ Authentication appears successful!")
                        
                        # Store cookies
                        cookies = await context.cookies()
                        session_data = {
                            "cookies": cookies,
                            "timestamp": time.time(),
                            "final_url": final_url,
                            "final_title": final_title,
                            "username": username
                        }
                        
                        with open(self.session_path, 'w') as f:
                            json.dump(session_data, f, indent=2, default=str)
                        
                        print(f"   💾 Session cookies stored: {self.session_path}")
                        print(f"   🍪 Stored {len(cookies)} cookies")
                        
                        self.results = {
                            "status": "success",
                            "final_url": final_url,
                            "final_title": final_title,
                            "cookies_stored": len(cookies),
                            "session_path": self.session_path
                        }
                        
                    else:
                        print("   ⚠️ Still on login page - authentication may have failed")
                        self.results = {
                            "status": "partial",
                            "final_url": final_url,
                            "final_title": final_title,
                            "note": "Still on login page"
                        }
                    
                    await browser.close()
                    return is_authenticated
                    
                except Exception as nav_error:
                    print(f"   ❌ Navigation error: {nav_error}")
                    await page.screenshot(path="linkedin_error.png")
                    print("   📸 Error screenshot saved")
                    self.results = {"status": "error", "error": str(nav_error)}
                    return False
                    
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            self.results = {"status": "connection_error", "error": str(e)}
            return False
    
    def save_results(self):
        """Save test results"""
        results_path = f"data/simple_auth_results_{int(time.time())}.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"💾 Results saved: {results_path}")

async def main():
    """Run simplified authentication test"""
    print("🚀 Simplified LinkedIn Authentication Test")
    print("=" * 50)
    
    auth = SimpleLinkedInAuth()
    success = await auth.test_connection()
    auth.save_results()
    
    if success:
        print("\n🎉 Authentication test successful!")
        print("✅ Cookies have been stored for future use")
        print("🔍 Check the screenshots to verify the process")
    else:
        print("\n❌ Authentication test failed")
        print("📸 Check error screenshots for debugging")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())