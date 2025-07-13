#!/usr/bin/env python
# src/reaction_reach_v2/main.py
import sys
import os
from reaction_reach_v2.crew import ReactionReachV2Crew


def run():
    """
    Run the crew.
    """
    # You can customize these inputs as needed
    inputs = {
        'linkedin_profile': os.getenv('LINKEDIN_PROFILE_URL', 'https://linkedin.com/in/adamanz'),
        'days_back': int(os.getenv('TARGET_DAYS_BACK', '30'))
    }
    
    print("🚀 Starting LinkedIn Reaction Reach Intelligence Gathering...")
    print(f"📊 Target Profile: {inputs['linkedin_profile']}")
    print(f"📅 Days Back: {inputs['days_back']}")
    
    ReactionReachV2Crew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'linkedin_profile': os.getenv('LINKEDIN_PROFILE_URL', 'https://linkedin.com/in/adamanz'),
        'days_back': int(os.getenv('TARGET_DAYS_BACK', '30'))
    }
    
    try:
        ReactionReachV2Crew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ReactionReachV2Crew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'linkedin_profile': os.getenv('LINKEDIN_PROFILE_URL', 'https://linkedin.com/in/adamanz'),
        'days_back': int(os.getenv('TARGET_DAYS_BACK', '30'))
    }
    
    try:
        ReactionReachV2Crew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    run()