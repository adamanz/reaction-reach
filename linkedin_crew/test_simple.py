#!/usr/bin/env python3
"""
Simple test of the LinkedIn extraction without CrewAI complexity
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test that we have the required environment variables
print("Environment check:")
print(f"BROWSERBASE_API_KEY: {'✓' if os.getenv('BROWSERBASE_API_KEY') else '✗'}")
print(f"BROWSERBASE_PROJECT_ID: {'✓' if os.getenv('BROWSERBASE_PROJECT_ID') else '✗'}")
print(f"OPENAI_API_KEY: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")

# Test the original script
print("\nRunning original LinkedIn extractor...")
import sys
sys.path.insert(0, '..')
from smart_linkedin_extractor import SmartLinkedInExtractor

if __name__ == "__main__":
    try:
        extractor = SmartLinkedInExtractor()
        extractor.run()
    except Exception as e:
        print(f"Error: {e}")