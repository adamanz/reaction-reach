#!/usr/bin/env python3
"""
Example script to run the LinkedIn Reaction Reach crew
"""

from linkedin_reaction_reach.crew import LinkedInReactionReachCrew


def main():
    """Run the crew with example inputs"""
    
    # Configure inputs
    inputs = {
        # Optional: Specify a custom Browserbase context ID
        # 'context_id': 'your-context-id-here',
        
        # Optional: Maximum retries for extraction
        'max_retries': 3,
        
        # Optional: Reveal personal emails (uses Apollo credits)
        'reveal_personal_emails': False
    }
    
    print("🚀 Starting LinkedIn Reaction Reach Crew")
    print("=" * 50)
    
    # Create and run the crew
    crew = LinkedInReactionReachCrew().crew()
    result = crew.kickoff(inputs=inputs)
    
    print("\n" + "=" * 50)
    print("✅ Crew execution completed!")
    print("📄 Check output/linkedin_reactions_report.md for results")
    
    return result


if __name__ == "__main__":
    main()