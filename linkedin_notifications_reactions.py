#!/usr/bin/env python3
"""
LinkedIn login, navigate to notifications, click most recent post, screenshot reactions
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def linkedin_notifications_reactions():
    """Login to LinkedIn and capture reactions on most recent post from notifications"""
    
    # Use the context
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    
    print(f"🚀 Starting LinkedIn notifications reactions capture")
    print("=" * 60)
    
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
    
    print(f"✅ Session created: {session.id}")
    print(f"🌐 Session URL: https://browserbase.com/sessions/{session.id}")
    
    # Connect with Playwright
    with sync_playwright() as playwright:
        print("🔗 Connecting to Browserbase session...")
        browser = playwright.chromium.connect_over_cdp(session.connectUrl)
        context = browser.contexts[0]
        page = context.pages[0]
        
        try:
            # Step 1: Login to LinkedIn
            print("📍 Step 1: Navigating to LinkedIn login...")
            page.goto("https://www.linkedin.com/login")
            page.wait_for_selector("#username", timeout=15000)
            
            print("📝 Filling LinkedIn credentials...")
            page.fill("#username", os.environ["LINKEDIN_USERNAME"])
            time.sleep(1)
            page.fill("#password", os.environ["LINKEDIN_PASSWORD"])
            time.sleep(1)
            
            print("🚀 Submitting login form...")
            page.click('button[type="submit"]')
            time.sleep(5)
            
            current_url = page.url
            print(f"📍 After login URL: {current_url}")
            
            # Handle 2FA if needed
            if "challenge" in current_url or "checkpoint" in current_url:
                print("\n📱 2FA required - please complete on your device...")
                print("⏳ Waiting up to 3 minutes for completion...")
                
                for attempt in range(18):  # 3 minutes
                    time.sleep(10)
                    current_url = page.url
                    if "challenge" not in current_url and "checkpoint" not in current_url:
                        print(f"✅ 2FA completed!")
                        break
                    if attempt % 3 == 0:
                        print(f"   ⏳ Still waiting... ({attempt + 1}/18)")
                else:
                    print("⚠️  2FA timeout - continuing anyway...")
            
            # Step 2: Navigate to notifications
            print("\n📍 Step 2: Navigating to notifications...")
            notifications_url = "https://www.linkedin.com/notifications/?filter=my_posts_all"
            page.goto(notifications_url)
            time.sleep(5)
            
            print(f"📍 Notifications URL: {page.url}")
            
            # Take screenshot of notifications page
            notifications_screenshot = f"linkedin_notifications_{int(time.time())}.png"
            page.screenshot(path=notifications_screenshot)
            print(f"📸 Notifications screenshot: {notifications_screenshot}")
            
            # Step 3: Find and click most recent post
            print("\n📍 Step 3: Looking for most recent post notification...")
            
            # Wait for notifications to load
            time.sleep(3)
            
            # Look for notification items (various selectors LinkedIn might use)
            notification_selectors = [
                '[data-urn*="activity"]',
                '.notification-item',
                '[data-notification-id]',
                '.artdeco-list__item',
                '.notification-card',
                'li[data-urn]'
            ]
            
            most_recent_notification = None
            for selector in notification_selectors:
                notifications = page.query_selector_all(selector)
                if notifications:
                    most_recent_notification = notifications[0]  # First one is most recent
                    print(f"✅ Found notifications using selector: {selector}")
                    print(f"   📊 Found {len(notifications)} notifications")
                    break
            
            if most_recent_notification:
                print("🎯 Clicking on most recent post notification...")
                most_recent_notification.click()
                time.sleep(5)
                
                print(f"📍 After clicking URL: {page.url}")
                
                # Step 4: Look for reactions and screenshot
                print("\n📍 Step 4: Looking for reactions on the post...")
                
                # Scroll to see reactions if needed
                page.evaluate("window.scrollTo(0, 500)")
                time.sleep(2)
                
                # Look for reactions section
                reactions_selectors = [
                    '[data-urn*="reaction"]',
                    '.reactions-list',
                    '.social-actions-bar',
                    '.feed-shared-social-action-bar',
                    '.reaction-list-item',
                    '[aria-label*="reaction"]',
                    '.social-actions'
                ]
                
                reactions_found = False
                for selector in reactions_selectors:
                    reactions = page.query_selector_all(selector)
                    if reactions:
                        print(f"✅ Found reactions using selector: {selector}")
                        print(f"   👍 Found {len(reactions)} reaction elements")
                        reactions_found = True
                        break
                
                # Take screenshot of the post with reactions
                post_reactions_screenshot = f"linkedin_post_reactions_{int(time.time())}.png"
                page.screenshot(path=post_reactions_screenshot)
                print(f"📸 Post reactions screenshot: {post_reactions_screenshot}")
                
                # Try to click on reactions to see who reacted
                print("\n📍 Step 5: Attempting to view reaction details...")
                
                # Look for reactions count or "See who reacted" links
                reaction_detail_selectors = [
                    '[aria-label*="See who"]',
                    '.social-actions-bar button',
                    '[data-urn*="reaction"] button',
                    '.feed-shared-social-action-bar button'
                ]
                
                for selector in reaction_detail_selectors:
                    reaction_buttons = page.query_selector_all(selector)
                    if reaction_buttons:
                        print(f"🎯 Trying to click reaction details with: {selector}")
                        try:
                            reaction_buttons[0].click()
                            time.sleep(3)
                            
                            # Screenshot reaction details
                            reaction_details_screenshot = f"linkedin_reaction_details_{int(time.time())}.png"
                            page.screenshot(path=reaction_details_screenshot)
                            print(f"📸 Reaction details screenshot: {reaction_details_screenshot}")
                            break
                        except Exception as e:
                            print(f"   ⚠️  Could not click reaction details: {e}")
                            continue
                
                print("\n🎉 COMPLETED! Screenshots captured:")
                print(f"   📸 Notifications page: {notifications_screenshot}")
                print(f"   📸 Post with reactions: {post_reactions_screenshot}")
                if 'reaction_details_screenshot' in locals():
                    print(f"   📸 Reaction details: {reaction_details_screenshot}")
                
                return True
                
            else:
                print("❌ Could not find any notifications")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            print("💾 Keeping browser open briefly to save context...")
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    success = linkedin_notifications_reactions()
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'FAILED ❌'}")