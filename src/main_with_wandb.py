#!/usr/bin/env python3
"""
ReactionReach Main Script with Weights & Biases Integration

This script runs the LinkedIn reaction intelligence system with comprehensive
W&B tracking for monitoring agent performance, metrics, and insights.
"""

import os
import sys
import weave
import argparse
from datetime import datetime
from dotenv import load_dotenv
from reaction_reach_crew import create_reaction_reach_crew

# Load environment variables
load_dotenv()

@weave.op()
def run_reaction_reach_analysis(
    target_profile_url: str,
    days_back: int = 30,
    max_posts: int = 10
):
    """
    Main ReactionReach analysis with automatic W&B tracking
    
    :param target_profile_url: LinkedIn profile URL to analyze
    :param days_back: Number of days to look back for posts
    :param max_posts: Maximum number of posts to analyze
    :return: Analysis results
    """
    
    print(f"🎯 Target Profile: {target_profile_url}")
    print(f"📅 Analysis Period: Last {days_back} days")
    print(f"📊 Max Posts: {max_posts}")
    print("-" * 60)
    
    # Log analysis parameters to W&B
    weave.log({
        "target_profile_url": target_profile_url,
        "days_back": days_back,
        "max_posts": max_posts,
        "analysis_start_time": datetime.now().isoformat()
    })
    
    # Create and configure the crew
    crew = create_reaction_reach_crew(
        target_profile_url=target_profile_url,
        days_back=days_back,
        max_posts=max_posts
    )
    
    # Execute the crew with tracking
    print("🚀 Starting LinkedIn intelligence gathering...")
    
    try:
        result = crew.kickoff(inputs={
            "target_profile_url": target_profile_url,
            "days_back": days_back,
            "max_posts": max_posts
        })
        
        # Log successful completion
        weave.log({
            "analysis_status": "completed",
            "analysis_end_time": datetime.now().isoformat(),
            "tasks_completed": len(result.tasks_output) if result else 0
        })
        
        print("✅ Analysis completed successfully!")
        print(f"📋 Report saved to: data/intelligence-report.md")
        
        return result
        
    except Exception as e:
        # Log errors to W&B
        weave.log({
            "analysis_status": "failed",
            "error_message": str(e),
            "analysis_end_time": datetime.now().isoformat()
        })
        
        print(f"❌ Analysis failed: {e}")
        raise

def main():
    """Main entry point with CLI argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="ReactionReach - LinkedIn Reaction Intelligence System"
    )
    parser.add_argument(
        "profile_url", 
        nargs='?',
        help="LinkedIn profile URL to analyze"
    )
    parser.add_argument(
        "--profile", "-p",
        help="LinkedIn profile URL to analyze"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)"
    )
    parser.add_argument(
        "--max-posts", "-m",
        type=int,
        default=10,
        help="Maximum number of posts to analyze (default: 10)"
    )
    parser.add_argument(
        "--project", 
        default="reaction-reach",
        help="W&B project name (default: reaction-reach)"
    )
    parser.add_argument(
        "--no-tracking",
        action="store_true",
        help="Disable W&B tracking"
    )
    
    args = parser.parse_args()
    
    # Determine target profile URL
    target_profile = (
        args.profile_url or 
        args.profile or 
        os.getenv("LINKEDIN_PROFILE_URL")
    )
    
    if not target_profile:
        print("❌ Error: No LinkedIn profile URL provided!")
        print("\nUsage options:")
        print("1. python src/main_with_wandb.py 'https://linkedin.com/in/username'")
        print("2. python src/main_with_wandb.py --profile 'https://linkedin.com/in/username'")
        print("3. Set LINKEDIN_PROFILE_URL in .env file")
        sys.exit(1)
    
    # Validate required environment variables
    required_vars = ["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file configuration.")
        sys.exit(1)
    
    # Initialize Weights & Biases tracking
    if not args.no_tracking:
        project_name = f"{args.project}-{datetime.now().strftime('%Y-%m-%d')}"
        weave.init(project_name=project_name)
        
        print(f"📊 W&B Tracking initialized: {project_name}")
        
        # Log system information
        weave.log({
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "browserbase_configured": bool(os.getenv("BROWSERBASE_API_KEY")),
                "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
            }
        })
    else:
        print("⚠️  W&B tracking disabled")
    
    # Run the analysis
    try:
        result = run_reaction_reach_analysis(
            target_profile_url=target_profile,
            days_back=args.days,
            max_posts=args.max_posts
        )
        
        print("\n" + "="*60)
        print("🎉 ReactionReach Analysis Complete!")
        print("="*60)
        
        if not args.no_tracking:
            wandb_entity = os.getenv('WANDB_ENTITY', 'your-username')
            print(f"📊 View detailed metrics: https://wandb.ai/{wandb_entity}/{project_name}")
        
        print(f"📋 Intelligence report: data/intelligence-report.md")
        print(f"💾 Raw data: data/reactions.json")
        
        return result
        
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        if not args.no_tracking:
            print(f"📊 Check W&B dashboard for error details")
        sys.exit(1)

if __name__ == "__main__":
    main()