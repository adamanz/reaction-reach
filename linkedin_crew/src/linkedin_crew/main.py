#!/usr/bin/env python
import sys
import warnings
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from linkedin_crew.crew import LinkedinCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try current directory
    load_dotenv()

def run():
    """
    Run the crew.
    """
    # Check required environment variables
    required_vars = ['BROWSERBASE_API_KEY', 'BROWSERBASE_PROJECT_ID', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return
    
    inputs = {
        'context_id': os.getenv('BROWSERBASE_CONTEXT_ID')  # Optional pre-authenticated session
    }
    
    try:
        LinkedinCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        LinkedinCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        LinkedinCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        LinkedinCrew().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
