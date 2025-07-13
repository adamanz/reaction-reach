#!/usr/bin/env python3
"""
Direct test of Gmail MCP functionality
"""
import json
import subprocess
import tempfile
import os

def test_gmail_draft():
    """Test creating a Gmail draft directly"""
    
    print("🧪 Testing Gmail MCP Draft Creation...")
    
    # Test email data
    test_email = {
        "to": ["test@example.com"],
        "subject": "Test Draft from LinkedIn Integration",
        "body": "This is a test email draft created from the LinkedIn reactions extractor.\n\nPlease ignore this test message."
    }
    
    print(f"📧 Test email: {test_email}")
    
    try:
        # Create temporary file for the email data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_email, f, indent=2)
            temp_file = f.name
        
        print(f"📁 Created temp file: {temp_file}")
        
        # Try to call Gmail MCP server directly
        print("🔄 Calling Gmail MCP server...")
        
        result = subprocess.run([
            "npx", "@gongrzhe/server-gmail-autoauth-mcp",
            "draft_email",
            "--input", temp_file
        ], capture_output=True, text=True, timeout=30)
        
        print(f"📤 Command executed")
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Gmail draft creation successful!")
            return True
        else:
            print(f"❌ Gmail draft creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gmail MCP: {e}")
        return False
    finally:
        # Clean up temp file
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)

def test_gmail_mcp_status():
    """Check Gmail MCP server status"""
    
    print("\n🔍 Checking Gmail MCP Server Status...")
    
    # Check if credentials exist
    creds_file = os.path.expanduser("~/.gmail-mcp/credentials.json")
    oauth_file = os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")
    
    print(f"📁 Credentials file: {creds_file} - {'✅' if os.path.exists(creds_file) else '❌'}")
    print(f"📁 OAuth file: {oauth_file} - {'✅' if os.path.exists(oauth_file) else '❌'}")
    
    if os.path.exists(creds_file):
        try:
            with open(creds_file, 'r') as f:
                creds = json.load(f)
            print(f"🔑 Credentials contain: {list(creds.keys())}")
        except Exception as e:
            print(f"❌ Error reading credentials: {e}")

if __name__ == "__main__":
    test_gmail_mcp_status()
    test_gmail_draft()