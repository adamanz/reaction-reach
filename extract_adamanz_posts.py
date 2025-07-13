#!/usr/bin/env python3
"""
Extract Last 10 LinkedIn Posts for adamanz
Uses authenticated Browserbase Context for instant access
"""

import os
import asyncio
import json
import time
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import sys
sys.path.append("src")

from auth.browserbase_context_auth import BrowserbaseContextAuth

load_dotenv()

class LinkedInPostExtractor:
    """Extract LinkedIn posts using authenticated Browserbase Context"""
    
    def __init__(self, profile_username: str = "adamanz"):
        self.profile_username = profile_username
        self.profile_url = f"https://linkedin.com/in/{profile_username}"
        self.activity_url = f"{self.profile_url}/recent-activity/all/"
        self.auth = BrowserbaseContextAuth()
        self.extracted_posts = []
    
    async def extract_posts(self, max_posts: int = 10):
        """Extract posts using authenticated context"""
        print(f"🚀 Extracting last {max_posts} posts from {self.profile_url}")
        print("=" * 60)
        
        try:
            # Get authenticated session (should be instant due to context)
            print("🔐 Loading authenticated session from context...")
            page, context, browser = await self.auth.get_authenticated_page()
            
            print("✅ Authentication loaded from context!")
            print()
            
            # Navigate to activity page
            print(f"📊 Navigating to activity page...")
            print(f"   🔗 URL: {self.activity_url}")
            
            await page.goto(self.activity_url, wait_until="domcontentloaded", timeout=60000)
            
            # Take screenshot for verification
            await page.screenshot(path="linkedin_posts_page.png")
            print("   📸 Screenshot saved: linkedin_posts_page.png")
            
            current_url = page.url
            page_title = await page.title()
            
            print(f"   📍 Final URL: {current_url}")
            print(f"   📰 Page Title: {page_title}")
            print()
            
            # Check if we have access
            if "authwall" in current_url or "login" in current_url:
                print("⚠️  Still hitting authwall - may need public profile or different approach")
                return []
            
            # Scroll to load posts
            print("📜 Scrolling to load recent posts...")
            for i in range(5):  # More scrolls to get more posts
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)  # Longer wait for content to load
                print(f"   📜 Scroll {i+1}/5 completed")
            
            print()
            print("🔍 Extracting post data...")
            
            # Try multiple selectors for LinkedIn posts
            post_selectors = [
                '[data-urn*="urn:li:activity"]',
                '.feed-shared-update-v2',
                '.occludable-update', 
                'article[data-id]',
                '.update-components-article',
                '[data-urn*="activity"]'
            ]
            
            all_posts = []
            for selector in post_selectors:
                posts = await page.query_selector_all(selector)
                if posts:
                    print(f"   ✅ Found {len(posts)} posts using selector: {selector}")
                    all_posts = posts
                    break
            
            if not all_posts:
                print("   ⚠️  No posts found with standard selectors, trying alternative extraction...")
                
                # Try to extract any content that looks like posts
                content_elements = await page.query_selector_all('div[class*="update"], div[class*="post"], div[class*="activity"]')
                print(f"   🔍 Found {len(content_elements)} potential content elements")
                all_posts = content_elements[:max_posts] if content_elements else []
            
            # Extract post information
            print(f"   📝 Extracting data from {min(len(all_posts), max_posts)} posts...")
            
            for i, post_element in enumerate(all_posts[:max_posts]):
                try:
                    print(f"   📄 Processing post {i+1}/{min(len(all_posts), max_posts)}...")
                    
                    # Get post text content
                    post_text = await post_element.text_content()
                    if not post_text or len(post_text.strip()) < 10:
                        print(f"      ⚠️  Post {i+1}: No meaningful text content")
                        continue
                    
                    # Get post HTML for additional analysis
                    post_html = await post_element.inner_html()
                    
                    # Extract post metadata
                    post_data = {
                        "post_index": i + 1,
                        "text_content": post_text.strip(),
                        "text_preview": post_text.strip()[:200] + "..." if len(post_text.strip()) > 200 else post_text.strip(),
                        "character_count": len(post_text.strip()),
                        "word_count": len(post_text.strip().split()),
                        "contains_links": "http" in post_text or "linkedin.com" in post_text,
                        "has_reactions": any(word in post_html.lower() for word in ["like", "reaction", "👍", "❤️"]),
                        "has_comments": any(word in post_html.lower() for word in ["comment", "reply"]),
                        "has_shares": "share" in post_html.lower(),
                        "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "extraction_method": "browserbase_context"
                    }
                    
                    # Try to extract timestamp if available
                    try:
                        time_elements = await post_element.query_selector_all('time, [class*="time"], [class*="date"]')
                        if time_elements:
                            time_text = await time_elements[0].text_content()
                            post_data["timestamp_text"] = time_text.strip()
                    except:
                        pass
                    
                    # Try to extract engagement metrics
                    try:
                        reaction_elements = await post_element.query_selector_all('[aria-label*="reaction"], [class*="reaction"]')
                        if reaction_elements:
                            reaction_text = await reaction_elements[0].text_content()
                            post_data["reaction_text"] = reaction_text.strip()
                    except:
                        pass
                    
                    self.extracted_posts.append(post_data)
                    print(f"      ✅ Post {i+1}: {post_data['word_count']} words, {post_data['character_count']} chars")
                    
                except Exception as e:
                    print(f"      ❌ Error extracting post {i+1}: {e}")
                    continue
            
            # Clean up
            await browser.close()
            
            print()
            print(f"✅ Extraction completed! Found {len(self.extracted_posts)} posts")
            return self.extracted_posts
            
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return []
    
    def analyze_posts(self):
        """Analyze extracted posts"""
        if not self.extracted_posts:
            print("❌ No posts to analyze")
            return
        
        print("📊 POST ANALYSIS")
        print("=" * 60)
        
        total_posts = len(self.extracted_posts)
        total_words = sum(post.get('word_count', 0) for post in self.extracted_posts)
        total_chars = sum(post.get('character_count', 0) for post in self.extracted_posts)
        posts_with_reactions = sum(1 for post in self.extracted_posts if post.get('has_reactions', False))
        posts_with_comments = sum(1 for post in self.extracted_posts if post.get('has_comments', False))
        posts_with_links = sum(1 for post in self.extracted_posts if post.get('contains_links', False))
        
        print(f"📝 Total Posts: {total_posts}")
        print(f"📖 Total Words: {total_words:,}")
        print(f"🔤 Total Characters: {total_chars:,}")
        print(f"📊 Average Words per Post: {total_words/total_posts:.1f}")
        print(f"💝 Posts with Reactions: {posts_with_reactions}/{total_posts}")
        print(f"💬 Posts with Comments: {posts_with_comments}/{total_posts}")
        print(f"🔗 Posts with Links: {posts_with_links}/{total_posts}")
        print()
        
        print("📋 POST PREVIEWS:")
        print("-" * 60)
        for i, post in enumerate(self.extracted_posts, 1):
            print(f"Post {i}:")
            print(f"   📝 Preview: {post['text_preview']}")
            print(f"   📊 Stats: {post['word_count']} words, {post['character_count']} chars")
            
            features = []
            if post.get('has_reactions'): features.append("💝 Reactions")
            if post.get('has_comments'): features.append("💬 Comments") 
            if post.get('contains_links'): features.append("🔗 Links")
            
            if features:
                print(f"   🎯 Features: {', '.join(features)}")
            
            if post.get('timestamp_text'):
                print(f"   ⏰ Time: {post['timestamp_text']}")
            
            print()
    
    def save_results(self):
        """Save extracted posts to file"""
        if not self.extracted_posts:
            print("❌ No posts to save")
            return None
        
        timestamp = int(time.time())
        filename = f"adamanz_linkedin_posts_{timestamp}.json"
        filepath = f"data/{filename}"
        
        os.makedirs("data", exist_ok=True)
        
        results = {
            "extraction_info": {
                "profile_username": self.profile_username,
                "profile_url": self.profile_url,
                "activity_url": self.activity_url,
                "total_posts_extracted": len(self.extracted_posts),
                "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "extraction_method": "browserbase_context_authenticated"
            },
            "posts": self.extracted_posts
        }
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filepath}")
        return filepath

async def main():
    """Main extraction function"""
    print("🎯 LinkedIn Post Extraction for adamanz")
    print("Using authenticated Browserbase Context")
    print("=" * 60)
    print()
    
    extractor = LinkedInPostExtractor("adamanz")
    
    # Extract posts
    posts = await extractor.extract_posts(max_posts=10)
    
    if posts:
        print()
        # Analyze posts
        extractor.analyze_posts()
        
        # Save results
        print()
        filepath = extractor.save_results()
        
        print()
        print("🎉 SUCCESS: LinkedIn post extraction completed!")
        print(f"✅ Extracted {len(posts)} posts from linkedin.com/in/adamanz")
        print(f"📄 Results saved to: {filepath}")
        print("🔍 Check the analysis above for post insights")
        
        return True
    else:
        print("❌ No posts extracted")
        print()
        print("🔧 Possible reasons:")
        print("1. Profile may be private or require connection")
        print("2. LinkedIn may be blocking automated access")
        print("3. Different selectors needed for current LinkedIn layout")
        print("4. Try accessing your own profile or a public profile")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)