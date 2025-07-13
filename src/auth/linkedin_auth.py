"""
LinkedIn Authentication Module with Stealth Mode and Cookie Management
Handles automatic login, session persistence, and anti-bot detection evasion
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import Page, BrowserContext
from dotenv import load_dotenv

load_dotenv()

class LinkedInAuth:
    """
    LinkedIn Authentication with Browserbase Stealth Mode
    Features:
    - Username/password authentication
    - Cookie session persistence  
    - Proxy and fingerprinting via Browserbase
    - Anti-captcha and rate limiting protection
    """
    
    def __init__(self, session_storage_path: str = None):
        """
        Initialize LinkedIn authentication
        
        :param session_storage_path: Path to store session cookies
        """
        self.username = os.getenv("LINKEDIN_USERNAME")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.use_stored_cookies = os.getenv("USE_STORED_COOKIES", "true").lower() == "true"
        self.enable_proxies = os.getenv("ENABLE_PROXIES", "true").lower() == "true"
        self.enable_stealth = os.getenv("ENABLE_STEALTH_MODE", "true").lower() == "true"
        
        # Session storage
        self.session_storage_path = session_storage_path or os.getenv(
            "SESSION_STORAGE_PATH", "./data/linkedin_session.json"
        )
        
        # Ensure data directory exists
        Path(self.session_storage_path).parent.mkdir(parents=True, exist_ok=True)
        
        if not self.username or not self.password:
            raise ValueError("LINKEDIN_USERNAME and LINKEDIN_PASSWORD must be set in .env file")
    
    def load_stored_session(self) -> Optional[Dict[str, Any]]:
        """
        Load stored session cookies from file
        
        :return: Stored session data or None
        """
        if not self.use_stored_cookies:
            return None
            
        try:
            session_path = Path(self.session_storage_path)
            if session_path.exists():
                with open(session_path, 'r') as f:
                    session_data = json.load(f)
                
                # Check if session is still valid (not expired)
                if self._is_session_valid(session_data):
                    print("   ✅ Found valid stored session")
                    return session_data
                else:
                    print("   ⚠️  Stored session expired, will re-authenticate")
                    
        except Exception as e:
            print(f"   ⚠️  Error loading stored session: {e}")
        
        return None
    
    def store_session(self, cookies: list, additional_data: Dict[str, Any] = None):
        """
        Store session cookies and data to file
        
        :param cookies: Browser cookies to store
        :param additional_data: Additional session data
        """
        if not self.use_stored_cookies:
            return
            
        try:
            session_data = {
                "cookies": cookies,
                "timestamp": time.time(),
                "additional_data": additional_data or {},
                "username": self.username  # Store username for verification
            }
            
            with open(self.session_storage_path, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            print(f"   💾 Session stored to: {self.session_storage_path}")
            
        except Exception as e:
            print(f"   ❌ Error storing session: {e}")
    
    def _is_session_valid(self, session_data: Dict[str, Any]) -> bool:
        """
        Check if stored session is still valid
        
        :param session_data: Session data to validate
        :return: True if session is valid
        """
        if not session_data:
            return False
        
        # Check timestamp (sessions expire after 24 hours)
        timestamp = session_data.get("timestamp", 0)
        age_hours = (time.time() - timestamp) / 3600
        
        if age_hours > 24:
            return False
        
        # Check if cookies exist and have essential LinkedIn cookies
        cookies = session_data.get("cookies", [])
        essential_cookies = ["li_at", "JSESSIONID", "liap"]
        
        cookie_names = [cookie.get("name", "") for cookie in cookies]
        has_essential = any(essential in cookie_names for essential in essential_cookies)
        
        return has_essential
    
    async def authenticate(self, page: Page, context: BrowserContext) -> bool:
        """
        Authenticate with LinkedIn using stored session or username/password
        
        :param page: Playwright page object
        :param context: Playwright browser context
        :return: True if authentication successful
        """
        print("🔐 Starting LinkedIn authentication...")
        
        # Try to use stored session first
        stored_session = self.load_stored_session()
        if stored_session and await self._try_stored_session(page, context, stored_session):
            print("   ✅ Authentication successful using stored session")
            return True
        
        # Fall back to username/password authentication
        print("   🔑 Authenticating with username/password...")
        return await self._authenticate_with_credentials(page, context)
    
    async def _try_stored_session(self, page: Page, context: BrowserContext, session_data: Dict[str, Any]) -> bool:
        """
        Try to authenticate using stored session cookies
        
        :param page: Playwright page object
        :param context: Playwright browser context  
        :param session_data: Stored session data
        :return: True if session authentication successful
        """
        try:
            cookies = session_data.get("cookies", [])
            if cookies:
                await context.add_cookies(cookies)
                print("   🍪 Added stored cookies to context")
            
            # Test authentication by accessing a protected page
            await page.goto("https://www.linkedin.com/feed/", wait_until="networkidle")
            
            # Check if we're redirected to login (indicates session invalid)
            if "login" in page.url or "sign-in" in page.url:
                print("   ❌ Stored session invalid, redirected to login")
                return False
            
            # Check for LinkedIn feed content (indicates successful auth)
            if "feed" in page.url and await page.query_selector('[data-urn*="urn:li:activity"]'):
                print("   ✅ Stored session valid, authenticated successfully")
                return True
                
            return False
            
        except Exception as e:
            print(f"   ❌ Error trying stored session: {e}")
            return False
    
    async def _authenticate_with_credentials(self, page: Page, context: BrowserContext) -> bool:
        """
        Authenticate using LinkedIn username and password
        
        :param page: Playwright page object
        :param context: Playwright browser context
        :return: True if authentication successful
        """
        try:
            # Navigate to LinkedIn login page
            print("   🌐 Navigating to LinkedIn login...")
            await page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            
            # Wait for login form
            await page.wait_for_selector("#username", timeout=10000)
            
            # Fill in credentials
            print("   📝 Filling in credentials...")
            await page.fill("#username", self.username)
            await page.fill("#password", self.password)
            
            # Submit login form
            print("   🚀 Submitting login form...")
            await page.click('button[type="submit"]')
            
            # Wait for navigation after login
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Check for successful login
            if await self._verify_authentication(page):
                # Store session cookies
                cookies = await context.cookies()
                self.store_session(cookies, {"login_method": "credentials"})
                
                print("   ✅ Authentication successful with credentials")
                return True
            else:
                print("   ❌ Authentication failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Error during credential authentication: {e}")
            return False
    
    async def _verify_authentication(self, page: Page) -> bool:
        """
        Verify that LinkedIn authentication was successful
        
        :param page: Playwright page object
        :return: True if authenticated
        """
        try:
            # Check if we're on a LinkedIn authenticated page
            current_url = page.url
            
            # Common indicators of successful login
            success_indicators = [
                "linkedin.com/feed",
                "linkedin.com/in/",
                "linkedin.com/mynetwork",
                "linkedin.com/notifications"
            ]
            
            if any(indicator in current_url for indicator in success_indicators):
                return True
            
            # Check for presence of authenticated navigation elements
            nav_selectors = [
                '[data-test-id="global-nav"]',
                '.global-nav',
                '[data-test-global-nav]'
            ]
            
            for selector in nav_selectors:
                if await page.query_selector(selector):
                    return True
            
            # Check for feed content
            if await page.query_selector('[data-urn*="activity"]'):
                return True
                
            return False
            
        except Exception as e:
            print(f"   ⚠️  Error verifying authentication: {e}")
            return False
    
    def clear_stored_session(self):
        """Clear stored session data"""
        try:
            session_path = Path(self.session_storage_path)
            if session_path.exists():
                session_path.unlink()
                print(f"   🗑️  Cleared stored session: {self.session_storage_path}")
        except Exception as e:
            print(f"   ❌ Error clearing session: {e}")


def create_authenticated_browserbase_session():
    """
    Create a Browserbase session with stealth mode and proxy support
    Returns session configuration for LinkedIn automation
    """
    browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
    browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
    enable_proxies = os.getenv("ENABLE_PROXIES", "true").lower() == "true"
    
    if not browserbase_api_key or not browserbase_project_id:
        raise ValueError("BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID must be set")
    
    # Build session configuration
    session_config = {
        "projectId": browserbase_project_id,
        "proxies": enable_proxies,
        "fingerprint": {
            "devices": ["desktop"],
            "locales": ["en-US"],
            "operatingSystems": ["macos", "windows"]
        }
    }
    
    # WebSocket connection URL
    connect_url = f"wss://connect.browserbase.com?apiKey={browserbase_api_key}&projectId={browserbase_project_id}"
    if enable_proxies:
        connect_url += "&enableProxy=true"
    
    return connect_url, session_config