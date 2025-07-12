#!/usr/bin/env python3
"""
Smart LinkedIn notifications - automatically click most recent post using GPT-4o
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
import openai

load_dotenv()

# Configure OpenAI to use GPT-4o
openai.api_key = os.environ["OPENAI_API_KEY"]

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def get_click_strategy_from_gpt4o(page_content):
    """Use GPT-4o to determine the best strategy to click the most recent post"""
    
    prompt = f"""
    You are a LinkedIn automation expert. I need to click on the MOST RECENT post in a LinkedIn notifications page.
    
    Here's the current page HTML structure:
    {page_content[:3000]}  # Truncate for token limits
    
    Please analyze this and provide a CSS selector or strategy to click on the FIRST/MOST RECENT post notification.
    
    Look for:
    1. Links to posts (like href="/feed/update/...")
    2. Clickable notification items
    3. The topmost/first post in the list
    
    Return ONLY a valid CSS selector that will click on the most recent post, like:
    - 'a[href*="/feed/update/"]:first-of-type'
    - '.notification-item:first-child a'
    - '[data-urn*="activity"]:first-child'
    
    Be specific and target the FIRST/MOST RECENT item.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-2024-11-20",  # Use GPT-4o
            messages=[
                {"role": "system", "content": "You are a web automation expert. Return only CSS selectors."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        selector = response.choices[0].message.content.strip()
        print(f"🧠 GPT-4o suggested selector: {selector}")
        return selector
        
    except Exception as e:
        print(f"⚠️ GPT-4o error: {e}")
        # Fallback selectors
        return 'a[href*="/feed/update/"]:first-of-type'

def smart_click_recent_post():
    """Smart LinkedIn recent post clicking with GPT-4o intelligence"""
    
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    
    print(f"🚀 Smart LinkedIn Recent Post Clicker (GPT-4o Powered)")
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
    
    print(f"✅ Session: {session.id}")
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(session.connectUrl)
        context = browser.contexts[0]
        page = context.pages[0]
        
        try:
            # Navigate to notifications with posts filter
            print("📍 Navigating to LinkedIn notifications (my posts)...")
            notifications_url = "https://www.linkedin.com/notifications/?filter=my_posts_all"
            
            # Use networkidle for better loading
            page.goto(notifications_url, wait_until="networkidle", timeout=60000)
            time.sleep(3)
            
            print(f"✅ Loaded: {page.url}")
            
            # Take screenshot of notifications page
            notifications_screenshot = f"notifications_before_click_{int(time.time())}.png"
            page.screenshot(path=notifications_screenshot)
            print(f"📸 Before click: {notifications_screenshot}")
            
            # Get page content for GPT-4o analysis
            print("🧠 Analyzing page with GPT-4o...")
            page_html = page.content()
            
            # Get smart selector from GPT-4o
            smart_selector = get_click_strategy_from_gpt4o(page_html)
            
            # Try the GPT-4o suggested selector first
            print(f"🎯 Trying GPT-4o selector: {smart_selector}")
            
            try:
                element = page.query_selector(smart_selector)
                if element:
                    print("✅ Found element with GPT-4o selector!")
                    element.click()
                    time.sleep(5)
                    
                    print(f"📍 After click URL: {page.url}")
                    
                    # Screenshot after clicking
                    post_screenshot = f"post_after_click_{int(time.time())}.png"
                    page.screenshot(path=post_screenshot)
                    print(f"📸 After click: {post_screenshot}")
                    
                    # Look for reactions
                    print("🔍 Looking for reactions on the post...")
                    
                    # Scroll to see reactions
                    page.evaluate("window.scrollTo(0, 400)")
                    time.sleep(2)
                    
                    # First try to click on the "Reactions" text or the reaction images area
                    print("🎯 Looking for reaction details to expand...")
                    
                    # Enhanced selectors to find the reactions area
                    reaction_detail_selectors = [
                        # Try clicking on "Reactions" text
                        'text="Reactions"',
                        # Try clicking on the reaction avatars area
                        '.feed-shared-social-action-bar__reactions',
                        '.social-actions-bar .reactions-list',
                        '.feed-shared-social-counts-bar',
                        # Try the reaction button itself
                        'button[aria-label*="reactions"]',
                        'button[aria-label*="likes"]',
                        'button[aria-label*="See who"]',
                        # Try clicking on reaction images
                        '.feed-shared-social-action-bar img:first-of-type',
                        '[data-urn*="reaction"]',
                        # Generic social actions
                        '.social-actions-bar button:first-child',
                        '.feed-shared-social-action-bar button:first-child'
                    ]
                    
                    reactions_expanded = False
                    for reaction_selector in reaction_detail_selectors:
                        try:
                            print(f"🎯 Trying reaction selector: {reaction_selector}")
                            
                            if reaction_selector.startswith('text='):
                                # Handle text selector differently
                                elements = page.get_by_text("Reactions").all()
                            else:
                                elements = page.query_selector_all(reaction_selector)
                            
                            if elements:
                                print(f"✅ Found {len(elements)} elements with: {reaction_selector}")
                                try:
                                    if reaction_selector.startswith('text='):
                                        elements[0].click()
                                    else:
                                        elements[0].click()
                                    
                                    time.sleep(3)
                                    print(f"✅ Successfully clicked reaction area!")
                                    reactions_expanded = True
                                    
                                    # Screenshot reaction details modal/popup
                                    reactions_screenshot = f"reactions_details_{int(time.time())}.png"
                                    page.screenshot(path=reactions_screenshot)
                                    print(f"📸 Reaction details: {reactions_screenshot}")
                                    
                                    # Check if a modal opened and take another screenshot after a moment
                                    time.sleep(2)
                                    modal_screenshot = f"reactions_modal_{int(time.time())}.png"
                                    page.screenshot(path=modal_screenshot)
                                    print(f"📸 Modal view: {modal_screenshot}")
                                    
                                    break
                                    
                                except Exception as e:
                                    print(f"   ❌ Click failed: {e}")
                                    continue
                            else:
                                print(f"   ❌ No elements found")
                        except Exception as e:
                            print(f"   ❌ Selector error: {e}")
                            continue
                    
                    if not reactions_expanded:
                        print("⚠️ Could not expand reactions, but captured post view")
                        # Take a screenshot anyway
                        reactions_screenshot = f"post_reactions_view_{int(time.time())}.png"
                        page.screenshot(path=reactions_screenshot)
                        print(f"📸 Post reactions view: {reactions_screenshot}")
                    
                    print("\n🎉 SUCCESS! Screenshots captured:")
                    print(f"   📸 {notifications_screenshot}")
                    print(f"   📸 {post_screenshot}")
                    if 'reactions_screenshot' in locals():
                        print(f"   📸 {reactions_screenshot}")
                    
                    return True
                else:
                    print("❌ GPT-4o selector didn't find element")
                    
            except Exception as e:
                print(f"❌ GPT-4o selector failed: {e}")
            
            # Fallback: Try common selectors
            print("🔄 Trying fallback selectors...")
            
            fallback_selectors = [
                'a[href*="/feed/update/"]:first-of-type',
                '[data-urn*="activity"]:first-child a',
                '.notification-item:first-child a',
                '.artdeco-list__item:first-child a',
                'li[data-urn]:first-child a'
            ]
            
            for selector in fallback_selectors:
                print(f"🎯 Trying fallback: {selector}")
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with: {selector}")
                    try:
                        elements[0].click()
                        time.sleep(5)
                        
                        print(f"📍 Clicked! New URL: {page.url}")
                        
                        # Screenshot
                        fallback_screenshot = f"fallback_click_{int(time.time())}.png"
                        page.screenshot(path=fallback_screenshot)
                        print(f"📸 Fallback result: {fallback_screenshot}")
                        
                        return True
                    except Exception as e:
                        print(f"❌ Fallback failed: {e}")
                        continue
            
            print("❌ All selectors failed")
            return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    success = smart_click_recent_post()
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'FAILED ❌'}")