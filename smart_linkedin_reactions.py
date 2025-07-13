#!/usr/bin/env python3
"""
Smart LinkedIn reactions capture - handles both authenticated and non-authenticated states
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def smart_linkedin_reactions():
    """Smart LinkedIn reactions capture with authentication detection"""
    
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    
    print(f"🚀 Smart LinkedIn reactions capture")
    print("=" * 50)
    
    # Create session
    session = bb.sessions.create(
        project_id=os.environ["BROWSERBASE_PROJECT_ID"],
        browser_settings={
            "context": {
                "id": context_id,
                "persist": True
            }
        },
        proxies=[{
            "type": "browserbase",
            "geolocation": {
                "city": "New York",
                "state": "NY", 
                "country": "US"
            }
        }]
    )
    
    print(f"✅ Session: {session.id}")
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(session.connectUrl)
        context = browser.contexts[0]
        page = context.pages[0]
        
        try:
            # Step 1: Check authentication status
            print("🔍 Checking authentication status...")
            page.goto("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            # Check if we need to login
            if "login" in current_url or "authwall" in current_url:
                print("🔐 Not authenticated - logging in...")
                
                page.goto("https://www.linkedin.com/login")
                time.sleep(2)
                
                # Check if login form is present
                username_field = page.query_selector("#username")
                if username_field:
                    print("📝 Filling credentials...")
                    page.fill("#username", os.environ["LINKEDIN_USERNAME"])
                    page.fill("#password", os.environ["LINKEDIN_PASSWORD"])
                    page.click('button[type="submit"]')
                    time.sleep(5)
                    
                    # Handle 2FA if needed
                    if "challenge" in page.url or "checkpoint" in page.url:
                        print("📱 2FA required - please complete and press Enter when done...")
                        input("Press Enter after completing 2FA...")
                else:
                    print("❌ Could not find login form")
                    return False
            else:
                print("✅ Already authenticated!")
            
            # Step 2: Navigate to notifications
            print("\n📍 Navigating to notifications...")
            notifications_url = "https://www.linkedin.com/notifications/?filter=my_posts_all"
            page.goto(notifications_url)
            time.sleep(5)
            
            print(f"📍 Notifications page loaded: {page.url}")
            
            # Take initial screenshot
            notifications_screenshot = f"notifications_{int(time.time())}.png"
            page.screenshot(path=notifications_screenshot)
            print(f"📸 Notifications screenshot: {notifications_screenshot}")
            
            # Step 3: Look for recent activity
            print("\n🔍 Looking for recent post activity...")
            
            # Wait for content to load
            time.sleep(3)
            
            # Try multiple approaches to find clickable notifications
            clickable_elements = []
            
            # Approach 1: Look for links in notifications
            links = page.query_selector_all('a[href*="/feed/update/"]')
            if links:
                clickable_elements.extend(links[:3])  # Top 3
                print(f"✅ Found {len(links)} post links")
            
            # Approach 2: Look for notification items
            notification_items = page.query_selector_all('[data-urn*="activity"]')
            if notification_items:
                clickable_elements.extend(notification_items[:3])
                print(f"✅ Found {len(notification_items)} activity items")
            
            # Approach 3: Look for list items that might be clickable
            list_items = page.query_selector_all('li[data-urn], .artdeco-list__item')
            if list_items:
                clickable_elements.extend(list_items[:3])
                print(f"✅ Found {len(list_items)} list items")
            
            if clickable_elements:
                print(f"🎯 Attempting to click most recent notification...")
                
                # Try clicking the first element
                try:
                    clickable_elements[0].click()
                    time.sleep(5)
                    
                    print(f"📍 After click URL: {page.url}")
                    
                    # Step 4: Capture reactions
                    print("\n📸 Capturing post and reactions...")
                    
                    # Scroll to see full post
                    page.evaluate("window.scrollTo(0, 300)")
                    time.sleep(2)
                    
                    # Screenshot the post
                    post_screenshot = f"post_with_reactions_{int(time.time())}.png"
                    page.screenshot(path=post_screenshot)
                    print(f"📸 Post screenshot: {post_screenshot}")
                    
                    # Look for and click reactions to see details
                    print("🔍 Looking for reaction details...")
                    
                    # Try to find and click reaction count/details
                    reaction_selectors = [
                        'button[aria-label*="reaction"]',
                        '.social-actions-bar button',
                        '[data-urn*="reaction"]',
                        'button[aria-label*="See who"]'
                    ]
                    
                    for selector in reaction_selectors:
                        buttons = page.query_selector_all(selector)
                        if buttons:
                            print(f"🎯 Trying reaction selector: {selector}")
                            try:
                                buttons[0].click()
                                time.sleep(3)
                                
                                # Screenshot reaction details
                                reactions_detail_screenshot = f"reaction_details_{int(time.time())}.png"
                                page.screenshot(path=reactions_detail_screenshot)
                                print(f"📸 Reaction details: {reactions_detail_screenshot}")
                                break
                            except:
                                continue
                    
                    print("\n🎉 COMPLETED! Screenshots saved:")
                    print(f"   📸 {notifications_screenshot}")
                    print(f"   📸 {post_screenshot}")
                    if 'reactions_detail_screenshot' in locals():
                        print(f"   📸 {reactions_detail_screenshot}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error clicking notification: {e}")
                    return False
            else:
                print("❌ No clickable notifications found")
                
                # Take screenshot of what we see
                no_notifications_screenshot = f"no_notifications_{int(time.time())}.png"
                page.screenshot(path=no_notifications_screenshot)
                print(f"📸 Current page: {no_notifications_screenshot}")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    success = smart_linkedin_reactions()
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'FAILED ❌'}")