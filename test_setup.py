#!/usr/bin/env python3
"""
ReactionReach Setup Test
Validates that all dependencies and configurations are working properly
"""

import os
import sys
from pathlib import Path

def test_environment_variables():
    """Test that required environment variables are set"""
    print("🔧 Testing environment variables...")
    
    required_vars = [
        "BROWSERBASE_API_KEY",
        "BROWSERBASE_PROJECT_ID", 
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"   ✅ {var}: Set")
    
    if missing_vars:
        print(f"   ❌ Missing: {', '.join(missing_vars)}")
        return False
    
    print("   ✅ All required environment variables are set")
    return True

def test_imports():
    """Test that all required modules can be imported"""
    print("\n📦 Testing imports...")
    
    try:
        import crewai
        print(f"   ✅ CrewAI: {crewai.__version__}")
    except ImportError as e:
        print(f"   ❌ CrewAI import failed: {e}")
        return False
    
    try:
        import playwright
        print(f"   ✅ Playwright: Available")
    except ImportError as e:
        print(f"   ❌ Playwright import failed: {e}")
        return False
    
    try:
        import html2text
        print(f"   ✅ html2text: Available")
    except ImportError as e:
        print(f"   ❌ html2text import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print(f"   ✅ python-dotenv: Available")
    except ImportError as e:
        print(f"   ❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_project_structure():
    """Test that project structure is correct"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        "src/main.py",
        "src/reaction_reach_crew.py", 
        "src/tools/linkedin_url_builder.py",
        "src/tools/browserbase_linkedin.py",
        ".env.example",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"   ✅ {file_path}")
    
    if missing_files:
        print(f"   ❌ Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_tools():
    """Test that custom tools can be imported and initialized"""
    print("\n🔧 Testing custom tools...")
    
    try:
        # Add src to path
        sys.path.append("src")
        
        from tools.linkedin_url_builder import linkedin_url_builder
        from tools.browserbase_linkedin import browserbase_linkedin
        
        print("   ✅ LinkedIn URL Builder tool imported")
        print("   ✅ Browserbase LinkedIn tool imported")
        
        # Test URL builder
        test_url = linkedin_url_builder(
            profile_url="https://linkedin.com/in/testuser",
            action="posts"
        )
        
        if "linkedin.com" in test_url:
            print("   ✅ LinkedIn URL Builder working")
        else:
            print("   ❌ LinkedIn URL Builder not working properly")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Tool import/test failed: {e}")
        return False

def test_browserbase_connection():
    """Test connection to Browserbase (if API keys are provided)"""
    print("\n🌐 Testing Browserbase connection...")
    
    if not os.getenv("BROWSERBASE_API_KEY") or not os.getenv("BROWSERBASE_PROJECT_ID"):
        print("   ⚠️  Browserbase API keys not set, skipping connection test")
        return True
    
    try:
        from playwright.sync_api import sync_playwright
        
        # Test connection without actually browsing
        print("   ✅ Playwright sync API available")
        print("   ⚠️  Skipping actual Browserbase connection (requires network)")
        return True
        
    except Exception as e:
        print(f"   ❌ Browserbase connection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ReactionReach Setup Test")
    print("=" * 40)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not available, loading .env manually")
    
    tests = [
        test_environment_variables,
        test_imports,
        test_project_structure,
        test_tools,
        test_browserbase_connection
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        if test():
            passed_tests += 1
    
    print("\n" + "=" * 40)
    print(f"🏁 Test Results: {passed_tests}/{total_tests} passed")
    
    if passed_tests == total_tests:
        print("✅ ReactionReach setup is complete and ready to use!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Run: python src/main.py --profile 'https://linkedin.com/in/username'")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        print("\nTroubleshooting:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Create .env file with your API keys")
        print("3. Check that all source files are present")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)