"""
LinkedIn Reactions Extraction Tool for CrewAI
Extracts reactions from the most recent LinkedIn post using Browserbase and GPT-4o
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from browserbase import Browserbase
from playwright.sync_api import sync_playwright
import os
import time
import json
from datetime import datetime
import openai


class LinkedInReactionsToolSchema(BaseModel):
    """Input schema for LinkedIn Reactions Tool"""
    context_id: Optional[str] = Field(
        default=None,
        description="Browserbase context ID for persistent authentication"
    )
    max_retries: Optional[int] = Field(
        default=3,
        description="Maximum number of retries for extraction"
    )


class LinkedInReactionsTool(BaseTool):
    name: str = "LinkedIn Reactions Extractor"
    description: str = "Extracts reactions from the most recent LinkedIn post using Browserbase"
    args_schema: type[BaseModel] = LinkedInReactionsToolSchema
    
    def __init__(self, browserbase_api_key: str, openai_api_key: str, project_id: str):
        super().__init__()
        self.bb = Browserbase(api_key=browserbase_api_key)
        self.project_id = project_id
        openai.api_key = openai_api_key
    
    def _run(self, context_id: Optional[str] = None, max_retries: int = 3) -> str:
        """Extract reactions from the most recent LinkedIn post"""
        
        # Use default context if not provided
        if not context_id:
            context_id = "929c2463-a010-4425-b900-4fde8a7ca327"  # Default LinkedIn context
        
        print(f"🚀 Starting LinkedIn reactions extraction...")
        
        # Create session with Browserbase
        session_config = {
            "projectId": self.project_id,
            "browserSettings": {
                "context": {
                    "id": context_id,
                    "persist": True
                }
            },
            "proxies": [{
                "type": "browserbase",
                "geolocation": {
                    "city": "New York",
                    "state": "NY",
                    "country": "US"
                }
            }]
        }
        
        session = self.bb.sessions.create(**session_config)
        print(f"✅ Session created: {session.id}")
        
        reactions_data = []
        
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(session.connectUrl)
            context = browser.contexts[0]
            page = context.pages[0]
            
            try:
                # Navigate to LinkedIn notifications
                print("📍 Navigating to LinkedIn notifications...")
                page.goto("https://www.linkedin.com/notifications/?filter=my_posts_all")
                time.sleep(5)
                
                # Get page content for GPT-4o analysis
                page_content = page.content()
                
                # Use GPT-4o to find the best selector
                selector = self._get_click_strategy_from_gpt4o(page_content[:3000])
                
                # Try to click on the most recent post
                print(f"🎯 Clicking on most recent post using: {selector}")
                try:
                    page.click(selector, timeout=5000)
                    time.sleep(5)
                except:
                    print("⚠️ Direct click failed, trying fallback...")
                    # Fallback: try first link
                    links = page.query_selector_all('a[href*="/feed/update/"]:first-of-type')
                    if links:
                        links[0].click()
                        time.sleep(5)
                
                # Look for reactions button and click it
                print("🔍 Looking for reactions to expand...")
                reaction_clicked = False
                
                # Try multiple selectors for reactions
                reaction_selectors = [
                    'button:has-text("and") >> text=/.*and.*others/',
                    'button[aria-label*="reaction"]',
                    '.social-details-social-counts__reactions-count',
                    '[data-urn*="socialDetail:urn:li:fs_socialDetail:"]'
                ]
                
                for selector in reaction_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            print(f"✅ Found reactions with: {selector}")
                            elements[0].click()
                            reaction_clicked = True
                            time.sleep(3)
                            break
                    except:
                        continue
                
                if reaction_clicked:
                    # Extract reactor profiles
                    print("📊 Extracting reactor profiles...")
                    reactions_data = self._extract_reactor_profiles(page)
                    
                    # Save data
                    timestamp = int(time.time())
                    output_file = f"reactions_data_{timestamp}.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(reactions_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ Extracted {len(reactions_data)} reactions")
                    print(f"💾 Data saved to: {output_file}")
                else:
                    print("❌ Could not find reactions to click")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                return json.dumps({"error": str(e), "reactions": []})
            finally:
                browser.close()
        
        return json.dumps({
            "success": True,
            "reactions_count": len(reactions_data),
            "reactions": reactions_data,
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_click_strategy_from_gpt4o(self, page_content: str) -> str:
        """Use GPT-4o to determine the best selector for clicking the most recent post"""
        
        prompt = f"""
        You are a LinkedIn automation expert. I need to click on the MOST RECENT post in a LinkedIn notifications page.
        
        Here's the current page HTML structure:
        {page_content}
        
        Please analyze this and provide a CSS selector or strategy to click on the FIRST/MOST RECENT post notification.
        
        Look for:
        1. Links to posts (like href="/feed/update/...")
        2. Clickable notification items
        3. The topmost/first post in the list
        
        Return ONLY a valid CSS selector that will click on the most recent post.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=[
                    {"role": "system", "content": "You are a web automation expert. Return only CSS selectors."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            selector = response.choices[0].message.content.strip()
            # Clean the selector
            selector = selector.strip('`"\'')
            return selector
            
        except Exception as e:
            print(f"⚠️ GPT-4o error: {e}")
            return 'a[href*="/feed/update/"]:first-of-type'
    
    def _extract_reactor_profiles(self, page) -> List[Dict[str, Any]]:
        """Extract detailed profile information from the reactions modal"""
        
        reactors = []
        
        # Try multiple selectors for reactor elements
        reactor_selectors = [
            'div[data-finite-scroll-hotkey-item]',
            '.artdeco-list__item',
            '[data-view-name="profile-card"]',
            'li[data-urn]'
        ]
        
        reactor_elements = []
        for selector in reactor_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"✅ Found {len(elements)} reactor elements with: {selector}")
                reactor_elements = elements
                break
        
        # Process each reactor
        for i, element in enumerate(reactor_elements):
            try:
                element_text = element.inner_text()
                
                # Skip empty elements
                if not element_text or len(element_text.strip()) < 5:
                    continue
                
                # Extract name (usually first line)
                lines = element_text.strip().split('\n')
                name = lines[0].strip() if lines else "Unknown"
                
                # Skip if name looks invalid
                if name.lower() in ['view', 'profile', 'degree', 'connection', '']:
                    continue
                
                # Extract profile URL
                profile_url = None
                links = element.query_selector_all('a[href*="/in/"]')
                if links:
                    profile_url = links[0].get_attribute('href')
                    if profile_url and not profile_url.startswith('http'):
                        profile_url = f"https://www.linkedin.com{profile_url}"
                
                # Extract connection degree
                connection_degree = "Unknown"
                if "1st degree connection" in element_text or "1st" in element_text:
                    connection_degree = "1st"
                elif "2nd degree connection" in element_text or "2nd" in element_text:
                    connection_degree = "2nd"
                elif "3rd degree connection" in element_text or "3rd" in element_text:
                    connection_degree = "3rd"
                
                # Extract title/company info
                title = "N/A"
                company = "N/A"
                
                # Try to extract from element text
                for line in lines[1:]:
                    line = line.strip()
                    if line and not any(skip in line.lower() for skip in ['view', 'profile', 'degree', 'connection']):
                        if title == "N/A":
                            title = line
                        elif company == "N/A" and ' at ' in line:
                            company = line.split(' at ')[-1]
                        elif company == "N/A":
                            company = line
                
                reactor_data = {
                    "name": name,
                    "title": title,
                    "company": company,
                    "profile_url": profile_url,
                    "connection_degree": connection_degree,
                    "extraction_timestamp": datetime.now().isoformat(),
                    "element_text": element_text
                }
                
                reactors.append(reactor_data)
                print(f"✅ Extracted reactor {i+1}: {name}")
                
            except Exception as e:
                print(f"⚠️ Error processing reactor {i+1}: {e}")
                continue
        
        return reactors