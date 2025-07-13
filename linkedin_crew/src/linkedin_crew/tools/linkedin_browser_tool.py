"""
Custom LinkedIn Browser Tool for CrewAI
Wraps Browserbase functionality for LinkedIn automation
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
import os
import json
import time
import logging
from browserbase import Browserbase
from playwright.sync_api import sync_playwright, Browser, Page
import openai

logger = logging.getLogger(__name__)


class LinkedInBrowserToolSchema(BaseModel):
    """Input schema for LinkedIn Browser Tool"""
    instruction: str = Field(
        ...,
        description="Natural language instruction describing what you want to do on LinkedIn"
    )
    url: Optional[str] = Field(
        None,
        description="URL to navigate to (if applicable)"
    )
    command_type: str = Field(
        "act",
        description="Type of command: 'act', 'navigate', 'extract', or 'observe'"
    )


class LinkedInBrowserTool(BaseTool):
    """
    A tool that uses Browserbase and GPT-4o to automate LinkedIn interactions
    """
    
    name: str = "LinkedIn Browser Tool"
    description: str = """Use this tool to control a web browser and interact with LinkedIn.
    
    Capabilities:
    - Navigate to LinkedIn pages
    - Click buttons and links
    - Extract data from pages
    - Observe and analyze page elements
    
    Command types:
    - 'navigate': Go to a specific URL
    - 'act': Perform actions like clicking
    - 'extract': Get data from the page
    - 'observe': Find and analyze elements
    """
    args_schema: type[BaseModel] = LinkedInBrowserToolSchema
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize private attributes
        self._openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._browserbase_client = Browserbase(api_key=os.getenv("BROWSERBASE_API_KEY"))
        self._browser = None
        self._page = None
        self._session_id = None
    
    def _setup_browser(self):
        """Initialize browser session if not already set up"""
        if not self._browser:
            logger.info("Initializing Browserbase session...")
            
            # Check for pre-authenticated context
            context_id = os.getenv("BROWSERBASE_CONTEXT_ID") or os.getenv("LINKEDIN_CONTEXT_ID") or os.getenv("CONTEXT_ID")
            
            # Create Browserbase session with context if available
            session_params = {
                "project_id": os.getenv("BROWSERBASE_PROJECT_ID"),
                "keep_alive": True
            }
            
            if context_id:
                session_params["browser_settings"] = {
                    "context": {
                        "id": context_id,
                        "persist": True
                    }
                }
                logger.info(f"Using pre-authenticated context: {context_id}")
            
            session = self._browserbase_client.sessions.create(**session_params)
            self._session_id = session.id
            
            # Connect to browser
            playwright = sync_playwright().start()
            self._browser = playwright.chromium.connect_over_cdp(session.connect_url)
            self._page = self._browser.contexts[0].pages[0]
            
            logger.info(f"Browser session created: {self._session_id}")
    
    def _take_screenshot(self) -> str:
        """Take a screenshot and return base64 encoded image"""
        if not self._page:
            return ""
        screenshot_bytes = self._page.screenshot()
        import base64
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    def _ask_gpt(self, instruction: str, screenshot: str) -> Dict[str, Any]:
        """Ask GPT-4o to analyze the page and provide actions"""
        response = self._openai_client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=[
                {
                    "role": "system",
                    "content": """You are a web automation assistant helping to interact with LinkedIn.
                    Analyze the screenshot and provide specific actions to take.
                    For extraction tasks, return structured data.
                    For observation tasks, describe what you see.
                    For action tasks, provide specific selectors or instructions."""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000,
            temperature=0.1
        )
        
        return {"response": response.choices[0].message.content}
    
    def _run(
        self,
        instruction: str,
        url: Optional[str] = None,
        command_type: str = "act"
    ) -> str:
        """Execute the browser automation task"""
        try:
            self._setup_browser()
            
            # Handle navigation
            if command_type == "navigate" and url:
                self._page.goto(url, wait_until="networkidle")
                time.sleep(2)  # Let page settle
                return f"Successfully navigated to {url}"
            
            # Take screenshot for GPT analysis
            screenshot = self._take_screenshot()
            
            # Get GPT's analysis
            gpt_response = self._ask_gpt(instruction, screenshot)
            
            if command_type == "observe":
                return f"Observation: {gpt_response['response']}"
            
            elif command_type == "extract":
                # Try to extract structured data from GPT's response
                response_text = gpt_response['response']
                try:
                    # Look for JSON in the response
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        extracted_data = json.loads(json_match.group())
                        return f"Extracted data: {json.dumps(extracted_data, indent=2)}"
                except:
                    pass
                return f"Extracted: {response_text}"
            
            elif command_type == "act":
                # Parse GPT's response for action instructions
                response_text = gpt_response['response']
                
                # Simple implementation - look for common patterns
                if "click" in response_text.lower():
                    # Try to extract selector from response
                    # This is simplified - in production you'd have better parsing
                    if "first post" in instruction.lower():
                        try:
                            # Click first notification link
                            self._page.click('a[href*="/feed/update/"]', timeout=5000)
                            time.sleep(2)
                            return "Successfully clicked on the first post notification"
                        except:
                            pass
                    elif "reaction" in instruction.lower():
                        try:
                            # Try common reaction selectors
                            selectors = [
                                'button[aria-label*="reaction"]',
                                'span:text-matches("\\d+ reaction")',
                                'button:has-text("others")',
                                '[data-test-id="social-actions__reaction-count"]'
                            ]
                            for selector in selectors:
                                try:
                                    self._page.click(selector, timeout=2000)
                                    time.sleep(2)
                                    return "Successfully clicked on reactions area"
                                except:
                                    continue
                        except:
                            pass
                
                return f"Action result: {response_text}"
            
            else:
                return f"Unknown command type: {command_type}"
                
        except Exception as e:
            logger.error(f"Error in LinkedIn browser tool: {str(e)}")
            return f"Error: {str(e)}"
    
    def close(self):
        """Clean up browser resources"""
        if self._browser:
            self._browser.close()
            self._browser = None
            self._page = None
        if self._session_id and self._browserbase_client:
            try:
                self._browserbase_client.sessions.stop(self._session_id)
            except:
                pass
            self._session_id = None