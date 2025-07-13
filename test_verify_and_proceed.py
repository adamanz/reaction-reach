#!/usr/bin/env python3
"""
LinkedIn Authentication with App Verification Handler
Waits for user to complete app verification then proceeds with post extraction
"""

import os
import json
import time
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

class LinkedInVerificationHandler:
    """Handle LinkedIn app verification and proceed with authenticated actions"""
    
    def __init__(self):
        self.session_path = "./data/linkedin_session.json"
        self.results = {}
    
    async def load_and_verify_session(self):
        """Load stored session and handle verification if needed"""
        print("🔐 Loading stored LinkedIn session...")
        
        try:
            # Load stored session
            with open(self.session_path, 'r') as f:
                session_data = json.load(f)
            
            cookies = session_data.get("cookies", [])
            print(f"   🍪 Found {len(cookies)} stored cookies")
            
            browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
            browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
            connect_url = f"wss://connect.browserbase.com?apiKey={browserbase_api_key}&projectId={browserbase_project_id}&enableProxy=true"
            
            async with async_playwright() as playwright:
                print("   🚀 Connecting to Browserbase...")
                browser = await playwright.chromium.connect_over_cdp(connect_url)
                
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page() if not context.pages else context.pages[0]
                
                # Load stored cookies
                await context.add_cookies(cookies)
                print("   ✅ Loaded stored cookies")
                
                # Try to access LinkedIn feed
                print("   📄 Testing access to LinkedIn...")
                await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)
                
                current_url = page.url
                page_title = await page.title()
                
                print(f"   🔗 Current URL: {current_url}")
                print(f"   📰 Page Title: {page_title}")
                
                # Check if we need verification
                if "challenge" in current_url or "checkpoint" in current_url:
                    print("   🔔 LinkedIn App Verification Required!")
                    print("   📱 Please check your LinkedIn mobile app and tap 'Yes' to approve this sign-in")
                    print("   ⏳ Waiting for verification... (checking every 10 seconds)")
                    
                    # Take screenshot of verification page
                    await page.screenshot(path="linkedin_verification_required.png")
                    print("   📸 Verification screenshot saved")
                    
                    # Wait for verification (check every 10 seconds for up to 5 minutes)
                    verification_success = False
                    for attempt in range(30):  # 30 attempts * 10 seconds = 5 minutes
                        await asyncio.sleep(10)
                        
                        # Check if URL changed (verification completed)
                        await page.reload()
                        current_url = page.url
                        page_title = await page.title()
                        
                        print(f"   🔍 Attempt {attempt + 1}: {current_url}")
                        
                        if "challenge" not in current_url and "checkpoint" not in current_url:
                            print("   ✅ Verification completed!")
                            verification_success = True
                            break
                    
                    if not verification_success:
                        print("   ❌ Verification timeout - please try again")
                        return False
                
                # If we're here, we should be authenticated
                print("   🎉 Authentication successful!")
                
                # Save updated cookies
                updated_cookies = await context.cookies()
                session_data["cookies"] = updated_cookies
                session_data["last_verified"] = time.time()
                
                with open(self.session_path, 'w') as f:
                    json.dump(session_data, f, indent=2, default=str)
                
                print(f"   💾 Updated session saved with {len(updated_cookies)} cookies")
                
                # Now try to access the target profile
                profile_url = "https://linkedin.com/in/adamanz"
                activity_url = f"https://www.linkedin.com/in/adamanz/recent-activity/all/"
                
                print(f"   📊 Accessing target profile: {profile_url}")
                await page.goto(activity_url, wait_until="domcontentloaded", timeout=60000)
                
                # Take screenshot of profile page
                await page.screenshot(path="linkedin_authenticated_profile.png")
                print("   📸 Profile page screenshot saved")
                
                final_url = page.url
                final_title = await page.title()
                
                print(f"   🎯 Final URL: {final_url}")
                print(f"   📰 Final Title: {final_title}")
                
                # Try to extract some posts
                print("   📝 Looking for posts...")
                
                # Scroll to load content
                for i in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                
                # Look for post elements
                post_selectors = [
                    '[data-urn*="activity"]',
                    '.feed-shared-update-v2',
                    '.occludable-update',
                    'article[data-id]'
                ]
                
                posts_found = 0
                for selector in post_selectors:
                    posts = await page.query_selector_all(selector)
                    if posts:
                        posts_found = len(posts)
                        print(f"   ✅ Found {posts_found} posts using selector: {selector}")
                        break
                
                # Extract some basic post info
                extracted_posts = []
                if posts_found > 0:
                    for i, post in enumerate(posts[:5]):  # First 5 posts
                        try:
                            post_text = await post.text_content()
                            if post_text and len(post_text.strip()) > 0:
                                extracted_posts.append({
                                    "index": i + 1,
                                    "preview": post_text[:100] + "..." if len(post_text) > 100 else post_text,
                                    "length": len(post_text)
                                })
                        except:
                            continue
                
                print(f"   📊 Extracted {len(extracted_posts)} posts with content")
                
                self.results = {
                    "authentication": "success",
                    "verification_completed": True,
                    "final_url": final_url,
                    "final_title": final_title,
                    "posts_found": posts_found,
                    "posts_extracted": extracted_posts,
                    "cookies_updated": len(updated_cookies),
                    "timestamp": time.time()
                }
                
                await browser.close()
                return True
                
        except FileNotFoundError:
            print("   ❌ No stored session found - please run authentication first")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results = {"error": str(e)}
            return False
    
    def save_results(self):
        """Save results"""
        results_path = f"data/verification_results_{int(time.time())}.json"
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"💾 Results saved: {results_path}")

async def main():
    """Run verification and post extraction"""
    print("🚀 LinkedIn Verification & Post Extraction")
    print("=" * 50)
    print("📱 Make sure you have your LinkedIn mobile app ready!")
    print()
    
    handler = LinkedInVerificationHandler()
    success = await handler.load_and_verify_session()
    handler.save_results()
    
    if success:
        print("\n🎉 SUCCESS! LinkedIn authentication and post extraction completed!")
        print("✅ Your session is now fully authenticated")
        print("📊 Posts have been extracted from linkedin.com/in/adamanz")
        print("🔍 Check the screenshots to see the authenticated pages")
        print("\n🎯 Next: Run the full ReactionReach pipeline!")
    else:
        print("\n❌ Authentication/verification failed")
        print("🔧 Please check the error messages above")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())