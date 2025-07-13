#!/usr/bin/env python3
"""
Simple runner for ReactionReach V2 crew
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run
from reaction_reach_v2.main import run

if __name__ == "__main__":
    run()