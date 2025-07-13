#!/usr/bin/env python3
"""
Create fresh context and session, then get context ID
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

def get_session_context_id(session_id: str):
    """Get context ID for a session using API"""
    import requests
    
    response = requests.get(
        f"https://api.browserbase.com/v1/sessions/{session_id}",
        headers={"X-BB-API-Key": os.environ["BROWSERBASE_API_KEY"]}
    )
    
    if response.status_code == 200:
        session_data = response.json()
        return session_data.get("contextId")
    else:
        return None

def main():
    print("🚀 Creating Fresh Context and Session")
    print("=" * 50)
    
    # Step 1: Create new context
    print("📦 Creating new context...")
    context_id = create_context()
    print(f"✅ Created context: {context_id}")
    
    # Step 2: Create session with context
    print("🌐 Creating session with context...")
    session = create_session_with_context(context_id)
    print(f"✅ Created session: {session.id}")
    
    # Step 3: Verify context ID via API
    print("🔍 Verifying context ID via API...")
    api_context_id = get_session_context_id(session.id)
    print(f"✅ API confirms context ID: {api_context_id}")
    
    # Step 4: Summary
    print("\n📋 Summary:")
    print(f"Context ID: {context_id}")
    print(f"Session ID: {session.id}")
    print(f"Session URL: https://browserbase.com/sessions/{session.id}")
    print(f"API Context ID: {api_context_id}")
    
    # Verify they match
    if context_id == api_context_id:
        print("✅ Context IDs match!")
    else:
        print("⚠️  Context ID mismatch!")
    
    return context_id, session.id

if __name__ == "__main__":
    context_id, session_id = main()
    print(f"\n🎯 New Context ID: {context_id}")
    print(f"🎯 New Session ID: {session_id}")