#!/usr/bin/env python3
"""
Create new session with existing context and navigate to LinkedIn
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def create_session_with_context(context_id: str):
    """Create new session with existing context"""
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
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    
    print(f"🚀 Creating new session with context: {context_id}")
    print("=" * 60)
    
    # Create session with existing context
    session = create_session_with_context(context_id)
    
    print(f"✅ Session created: {session.id}")
    print(f"🌐 Session URL: https://browserbase.com/sessions/{session.id}")
    print(f"📋 Context ID: {context_id}")
    
    print("\n📝 Ready to navigate to LinkedIn!")
    
    return session

if __name__ == "__main__":
    session = main()