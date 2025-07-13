#!/usr/bin/env python3
"""
Debug Gmail MCP server to understand why drafts aren't appearing
"""
import json
import subprocess
import tempfile
import os

def debug_gmail_mcp():
    """Debug Gmail MCP server functionality"""
    
    print("🔍 Debugging Gmail MCP Server")
    print("=" * 50)
    
    # Check credentials
    print("1. Checking credentials...")
    creds_file = os.path.expanduser("~/.gmail-mcp/credentials.json")
    oauth_file = os.path.expanduser("~/.gmail-mcp/gcp-oauth.keys.json")
    
    if os.path.exists(creds_file):
        with open(creds_file, 'r') as f:
            creds = json.load(f)
        print(f"✅ Credentials found: {list(creds.keys())}")
        print(f"🔑 Access token: {creds.get('access_token', 'N/A')[:20]}...")
        print(f"📅 Expiry: {creds.get('expiry_date', 'N/A')}")
    else:
        print("❌ No credentials found")
        return
    
    if os.path.exists(oauth_file):
        with open(oauth_file, 'r') as f:
            oauth = json.load(f)
        print(f"✅ OAuth config found")
        client_id = oauth.get('installed', {}).get('client_id', 'N/A')
        print(f"🆔 Client ID: {client_id[:20]}...")
    else:
        print("❌ No OAuth config found")
        return
    
    # Test 1: Simple draft with minimal data
    print("\n2. Testing simple draft creation...")
    
    simple_draft = {
        "to": ["adam@mysimplestack.com"],
        "subject": "DEBUG: Simple Test Draft",
        "body": "This is a simple test draft to debug the Gmail MCP server."
    }
    
    success = create_draft_and_check(simple_draft, "Simple Draft")
    
    if not success:
        print("❌ Simple draft failed - checking server status...")
        check_server_status()
        return
    
    # Test 2: Draft with more complex content
    print("\n3. Testing complex draft creation...")
    
    complex_draft = {
        "to": ["adam@mysimplestack.com"],
        "subject": "DEBUG: Complex Test Draft with LinkedIn Data",
        "body": """Hi Adam,

This is a test of the LinkedIn → Gmail integration.

Contact Details:
- Name: Test Contact
- Company: Test Corp
- Title: Software Engineer
- Connection: 1st degree

This draft should appear in your Gmail drafts folder.

Best regards,
LinkedIn Extractor Bot

---
Generated at: {datetime.now()}
"""
    }
    
    success = create_draft_and_check(complex_draft, "Complex Draft")
    
    # Test 3: Check Gmail API directly
    print("\n4. Testing Gmail API access...")
    test_gmail_api_access()

def create_draft_and_check(email_data, test_name):
    """Create a draft and check for errors"""
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(email_data, f, indent=2)
            temp_file = f.name
        
        print(f"📝 Creating {test_name}...")
        print(f"📧 Subject: {email_data['subject']}")
        
        # Call Gmail MCP with verbose output
        result = subprocess.run([
            "npx", "@gongrzhe/server-gmail-autoauth-mcp",
            "draft_email",
            "--input", temp_file
        ], capture_output=True, text=True, timeout=60)
        
        print(f"📤 Return code: {result.returncode}")
        print(f"📤 STDOUT: {result.stdout}")
        if result.stderr:
            print(f"🚨 STDERR: {result.stderr}")
        
        if result.returncode == 0:
            print(f"✅ {test_name} created successfully!")
            return True
        else:
            print(f"❌ {test_name} failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {test_name}: {e}")
        return False
    finally:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.unlink(temp_file)

def check_server_status():
    """Check Gmail MCP server status"""
    
    print("\n🔍 Checking server status...")
    
    try:
        # Try to get help/version info
        result = subprocess.run([
            "npx", "@gongrzhe/server-gmail-autoauth-mcp", 
            "--version"
        ], capture_output=True, text=True, timeout=30)
        
        print(f"📦 Server version info:")
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
    except Exception as e:
        print(f"❌ Error checking server: {e}")

def test_gmail_api_access():
    """Test direct Gmail API access"""
    
    print("🔗 Testing Gmail API access...")
    
    # Try to re-authenticate
    try:
        print("🔄 Re-testing authentication...")
        result = subprocess.run([
            "npx", "@gongrzhe/server-gmail-autoauth-mcp",
            "auth"
        ], capture_output=True, text=True, timeout=60)
        
        print(f"🔐 Auth result: {result.returncode}")
        if result.stdout:
            print(f"📤 Auth output: {result.stdout}")
        if result.stderr:
            print(f"🚨 Auth errors: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Auth test error: {e}")

if __name__ == "__main__":
    debug_gmail_mcp()
    
    print(f"\n💡 After running this debug:")
    print(f"1. Check your Gmail drafts folder")
    print(f"2. Look for subjects starting with 'DEBUG:'")
    print(f"3. If still no drafts, there may be an API scope issue")
    print(f"4. Try logging into Gmail web interface to refresh")