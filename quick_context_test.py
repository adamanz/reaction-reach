#!/usr/bin/env python3
"""
Quick test to create LinkedIn context and get session URL for manual authentication
"""

import os
from dotenv import load_dotenv
from browserbase import Browserbase

load_dotenv()

def main():
    print("🚀 Creating LinkedIn Browserbase Context")
    
    # Initialize Browserbase
    bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
    
    # Create a new context
    print("🔧 Creating new context...")
    context = bb.contexts.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
    context_id = context.id
    
    print(f"✅ Created context: {context_id}")
    
    # Create session with context
    print("🌐 Creating session...")
    session = bb.sessions.create(
        project_id=os.environ["BROWSERBASE_PROJECT_ID"],
        browser_settings={
            "context": {
                "id": context_id,
                "persist": True  # Save authentication state
            }
        },
        proxies=True  # Enable stealth mode
    )
    
    print(f"✅ Session created: {session.id}")
    print(f"🌐 Session URL: https://www.browserbase.com/sessions/{session.id}")
    
    print("\n📋 Summary:")
    print(f"Context ID: {context_id}")
    print(f"Session ID: {session.id}")
    print("\n💡 Next steps:")
    print(f"1. Add to .env: LINKEDIN_CONTEXT_ID={context_id}")
    print("2. The session is now ready for LinkedIn authentication")
    print("3. Use MCP tools to navigate and authenticate")
    
    return context_id

if __name__ == "__main__":
    context_id = main()
    print(f"\n🎯 New Context ID: {context_id}")