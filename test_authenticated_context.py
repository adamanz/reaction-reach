#!/usr/bin/env python3
"""
Test authenticated context by creating new session and accessing LinkedIn
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def create_session_with_context(context_id: str):
    """Create new session with authenticated context"""
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
    return session

def main():
    """Test the authenticated context"""
    context_id = "7335ed5e-28c0-4af9-b911-0fe90dee9521"
    
    print(f"🚀 Testing authenticated context: {context_id}")
    print("=" * 60)
    
    # Create session with authenticated context
    print("🌐 Creating session with authenticated context...")
    session = create_session_with_context(context_id)
    
    print(f"✅ Session created: {session.id}")
    print(f"🌐 Session URL: https://browserbase.com/sessions/{session.id}")
    print(f"📋 Context ID: {context_id}")
    
    print("\n📝 Session ready for LinkedIn access!")
    print("The context should have your LinkedIn authentication saved.")
    
    return session

if __name__ == "__main__":
    session = main()