#!/usr/bin/env python3
"""
LinkedIn authentication with Playwright - fills credentials and waits for 2FA
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def authenticate_linkedin_with_2fa():
    """Authenticate to LinkedIn using existing session with 2FA support"""
    
    # Use the current context and create session
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    
    print(f"🚀 Starting LinkedIn authentication with context: {context_id}")
    print("=" * 60)
    
    # Create session
    session = bb.sessions.create(
        project_id=os.environ["BROWSERBASE_PROJECT_ID"],
        browser_settings={
            "context": {
                "id": context_id,
                "persist": True  # Save authentication
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
            print("📍 Navigating to LinkedIn login...")
            page.goto("https://www.linkedin.com/login")
            page.wait_for_selector("#username", timeout=15000)
            
            print("📝 Filling LinkedIn credentials...")
            # Fill username
            page.fill("#username", os.environ["LINKEDIN_USERNAME"])
            time.sleep(1)
            
            # Fill password  
            page.fill("#password", os.environ["LINKEDIN_PASSWORD"])
            time.sleep(1)
            
            print("🚀 Submitting login form...")
            page.click('button[type="submit"]')
            
            # Wait for response
            time.sleep(5)
            
            current_url = page.url
            print(f"📍 After login URL: {current_url}")
            
            # Check if 2FA/verification is required
            if "challenge" in current_url or "checkpoint" in current_url:
                print("\n📱 LinkedIn 2FA/Verification Required!")
                print("🔄 Please complete verification on your device...")
                print("   - Check your LinkedIn mobile app")
                print("   - Or check your email/SMS for verification code")
                print("   - Complete the verification process")
                print("⏳ Waiting for you to complete 2FA (up to 10 minutes)...")
                
                # Wait for verification with user feedback
                for attempt in range(60):  # 10 minutes (60 * 10 seconds)
                    time.sleep(10)
                    current_url = page.url
                    
                    if "challenge" not in current_url and "checkpoint" not in current_url:
                        print(f"\n✅ 2FA completed after {(attempt + 1) * 10} seconds!")
                        break
                        
                    if attempt % 6 == 0:  # Every minute
                        print(f"   ⏳ Still waiting for 2FA... ({attempt + 1}/60) - {(attempt + 1) * 10} seconds")
                        print(f"   📍 Current URL: {current_url}")
                else:
                    print("\n⚠️  2FA timeout - but continuing to test access...")
            
            # Test authentication by accessing LinkedIn feed
            print("\n🔍 Testing authentication by accessing LinkedIn feed...")
            page.goto("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            final_url = page.url
            final_title = page.title()
            
            print(f"📍 Feed URL: {final_url}")
            print(f"📰 Feed Title: {final_title}")
            
            # Check authentication success
            if ("feed" in final_url and "login" not in final_url and 
                "authwall" not in final_url and "sign" not in final_url.lower()):
                print("✅ Authentication successful!")
                
                # Test Adam's profile access
                print("🎯 Testing Adam's recent activity access...")
                page.goto("https://www.linkedin.com/in/adamanz/recent-activity/all/")
                time.sleep(3)
                
                profile_url = page.url
                profile_title = page.title()
                
                print(f"📍 Profile URL: {profile_url}")
                print(f"📰 Profile Title: {profile_title}")
                
                # Take screenshot
                screenshot_path = f"linkedin_authenticated_success_{int(time.time())}.png"
                page.screenshot(path=screenshot_path)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                success = True
            else:
                print("⚠️  Authentication may still need completion")
                success = False
            
            print(f"\n🎉 AUTHENTICATION COMPLETE!")
            print(f"📋 Context ID: {context_id}")
            print(f"🌐 Session: {session.id}")
            print(f"💾 Authentication state saved to context")
            
            if success:
                print("✅ Ready for automated LinkedIn access!")
                print(f"✅ Can access: https://www.linkedin.com/in/adamanz/recent-activity/all/")
                print(f"\n📝 Add to .env file:")
                print(f"LINKEDIN_CONTEXT_ID={context_id}")
            else:
                print("⚠️  May need additional verification steps")
            
            return success
            
        except Exception as e:
            print(f"❌ Error during authentication: {e}")
            return False
        finally:
            # Keep browser open for a moment to ensure context saves
            print("💾 Ensuring context persistence...")
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    success = authenticate_linkedin_with_2fa()
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'NEEDS COMPLETION ⚠️'}")