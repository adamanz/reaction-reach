#!/usr/bin/env python3
"""
Create new session with context and navigate to LinkedIn feed
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def create_session_with_context(context_id: str):
    """Create new session with the context"""
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
    # Context ID from session ddb0a969-886b-4c2d-9039-d0db67607971
    context_id = "7335ed5e-28c0-4af9-b911-0fe90dee9521"
    
    print(f"🚀 Creating new session with context: {context_id}")
    print("=" * 60)
    
    # Create session with context
    session = create_session_with_context(context_id)
    
    print(f"✅ Session created: {session.id}")
    print(f"🌐 Session URL: https://browserbase.com/sessions/{session.id}")
    print(f"📋 Context ID: {context_id}")
    
    print("\n📝 Ready to navigate to LinkedIn feed!")
    
    return session

if __name__ == "__main__":
    session = main()