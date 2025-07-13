#!/usr/bin/env python3
"""
Test class to fetch last 10 LinkedIn posts for linkedin.com/in/adamanz
Uses our ReactionReach tools to validate the setup
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append("src")

from tools.linkedin_url_builder import linkedin_url_builder
from tools.browserbase_linkedin import browserbase_linkedin

class LinkedInPostFetcher:
    """Test class to fetch LinkedIn posts using ReactionReach tools"""
    
    def __init__(self, profile_url: str = "https://linkedin.com/in/adamanz"):
        """
        Initialize the LinkedIn post fetcher
        
        :param profile_url: LinkedIn profile URL to test with
        """
        load_dotenv()
        self.profile_url = profile_url
        self.results = []
        
        # Validate environment
        self._validate_environment()
        
    def _validate_environment(self):
        """Validate required environment variables are set"""
        required_vars = [
            "BROWSERBASE_API_KEY",
            "BROWSERBASE_PROJECT_ID", 
            "OPENAI_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print("✅ Environment variables validated")
    
    def test_url_builder(self):
        """Test the LinkedIn URL builder tool"""
        print("\n🔧 Testing LinkedIn URL Builder...")
        
        try:
            # Test building activity feed URL
            activity_url = linkedin_url_builder(
                profile_url=self.profile_url,
                action="posts"
            )
            
            print(f"   ✅ Profile URL: {self.profile_url}")
            print(f"   ✅ Activity URL: {activity_url}")
            
            return activity_url
            
        except Exception as e:
            print(f"   ❌ URL Builder failed: {e}")
            raise
    
    def test_browserbase_connection(self):
        """Test basic Browserbase connection"""
        print("\n🌐 Testing Browserbase Connection...")
        
        try:
            # Test with a simple LinkedIn page first
            test_url = "https://www.linkedin.com"
            
            result = browserbase_linkedin(
                url=test_url,
                action="extract_content",
                wait_time=5
            )
            
            if "linkedin" in result.lower():
                print("   ✅ Browserbase connection successful")
                print(f"   ✅ Content length: {len(result)} characters")
                return True
            else:
                print("   ⚠️  Unexpected content returned")
                return False
                
        except Exception as e:
            print(f"   ❌ Browserbase connection failed: {e}")
            raise
    
    def fetch_posts(self, max_posts: int = 10):
        """
        Fetch the last N posts from the LinkedIn profile
        
        :param max_posts: Maximum number of posts to fetch
        :return: List of posts or error information
        """
        print(f"\n📊 Fetching last {max_posts} posts from {self.profile_url}...")
        
        try:
            # Step 1: Build the activity feed URL
            activity_url = linkedin_url_builder(
                profile_url=self.profile_url,
                action="posts"
            )
            
            print(f"   🔗 Navigating to: {activity_url}")
            
            # Step 2: Use Browserbase to scroll and extract posts
            result = browserbase_linkedin(
                url=activity_url,
                action="scroll_and_extract",
                wait_time=8,
                scroll_count=3  # Scroll 3 times to get more posts
            )
            
            print(f"   ✅ Content extracted: {len(result)} characters")
            
            # Step 3: Try to extract structured post data
            posts_result = browserbase_linkedin(
                url=activity_url,
                action="extract_posts",
                wait_time=5
            )
            
            # Try to parse JSON result
            try:
                posts_data = json.loads(posts_result)
                print(f"   📝 Found {posts_data.get('total_posts_found', 'unknown')} posts")
                
                self.results = {
                    "profile_url": self.profile_url,
                    "activity_url": activity_url,
                    "posts_data": posts_data,
                    "raw_content_length": len(result),
                    "status": "success"
                }
                
                return posts_data
                
            except json.JSONDecodeError:
                print("   ⚠️  Could not parse posts as JSON, returning raw content")
                
                self.results = {
                    "profile_url": self.profile_url,
                    "activity_url": activity_url,
                    "raw_content": result[:1000] + "..." if len(result) > 1000 else result,
                    "raw_content_length": len(result),
                    "status": "partial_success"
                }
                
                return result
                
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
        print("\n📋 Analysis Results:")
        print("=" * 50)
        
        if not self.results:
            print("❌ No results to analyze")
            return
        
        print(f"🎯 Profile: {self.results['profile_url']}")
        print(f"📊 Status: {self.results['status']}")
        
        if self.results['status'] == 'success':
            posts_data = self.results['posts_data']
            print(f"📝 Total posts found: {posts_data.get('total_posts_found', 0)}")
            
            extracted_posts = posts_data.get('extracted_posts', [])
            print(f"📑 Extracted posts: {len(extracted_posts)}")
            
            for i, post in enumerate(extracted_posts[:5]):  # Show first 5
                print(f"\n   Post {i+1}:")
                print(f"   - Preview: {post.get('text_preview', 'N/A')[:100]}...")
                print(f"   - Has reactions: {post.get('has_reactions', False)}")
                print(f"   - Has comments: {post.get('has_comments', False)}")
        
        elif self.results['status'] == 'partial_success':
            print(f"📄 Raw content length: {self.results['raw_content_length']} characters")
            print(f"📝 Content preview: {self.results['raw_content'][:200]}...")
        
        else:
            print(f"❌ Error: {self.results.get('error', 'Unknown error')}")
    
    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if not filename:
            filename = f"test_results_adamanz_{int(os.time.time())}.json"
        
        results_path = Path("data") / filename
        results_path.parent.mkdir(exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_path}")
        return results_path

def main():
    """Main test execution"""
    print("🚀 LinkedIn Post Fetcher Test")
    print("=" * 40)
    print("Testing ReactionReach tools with linkedin.com/in/adamanz")
    
    try:
        # Initialize the fetcher
        fetcher = LinkedInPostFetcher("https://linkedin.com/in/adamanz")
        
        # Run tests
        fetcher.test_url_builder()
        fetcher.test_browserbase_connection()
        
        # Fetch posts
        posts = fetcher.fetch_posts(max_posts=10)
        
        # Analyze results
        fetcher.analyze_results()
        
        # Save results
        fetcher.save_results()
        
        print("\n✅ Test completed successfully!")
        print("\nNext steps:")
        print("1. Review the saved results file")
        print("2. Check if posts were extracted properly")
        print("3. If successful, proceed with full ReactionReach analysis")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has valid API keys")
        print("2. Ensure linkedin.com/in/adamanz is accessible")
        print("3. Verify Browserbase project is active")
        print("4. Try running: python test_setup.py first")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)