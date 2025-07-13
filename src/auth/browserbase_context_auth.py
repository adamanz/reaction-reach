"""
Browserbase Context Authentication for LinkedIn
Uses Browserbase Contexts for persistent, encrypted authentication storage
"""

import os
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page, BrowserContext
import requests
import json
import time

load_dotenv()

class BrowserbaseContextAuth:
    """
    LinkedIn authentication using Browserbase Contexts
    
    Features:
    - Persistent authentication across sessions
    - Encrypted browser state storage
    - Reduced bot detection with consistent fingerprints
    - Automatic session management
    """
    
    def __init__(self):
        """Initialize Browserbase Context authentication"""
        self.api_key = os.getenv("BROWSERBASE_API_KEY")
        self.project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        self.linkedin_username = os.getenv("LINKEDIN_USERNAME")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        
        # Context configuration
        self.context_id = os.getenv("LINKEDIN_CONTEXT_ID")
        self.context_persist = os.getenv("LINKEDIN_CONTEXT_PERSIST", "true").lower() == "true"
        
        if not all([self.api_key, self.project_id, self.linkedin_username, self.linkedin_password]):
            raise ValueError("Missing required environment variables for Browserbase Context authentication")
    
    def create_linkedin_context(self) -> str:
        """Create a new Browserbase context for LinkedIn authentication"""
        print("🔧 Creating new LinkedIn context...")
        
        url = "https://api.browserbase.com/v1/contexts"
        headers = {
            "X-BB-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "projectId": self.project_id
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            context_data = response.json()
            context_id = context_data["id"]
            print(f"✅ Created LinkedIn context: {context_id}")
            
            # Save context ID to environment (you should update your .env file)
            print(f"💡 Add to your .env file: LINKEDIN_CONTEXT_ID={context_id}")
            
            return context_id
        else:
            raise Exception(f"Failed to create context: {response.status_code} - {response.text}")
    
    def create_authenticated_session(self) -> Dict[str, Any]:
        """Create a Browserbase session with LinkedIn context"""
        
        # Ensure we have a context ID
        if not self.context_id:
            self.context_id = self.create_linkedin_context()
        
        print(f"🌐 Creating session with context: {self.context_id}")
        
        url = "https://api.browserbase.com/v1/sessions"
        headers = {
            "X-BB-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "projectId": self.project_id,
            "browserSettings": {
                "context": {
                    "id": self.context_id,
                    "persist": self.context_persist
                }
            },
            "proxies": True  # Enable stealth mode
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            session_data = response.json()
            print(f"✅ Created session: {session_data['id']}")
            return session_data
        else:
            raise Exception(f"Failed to create session: {response.status_code} - {response.text}")
    
    async def authenticate_linkedin(self, page: Page, context: BrowserContext) -> bool:
        """
        Authenticate with LinkedIn using the context session
        
        The context may already contain authentication state from previous sessions
        """
        print("🔐 Starting LinkedIn authentication with context...")
        
        try:
            # First, try to access LinkedIn feed to see if we're already authenticated
            print("   📊 Testing existing authentication state...")
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            
            current_url = page.url
            page_title = await page.title()
            
            print(f"   📍 URL: {current_url}")
            print(f"   📰 Title: {page_title}")
            
            # Check if we're already authenticated
            if ("feed" in current_url and "login" not in current_url and 
                "authwall" not in current_url and "sign" not in current_url.lower()):
                print("   ✅ Already authenticated via context!")
                return True
            
            # If not authenticated, proceed with login
            print("   🔑 Authentication required - proceeding with login...")
            
            # Navigate to login page
            await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=30000)
            
            # Wait for login form
            await page.wait_for_selector("#username", timeout=15000)
            
            # Fill credentials
            print("   📝 Filling login credentials...")
            await page.fill("#username", self.linkedin_username)
            await asyncio.sleep(1)
            await page.fill("#password", self.linkedin_password)
            await asyncio.sleep(1)
            
            # Submit login
            print("   🚀 Submitting login form...")
            await page.click('button[type="submit"]')
            
            # Wait for login to process
            await asyncio.sleep(5)
            
            # Check for verification challenges
            current_url = page.url
            if "challenge" in current_url or "checkpoint" in current_url:
                print("   📱 LinkedIn verification required!")
                print("   ⏳ Please complete verification on your LinkedIn mobile app...")
                
                # Wait for verification
                for attempt in range(30):  # 5 minutes max
                    await asyncio.sleep(10)
                    current_url = page.url
                    
                    if "challenge" not in current_url and "checkpoint" not in current_url:
                        print(f"   ✅ Verification completed after {(attempt + 1) * 10} seconds!")
                        break
                    
                    if attempt % 3 == 0:  # Every 30 seconds
                        print(f"   ⏳ Still waiting for verification... ({attempt + 1}/30)")
                else:
                    print("   ❌ Verification timeout")
                    return False
            
            # Verify authentication success
            print("   🔍 Verifying authentication...")
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=30000)
            
            final_url = page.url
            final_title = await page.title()
            
            if ("feed" in final_url and "login" not in final_url and 
                "authwall" not in final_url):
                print("   🎉 Authentication successful!")
                print(f"   💾 Context will persist authentication for future sessions")
                return True
            else:
                print(f"   ❌ Authentication failed - Final URL: {final_url}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    async def get_authenticated_page(self) -> tuple[Page, BrowserContext, Any]:
        """
        Get an authenticated LinkedIn page using Browserbase Context
        
        Returns:
            tuple: (page, context, browser) - Ready for LinkedIn navigation
        """
        print("🚀 Getting authenticated LinkedIn session...")
        
        # Create session with context
        session_data = self.create_authenticated_session()
        connect_url = session_data["connectUrl"]
        
        # Connect to the session
        async with async_playwright() as playwright:
            browser = await playwright.chromium.connect_over_cdp(connect_url)
            
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page() if not context.pages else context.pages[0]
            
            # Set extended timeout for LinkedIn
            page.set_default_timeout(60000)
            
            # Authenticate
            authenticated = await self.authenticate_linkedin(page, context)
            
            if not authenticated:
                await browser.close()
                raise Exception("LinkedIn authentication failed")
            
            print("✅ Ready for LinkedIn navigation!")
            return page, context, browser
    
    def delete_context(self) -> bool:
        """Delete the LinkedIn context (cleanup)"""
        if not self.context_id:
            print("⚠️  No context ID to delete")
            return True
        
        print(f"🗑️  Deleting LinkedIn context: {self.context_id}")
        
        url = f"https://api.browserbase.com/v1/contexts/{self.context_id}"
        headers = {"X-BB-API-Key": self.api_key}
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 204:
            print("✅ Context deleted successfully")
            return True
        else:
            print(f"❌ Failed to delete context: {response.status_code}")
            return False

# Convenience function for quick authentication
async def get_authenticated_linkedin_session():
    """Quick function to get authenticated LinkedIn session"""
    auth = BrowserbaseContextAuth()
    return await auth.get_authenticated_page()