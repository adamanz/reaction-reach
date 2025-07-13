#!/usr/bin/env python3
"""
Start LinkedIn session with existing authenticated context
"""

from browserbase import Browserbase
import os
from dotenv import load_dotenv

load_dotenv()

def useContext(contextId):
    bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
    session = bb.sessions.create(
      project_id=os.environ["BROWSERBASE_PROJECT_ID"],
      browser_settings={
        "context": {
          "id": contextId,
          "persist": True
        }
      },
      proxies=True  # Enable stealth mode
    )
    print("Session ID:", session.id)
    print("Context ID:", contextId)
    print("Session URL:", f"https://www.browserbase.com/sessions/{session.id}")
    return session

def main():
    # Use the working context ID from .env
    context_id = os.environ["LINKEDIN_CONTEXT_ID"]  # b03b0494-a12d-4e4c-b99f-59651591529e
    
    print(f"🚀 Starting LinkedIn session with context: {context_id}")
    session = useContext(context_id)
    
    print(f"\n✅ Session created successfully!")
    print(f"🔗 You can view the session at: https://www.browserbase.com/sessions/{session.id}")
    print(f"💾 Context will persist any authentication state")
    
    return session

if __name__ == "__main__":
    session = main()