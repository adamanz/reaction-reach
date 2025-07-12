#!/usr/bin/env python3
"""
ReactionReach - LinkedIn Reaction Intelligence System
Main execution file for the CrewAI-powered LinkedIn engagement analysis
"""

import sys
import os
import argparse
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reaction_reach_crew import create_reaction_reach_crew

def main():
    """Main execution function for ReactionReach"""
    
    # Load environment variables
    load_dotenv()
    
    # Verify required environment variables
    required_env_vars = [
        "BROWSERBASE_API_KEY",
        "BROWSERBASE_PROJECT_ID", 
        "OPENAI_API_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="ReactionReach - LinkedIn Reaction Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --profile "https://linkedin.com/in/johndoe" 
  python main.py --profile "https://linkedin.com/in/johndoe" --days 14 --max-posts 5
  python main.py "https://linkedin.com/in/johndoe"  # Quick format
        """
    )
    
    # Accept profile URL as positional or named argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        # Quick format: python main.py "profile_url"
        profile_url = sys.argv[1]
        days_back = 30  # default
        max_posts = 10  # default
    else:
        # Named arguments format
        parser.add_argument(
            "--profile", "-p",
            required=True,
            help="LinkedIn profile URL to analyze (e.g., https://linkedin.com/in/username)"
        )
        parser.add_argument(
            "--days", "-d",
            type=int,
            default=30,
            help="Number of days to look back for posts (default: 30)"
        )
        parser.add_argument(
            "--max-posts", "-m",
            type=int,
            default=10,
            help="Maximum number of posts to analyze (default: 10)"
        )
        
        args = parser.parse_args()
        profile_url = args.profile
        days_back = args.days
        max_posts = args.max_posts
    
    # Validate LinkedIn URL format
    if not profile_url.startswith("https://linkedin.com/in/") and not profile_url.startswith("https://www.linkedin.com/in/"):
        print("❌ Invalid LinkedIn profile URL format.")
        print("Expected format: https://linkedin.com/in/username")
        sys.exit(1)
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    print("🚀 ReactionReach - LinkedIn Intelligence System")
    print("=" * 50)
    print(f"📊 Target Profile: {profile_url}")
    print(f"📅 Days Back: {days_back}")
    print(f"📝 Max Posts: {max_posts}")
    print(f"🕒 Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Create the ReactionReach crew
        crew = create_reaction_reach_crew(
            target_profile_url=profile_url,
            days_back=days_back,
            max_posts=max_posts
        )
        
        print("🤖 Initializing LinkedIn intelligence agents...")
        print("   🔐 Navigator Agent: Authentication & Stealth Navigation")
        print("   🔍 Post Hunter Agent: Content Discovery")  
        print("   📊 Reaction Harvester Agent: Engagement Extraction")
        print("   🧠 Data Analyst Agent: Pattern Analysis")
        print("   📄 Reporter Agent: Intelligence Reporting")
        print()
        
        # Execute the crew
        print("▶️  Starting LinkedIn intelligence gathering...")
        result = crew.kickoff(inputs={
            "target_profile_url": profile_url,
            "days_back": days_back,
            "max_posts": max_posts,
            "current_date": datetime.date.today().strftime("%Y-%m-%d")
        })
        
        print("\n" + "=" * 50)
        print("✅ ReactionReach Analysis Complete!")
        print("=" * 50)
        print(result)
        
        # Check if report was generated
        report_path = Path("data/intelligence-report.md")
        if report_path.exists():
            print(f"\n📄 Full intelligence report saved to: {report_path}")
            print(f"📁 Report size: {report_path.stat().st_size} bytes")
        
        print(f"\n🕒 Completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        print("\nDebugging tips:")
        print("1. Check your internet connection")
        print("2. Verify LinkedIn profile URL is accessible")
        print("3. Ensure Browserbase API keys are valid")
        print("4. Check if LinkedIn profile has recent posts")
        sys.exit(1)

if __name__ == "__main__":
    main()