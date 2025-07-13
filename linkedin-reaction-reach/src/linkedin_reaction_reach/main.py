#!/usr/bin/env python3
"""
Main entry point for LinkedIn Reaction Reach CrewAI
"""

import sys
import argparse
from linkedin_reaction_reach.crew import LinkedInReactionReachCrew


def run():
    """
    Run the LinkedIn Reaction Reach crew
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract LinkedIn reactions and enrich with emails')
    parser.add_argument(
        '--context-id',
        type=str,
        help='Browserbase context ID for LinkedIn authentication',
        default=None
    )
    parser.add_argument(
        '--max-retries',
        type=int,
        help='Maximum retries for extraction',
        default=3
    )
    parser.add_argument(
        '--reveal-personal-emails',
        action='store_true',
        help='Reveal personal emails in Apollo (uses credits)'
    )
    
    args = parser.parse_args()
    
    # Prepare inputs for the crew
    inputs = {
        'context_id': args.context_id,
        'max_retries': args.max_retries,
        'reveal_personal_emails': args.reveal_personal_emails
    }
    
    # Remove None values
    inputs = {k: v for k, v in inputs.items() if v is not None}
    
    print("🚀 Starting LinkedIn Reaction Reach Crew...")
    print(f"📊 Configuration: {inputs}")
    
    # Create and run the crew
    crew = LinkedInReactionReachCrew().crew()
    result = crew.kickoff(inputs=inputs)
    
    print("\n✅ Process completed!")
    print("📄 Check output/linkedin_reactions_report.md for the full report")
    
    return result


if __name__ == "__main__":
    run()