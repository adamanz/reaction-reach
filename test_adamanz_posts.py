#!/usr/bin/env python3
"""
Working test to fetch last 10 LinkedIn posts for linkedin.com/in/adamanz
Uses Playwright directly to validate our approach works
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time

class LinkedInPostFetcher:
    """Test class to fetch LinkedIn posts using Playwright + Browserbase"""
    
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
            "BROWSERBASE_PROJECT_ID"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ Environment variables validated")
    
    def build_activity_url(self):
        """Build LinkedIn activity URL from profile URL"""
        if '/in/' in self.profile_url:
            username = self.profile_url.split('/in/')[-1].rstrip('/')
        else:
            raise ValueError("Invalid LinkedIn profile URL format")
        
        return f"https://www.linkedin.com/in/{username}/recent-activity/all/"
    
    def fetch_posts_with_browserbase(self, max_posts: int = 10):
        """
        Fetch posts using Browserbase + Playwright
        """
        print(f"\\n📊 Fetching last {max_posts} posts from {self.profile_url}...")
        
        # Build activity URL
        activity_url = self.build_activity_url()
        print(f"   🔗 Activity URL: {activity_url}")
        
        # Browserbase connection
        browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
        browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        
        try:
            with sync_playwright() as p:
                print("   🌐 Connecting to Browserbase...")
                
                # Connect to Browserbase
                browser = p.chromium.connect_over_cdp(
                    f"wss://connect.browserbase.com?apiKey={browserbase_api_key}&projectId={browserbase_project_id}"
                )
                
                # Create a new context and page
                context = browser.new_context()
                page = context.new_page()
                
                print("   📄 Navigating to LinkedIn activity page...")
                
                # Navigate to activity page
                page.goto(activity_url, wait_until="networkidle")
                
                # Wait for page to load
                time.sleep(5)
                
                print("   📜 Scrolling to load posts...")
                
                # Scroll to load posts
                for i in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                
                print("   🔍 Extracting post information...")
                
                # Try to extract posts
                posts = []
                
                # Look for post containers (LinkedIn activity feed structure)
                post_selectors = [
                    '[data-urn*="urn:li:activity"]',  # Activity posts
                    '.feed-shared-update-v2',         # Updated feed structure
                    '.occludable-update',             # Legacy feed structure
                    'article[data-id]',               # Alternative selector
                ]
                
                for selector in post_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"   ✅ Found {len(elements)} posts with selector: {selector}")
                            
                            for i, element in enumerate(elements[:max_posts]):
                                try:
                                    # Extract post data
                                    post_data = {
                                        "post_index": i + 1,
                                        "element_selector": selector,
                                        "has_element": True
                                    }
                                    
                                    # Try to get text content
                                    try:
                                        text_content = element.inner_text()
                                        post_data["text_preview"] = text_content[:200] + "..." if len(text_content) > 200 else text_content
                                        post_data["has_text"] = True
                                    except:
                                        post_data["has_text"] = False
                                    
                                    # Try to get reactions
                                    try:
                                        reactions = element.query_selector('[aria-label*="reaction"]')
                                        post_data["has_reactions"] = reactions is not None
                                    except:
                                        post_data["has_reactions"] = False
                                    
                                    # Try to get comments
                                    try:
                                        comments = element.query_selector('[aria-label*="comment"]')
                                        post_data["has_comments"] = comments is not None
                                    except:
                                        post_data["has_comments"] = False
                                    
                                    posts.append(post_data)
                                    
                                except Exception as e:
                                    print(f"   ⚠️  Error extracting post {i+1}: {e}")
                            
                            break  # Found posts with this selector, stop trying others
                    except Exception as e:
                        print(f"   ⚠️  Selector {selector} failed: {e}")
                        continue
                
                if not posts:
                    # Fallback: try to get any visible text content
                    print("   ⚠️  No structured posts found, extracting page content...")
                    page_content = page.content()
                    
                    posts = [{
                        "method": "fallback_page_content",
                        "content_length": len(page_content),
                        "contains_linkedin": "linkedin" in page_content.lower(),
                        "contains_activity": "activity" in page_content.lower(),
                        "preview": page_content[:500] + "..." if len(page_content) > 500 else page_content
                    }]
                
                # Take a screenshot for debugging
                screenshot_path = "debug_linkedin_page.png"
                page.screenshot(path=screenshot_path)
                print(f"   📸 Screenshot saved: {screenshot_path}")
                
                # Clean up
                context.close()
                browser.close()
                
                self.results = {
                    "profile_url": self.profile_url,
                    "activity_url": activity_url,
                    "posts_found": len(posts),
                    "posts": posts,
                    "status": "success" if posts else "no_posts_found",
                    "screenshot_path": screenshot_path
                }
                
                return posts
                
        except Exception as e:
            error_msg = f"Failed to fetch posts: {str(e)}"
            print(f"   ❌ {error_msg}")
            
            self.results = {
                "profile_url": self.profile_url,
                "error": error_msg,
                "status": "failed"
            }
            
            raise
    
    def analyze_results(self):
        """Analyze and display the fetched results"""
        print("\\n📋 Analysis Results:")
        print("=" * 50)
        
        if not self.results:
            print("❌ No results to analyze")
            return
        
        print(f"🎯 Profile: {self.results['profile_url']}")
        print(f"📊 Status: {self.results['status']}")
        
        if self.results['status'] == 'success':
            print(f"📝 Posts found: {self.results['posts_found']}")
            
            for i, post in enumerate(self.results['posts'][:5]):  # Show first 5
                print(f"\\n   Post {i+1}:")
                if 'text_preview' in post:
                    print(f"   - Preview: {post['text_preview']}")
                    print(f"   - Has reactions: {post.get('has_reactions', False)}")
                    print(f"   - Has comments: {post.get('has_comments', False)}")
                elif 'method' in post:
                    print(f"   - Method: {post['method']}")
                    print(f"   - Content length: {post.get('content_length', 0)}")
                    print(f"   - Contains LinkedIn: {post.get('contains_linkedin', False)}")
        
        elif self.results['status'] == 'failed':
            print(f"❌ Error: {self.results.get('error', 'Unknown error')}")
        
        if 'screenshot_path' in self.results:
            print(f"\\n📸 Debug screenshot: {self.results['screenshot_path']}")
    
    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if not filename:
            filename = f"adamanz_posts_{int(time.time())}.json"
        
        results_path = Path("data") / filename
        results_path.parent.mkdir(exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\\n💾 Results saved to: {results_path}")
        return results_path

def main():
    """Main test execution"""
    print("🚀 LinkedIn Post Fetcher Test for adamanz")
    print("=" * 50)
    
    try:
        # Initialize the fetcher
        fetcher = LinkedInPostFetcher("https://linkedin.com/in/adamanz")
        
        # Fetch posts
        posts = fetcher.fetch_posts_with_browserbase(max_posts=10)
        
        # Analyze results
        fetcher.analyze_results()
        
        # Save results
        fetcher.save_results()
        
        print("\\n✅ Test completed successfully!")
        print("\\nNext steps:")
        print("1. Review the saved results file")
        print("2. Check the debug screenshot")
        print("3. If posts were found, proceed with reaction extraction")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ Test failed: {e}")
        print("\\nTroubleshooting:")
        print("1. Check your .env file has valid Browserbase API keys")
        print("2. Ensure linkedin.com/in/adamanz is accessible")
        print("3. Verify Browserbase project is active")
        
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)