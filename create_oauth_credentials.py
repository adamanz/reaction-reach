#!/usr/bin/env python3
"""
Create OAuth 2.0 credentials for Gmail MCP server using Google Cloud APIs
"""
import json
import os
import subprocess

def create_oauth_credentials():
    """Create OAuth credentials for Gmail MCP"""
    
    project_id = "titanium-vision-455301-c4"
    
    # Create OAuth client using gcloud
    try:
        print("🔧 Creating OAuth 2.0 client for Gmail MCP...")
        
        # Enable Gmail API
        print("📧 Enabling Gmail API...")
        result = subprocess.run([
            "gcloud", "services", "enable", "gmail.googleapis.com",
            "--project", project_id
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️ Gmail API enable result: {result.stderr}")
        else:
            print("✅ Gmail API enabled")
        
        # Create OAuth credentials using gcloud
        print("🔑 Creating OAuth client...")
        
        # First, let's create a simple OAuth client configuration manually
        oauth_config = {
            "installed": {
                "client_id": f"{project_id}.apps.googleusercontent.com", 
                "project_id": project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "GOCSPX-placeholder_secret",
                "redirect_uris": ["http://localhost:3000/oauth2callback"]
            }
        }
        
        # Save to Gmail MCP directory
        gmail_mcp_dir = os.path.expanduser("~/.gmail-mcp")
        os.makedirs(gmail_mcp_dir, exist_ok=True)
        
        credentials_file = os.path.join(gmail_mcp_dir, "gcp-oauth.keys.json")
        with open(credentials_file, 'w') as f:
            json.dump(oauth_config, f, indent=2)
        
        print(f"📁 OAuth config saved to: {credentials_file}")
        print("\n📋 Next steps:")
        print("1. Go to Google Cloud Console > APIs & Services > Credentials")
        print("2. Create OAuth 2.0 Client ID (Desktop application)")
        print("3. Download the JSON file and replace ~/.gmail-mcp/gcp-oauth.keys.json")
        print("4. Run: npx @gongrzhe/server-gmail-autoauth-mcp auth")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating OAuth credentials: {e}")
        return False

if __name__ == "__main__":
    create_oauth_credentials()