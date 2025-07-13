#!/usr/bin/env python3
"""
Create new Browserbase context and session for manual LinkedIn authentication
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv

load_dotenv()

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def create_context():
    """Create a new Browserbase context"""
    context = bb.contexts.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
    return context.id

def create_auth_session(context_id: str):
    """Create authenticated session with context and stealth proxies"""
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
    print("Session URL: https://browserbase.com/sessions/" + session.id)
    return session

def main():
    """Create context and session for manual authentication"""
    print("🚀 Creating LinkedIn Context and Authentication Session")
    print("=" * 60)
    
    try:
        # Step 1: Create new context
        print("📦 Creating new context...")
        context_id = create_context()
        print("Context ID:", context_id)
        
        # Step 2: Create session for manual authentication
        print("🌐 Creating authentication session...")
        session = create_auth_session(context_id)
        
        print("\n✅ Context and session created successfully!")
        print(f"📋 Context ID: {context_id}")
        print(f"🌐 Session URL: https://browserbase.com/sessions/{session.id}")
        
        print("\n📝 Next Steps:")
        print("1. Use the session URL above to manually login to LinkedIn")
        print("2. Navigate to: https://www.linkedin.com/in/adamanz/recent-activity/all/")
        print("3. Complete any LinkedIn verification if needed")
        print(f"4. Add to your .env file: LINKEDIN_CONTEXT_ID={context_id}")
        print("5. The context will persist your authentication for future use!")
        
        return context_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    context_id = main()
    if context_id:
        print(f"\n🎯 New Context ID: {context_id}")
    else:
        print("\n❌ Failed to create context")