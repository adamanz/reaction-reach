#!/usr/bin/env python3
"""
Test LinkedIn Authentication Flow with Cookie Management
Demonstrates how to fetch authenticated LinkedIn posts for linkedin.com/in/adamanz
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from playwright.async_api import async_playwright

# Add src to path for imports
import sys
sys.path.append("src")

from auth.linkedin_auth import LinkedInAuth, create_authenticated_browserbase_session

class AuthenticatedLinkedInTest:
    """Test LinkedIn authentication and post fetching"""
    
    def __init__(self, profile_url: str = "https://linkedin.com/in/adamanz"):
        load_dotenv()
        self.profile_url = profile_url
        self.results = {}
        
        # Validate environment
        self._validate_environment()
        
    def _validate_environment(self):
        """Validate required environment variables are set"""
        required_vars = [
            "BROWSERBASE_API_KEY",
            "BROWSERBASE_PROJECT_ID",
            "LINKEDIN_USERNAME", 
            "LINKEDIN_PASSWORD"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ Environment variables validated")
        print(f"   📧 LinkedIn Username: {os.getenv('LINKEDIN_USERNAME')}")
        print(f"   🔑 Password: {'*' * len(os.getenv('LINKEDIN_PASSWORD', ''))}")
        print(f"   📦 Browserbase Project: {os.getenv('BROWSERBASE_PROJECT_ID')}")
        print(f"   🍪 Cookie Storage: {os.getenv('SESSION_STORAGE_PATH', './data/linkedin_session.json')}")
    
    def build_activity_url(self):
        """Build LinkedIn activity URL from profile URL"""
        if '/in/' in self.profile_url:
            username = self.profile_url.split('/in/')[-1].rstrip('/')
        else:
            raise ValueError("Invalid LinkedIn profile URL format")
        
        return f"https://www.linkedin.com/in/{username}/recent-activity/all/"
    
    async def test_authentication_flow(self):
        """Test the complete authentication flow"""
        print("\\n🔐 Testing LinkedIn Authentication Flow...")
        
        try:
            # Initialize authentication
            auth = LinkedInAuth()
            
            # Get Browserbase connection with stealth mode
            connect_url, session_config = create_authenticated_browserbase_session()
            print(f"   🌐 Browserbase URL: {connect_url[:50]}...")
            print(f"   🥷 Stealth Mode: {session_config}")
            
            async with async_playwright() as playwright:
                print("   🚀 Connecting to Browserbase...")
                browser = await playwright.chromium.connect_over_cdp(connect_url)
                
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page() if not context.pages else context.pages[0]
                
                # Set viewport
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Test authentication
                print("   🔑 Starting authentication process...")
                authenticated = await auth.authenticate(page, context)
                
                if authenticated:
                    print("   ✅ Authentication successful!")
                    
                    # Test accessing profile
                    activity_url = self.build_activity_url()
                    print(f"   📄 Testing access to: {activity_url}")
                    
                    await page.goto(activity_url, wait_until="networkidle")
                    
                    # Take screenshot for verification
                    screenshot_path = "authenticated_linkedin_page.png"
                    await page.screenshot(path=screenshot_path)
                    print(f"   📸 Screenshot saved: {screenshot_path}")
                    
                    # Try to extract some basic info
                    page_title = await page.title()
                    page_url = page.url
                    
                    # Look for LinkedIn activity content
                    activity_elements = await page.query_selector_all('[data-urn*="activity"]')
                    feed_elements = await page.query_selector_all('.feed-shared-update-v2')
                    
                    self.results = {
                        "authentication": "successful",
                        "profile_url": self.profile_url,
                        "activity_url": activity_url,
                        "final_url": page_url,
                        "page_title": page_title,
                        "activity_elements_found": len(activity_elements),
                        "feed_elements_found": len(feed_elements),
                        "screenshot_path": screenshot_path,
                        "timestamp": time.time()
                    }
                    
                    return True
                    
                else:
                    print("   ❌ Authentication failed")
                    self.results = {
                        "authentication": "failed",
                        "error": "Could not authenticate with LinkedIn"
                    }
                    return False
                    
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            self.results = {
                "authentication": "error",
                "error": str(e)
            }
            return False
    
    async def test_post_extraction(self):
        """Test extracting posts from authenticated session"""
        print("\\n📝 Testing Post Extraction...")
        
        if not self.results.get("authentication") == "successful":
            print("   ❌ Skipping post extraction - authentication not successful")
            return False
        
        try:
            # Use the same authentication and extract posts
            auth = LinkedInAuth()
            connect_url, session_config = create_authenticated_browserbase_session()
            
            async with async_playwright() as playwright:
                browser = await playwright.chromium.connect_over_cdp(connect_url)
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page() if not context.pages else context.pages[0]
                
                # Authenticate
                await auth.authenticate(page, context)
                
                # Navigate to activity page
                activity_url = self.build_activity_url()
                await page.goto(activity_url, wait_until="networkidle")
                
                # Scroll to load more posts
                print("   📜 Scrolling to load posts...")
                for i in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)
                
                # Extract posts
                print("   🔍 Extracting post information...")
                posts = await page.query_selector_all('[data-urn*="activity"]')
                
                if not posts:
                    # Try alternative selectors
                    selectors = ['.feed-shared-update-v2', '.occludable-update', 'article[data-id]']
                    for selector in selectors:
                        posts = await page.query_selector_all(selector)
                        if posts:
                            print(f"   ✅ Found {len(posts)} posts with selector: {selector}")
                            break
                
                extracted_posts = []
                for i, post in enumerate(posts[:10]):
                    try:
                        post_text = await post.text_content()
                        post_html = await post.inner_html()
                        
                        extracted_posts.append({
                            "post_index": i + 1,
                            "text_preview": post_text[:150] + "..." if len(post_text) > 150 else post_text,
                            "has_reactions": "reaction" in post_html.lower(),
                            "has_comments": "comment" in post_html.lower(),
                            "char_length": len(post_text)
                        })
                    except Exception as e:
                        extracted_posts.append({
                            "post_index": i + 1,
                            "error": str(e)
                        })
                
                self.results["posts"] = {
                    "total_found": len(posts),
                    "extracted": extracted_posts,
                    "extraction_successful": len(extracted_posts) > 0
                }
                
                print(f"   📊 Extracted {len(extracted_posts)} posts")
                return len(extracted_posts) > 0
                
        except Exception as e:
            print(f"   ❌ Post extraction failed: {e}")
            self.results["posts"] = {"error": str(e)}
            return False
    
    def analyze_results(self):
        """Analyze and display test results"""
        print("\\n📋 Test Results Analysis:")
        print("=" * 60)
        
        if not self.results:
            print("❌ No results to analyze")
            return
        
        # Authentication results
        auth_status = self.results.get("authentication", "unknown")
        print(f"🔐 Authentication: {auth_status.upper()}")
        
        if auth_status == "successful":
            print(f"   🎯 Profile: {self.results['profile_url']}")
            print(f"   📄 Final URL: {self.results['final_url']}")
            print(f"   📰 Page Title: {self.results['page_title']}")
            print(f"   🔗 Activity Elements: {self.results['activity_elements_found']}")
            print(f"   📺 Feed Elements: {self.results['feed_elements_found']}")
            print(f"   📸 Screenshot: {self.results['screenshot_path']}")
        
        # Post extraction results
        if "posts" in self.results:
            posts_data = self.results["posts"]
            if "error" in posts_data:
                print(f"❌ Post Extraction: Failed - {posts_data['error']}")
            else:
                print(f"📝 Post Extraction: {'SUCCESS' if posts_data['extraction_successful'] else 'PARTIAL'}")
                print(f"   📊 Total Posts Found: {posts_data['total_found']}")
                print(f"   📑 Posts Extracted: {len(posts_data['extracted'])}")
                
                # Show sample posts
                for post in posts_data["extracted"][:3]:
                    if "error" not in post:
                        print(f"   📄 Post {post['post_index']}: {post['text_preview'][:80]}...")
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            filename = f"auth_test_results_{int(time.time())}.json"
        
        results_path = Path("data") / filename
        results_path.parent.mkdir(exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\\n💾 Results saved to: {results_path}")
        return results_path

async def main():
    """Main test execution"""
    print("🚀 LinkedIn Authentication & Post Extraction Test")
    print("=" * 60)
    print("Testing ReactionReach authentication with linkedin.com/in/adamanz")
    print()
    
    try:
        # Initialize test
        test = AuthenticatedLinkedInTest("https://linkedin.com/in/adamanz")
        
        # Test authentication
        auth_success = await test.test_authentication_flow()
        
        if auth_success:
            # Test post extraction
            await test.test_post_extraction()
        
        # Analyze results
        test.analyze_results()
        
        # Save results
        test.save_results()
        
        if auth_success:
            print("\\n🎉 Authentication test completed successfully!")
            print("\\n📋 Next steps:")
            print("1. Review the authentication screenshot")
            print("2. Check extracted post data")
            print("3. Run full ReactionReach pipeline with authenticated access")
            print("4. Monitor session cookie persistence for future runs")
        else:
            print("\\n❌ Authentication test failed!")
            print("\\n🔧 Troubleshooting:")
            print("1. Verify LinkedIn username/password in .env")
            print("2. Check if LinkedIn requires 2FA")
            print("3. Ensure Browserbase project is active")
            print("4. Try clearing stored session cookies")
        
        return auth_success
        
    except Exception as e:
        print(f"\\n💥 Test execution failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)