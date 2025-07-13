# Weights & Biases Integration with ReactionReach

## Overview

Weights & Biases (W&B) Weave provides automatic tracking and monitoring for CrewAI applications. This integration captures all agent interactions, task executions, LLM calls, and performance metrics for ReactionReach.

## Setup

### 1. Install Dependencies
```bash
pip install weave wandb
```

### 2. W&B Account Setup
- Sign up at [wandb.ai](https://wandb.ai)
- Get your API key from your account settings
- Login: `wandb login`

### 3. Initialize Weave in ReactionReach

Add to your main execution file:

```python
import weave
import os

# Initialize Weave tracking
weave.init(project_name="reaction-reach-linkedin-intelligence")
```

## Integration with ReactionReach

### Enhanced Main Script with W&B Tracking

```python
# src/main_with_wandb.py
import os
import weave
from datetime import datetime
from src.reaction_reach_crew import create_reaction_reach_crew

def main_with_tracking():
    # Initialize Weave tracking
    project_name = f"reaction-reach-{datetime.now().strftime('%Y-%m-%d')}"
    weave.init(project_name=project_name)
    
    # Configuration
    target_profile = os.getenv("LINKEDIN_PROFILE_URL")
    days_back = int(os.getenv("TARGET_DAYS_BACK", "30"))
    max_posts = int(os.getenv("MAX_POSTS_TO_ANALYZE", "10"))
    
    # Create crew with W&B tracking enabled
    crew = create_reaction_reach_crew(
        target_profile_url=target_profile,
        days_back=days_back,
        max_posts=max_posts
    )
    
    # Execute with automatic tracking
    print(f"🚀 Starting ReactionReach analysis with W&B tracking...")
    print(f"📊 View live tracking at: https://wandb.ai/{os.getenv('WANDB_ENTITY', 'your-username')}/{project_name}")
    
    result = crew.kickoff(inputs={
        "target_profile_url": target_profile,
        "days_back": days_back,
        "max_posts": max_posts
    })
    
    print("✅ Analysis complete! Check W&B dashboard for detailed metrics.")
    return result

if __name__ == "__main__":
    main_with_tracking()
```

### Custom Metrics Tracking

```python
# src/tools/wandb_logger.py
import weave
import time
from typing import Dict, Any

class ReactionReachLogger:
    """Custom logger for ReactionReach metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}
    
    @weave.op()
    def log_navigation_success(self, profile_url: str, success: bool):
        """Log LinkedIn navigation attempts"""
        weave.log({
            "navigation_success": success,
            "profile_url": profile_url,
            "timestamp": time.time()
        })
    
    @weave.op()
    def log_post_discovery(self, posts_found: int, target_posts: int):
        """Log post discovery metrics"""
        discovery_rate = posts_found / target_posts if target_posts > 0 else 0
        weave.log({
            "posts_discovered": posts_found,
            "target_posts": target_posts,
            "discovery_rate": discovery_rate
        })
    
    @weave.op()
    def log_reaction_extraction(self, post_id: str, reactions_extracted: int, extraction_time: float):
        """Log reaction extraction performance"""
        weave.log({
            "post_id": post_id,
            "reactions_extracted": reactions_extracted,
            "extraction_time_seconds": extraction_time,
            "reactions_per_second": reactions_extracted / extraction_time if extraction_time > 0 else 0
        })
    
    @weave.op()
    def log_analysis_insights(self, insights: Dict[str, Any]):
        """Log analysis results"""
        weave.log({
            "top_engagers_count": len(insights.get("top_engagers", [])),
            "total_reactions_analyzed": insights.get("total_reactions", 0),
            "unique_companies": len(insights.get("companies", [])),
            "analysis_completion_time": time.time() - self.start_time
        })
    
    @weave.op()
    def log_crew_performance(self, crew_result):
        """Log overall crew performance metrics"""
        total_time = time.time() - self.start_time
        weave.log({
            "total_execution_time": total_time,
            "crew_success": crew_result is not None,
            "tasks_completed": len(crew_result.tasks_output) if crew_result else 0
        })
```

### Enhanced Agent Implementation with Tracking

```python
# Enhanced reaction_reach_crew.py with W&B integration
import weave
from tools.wandb_logger import ReactionReachLogger

def create_reaction_reach_crew_with_tracking(
    target_profile_url: str,
    days_back: int = 30,
    max_posts: int = 10
) -> Crew:
    """Create crew with W&B tracking enabled"""
    
    # Initialize logger
    logger = ReactionReachLogger()
    
    # Enhanced tasks with tracking
    navigate_task = Task(
        description=(
            f"Navigate to LinkedIn profile {target_profile_url} and establish a secure session. "
            f"Log navigation success/failure to W&B. "
            f"Ensure stealth operation and prepare for content discovery. "
            f"Verify the profile is accessible and return the profile's activity feed URL."
        ),
        expected_output="Confirmation of successful LinkedIn navigation with W&B metrics logged",
        agent=linkedin_navigator_agent,
    )
    
    # Add tracking to other tasks...
    
    return crew

# Decorator for automatic performance tracking
@weave.op()
def run_reaction_reach_analysis(target_profile: str, days_back: int = 30):
    """Main analysis function with automatic W&B tracking"""
    crew = create_reaction_reach_crew_with_tracking(
        target_profile_url=target_profile,
        days_back=days_back
    )
    
    result = crew.kickoff(inputs={
        "target_profile_url": target_profile,
        "days_back": days_back
    })
    
    return result
```

## What Gets Tracked Automatically

### CrewAI Operations
- ✅ **Agent Interactions**: Every agent's role, goal, and execution
- ✅ **Task Executions**: Task descriptions, outputs, and dependencies  
- ✅ **LLM Calls**: Model used, tokens consumed, latency, costs
- ✅ **Tool Usage**: Browserbase calls, LinkedIn automation steps
- ✅ **Crew Performance**: Total execution time, success rates

### Custom ReactionReach Metrics
- 📊 **LinkedIn Navigation**: Success/failure rates, profile accessibility
- 🔍 **Post Discovery**: Discovery rates, posts found vs. targeted
- 💡 **Reaction Extraction**: Extraction speed, reaction counts per post
- 📈 **Analysis Quality**: Insights generated, data completeness
- ⚡ **Performance**: Time per task, bottlenecks, optimization opportunities

## W&B Dashboard Views

### 1. Execution Overview
```
📊 Crew Performance Dashboard
├── Total Execution Time: 12.3 minutes
├── Tasks Completed: 5/5 ✅
├── Success Rate: 100%
├── LLM Tokens Used: 15,247
└── Cost: $0.23
```

### 2. Agent Performance
```
🤖 Agent Metrics
├── Navigator Agent: 2.1 min (Auth + Navigation)
├── Post Hunter: 3.7 min (15 posts discovered)  
├── Reaction Harvester: 5.2 min (247 reactions)
├── Data Analyst: 0.8 min (Insights generated)
└── Reporter: 0.5 min (Report created)
```

### 3. LinkedIn Automation Metrics
```
🔍 LinkedIn Intelligence
├── Profile Access: ✅ Successful
├── Posts Discovered: 15/15 (100%)
├── Reactions Extracted: 247 total
├── Top Engagers Identified: 23
└── Industries Analyzed: 12
```

## Environment Configuration

Add to your `.env`:
```bash
# W&B Configuration
WANDB_PROJECT=reaction-reach
WANDB_ENTITY=your-wandb-username
WANDB_API_KEY=your-wandb-api-key

# Optional: Custom tracking settings
WANDB_LOG_MODEL=true
WANDB_SAVE_CODE=true
```

## Usage Examples

### Basic Tracking
```python
import weave
weave.init(project_name="reaction-reach")

# Your existing CrewAI code - tracking is automatic!
crew = create_reaction_reach_crew(profile_url, days_back=30)
result = crew.kickoff()
```

### Advanced Custom Tracking
```python
import weave
from tools.wandb_logger import ReactionReachLogger

@weave.op()
def analyze_competitor_profiles(profiles: list):
    logger = ReactionReachLogger()
    
    for profile in profiles:
        start_time = time.time()
        result = run_reaction_reach_analysis(profile)
        
        logger.log_analysis_insights({
            "profile": profile,
            "execution_time": time.time() - start_time,
            "insights": result
        })
    
    return "Multi-profile analysis complete"

# Usage
competitor_profiles = [
    "https://linkedin.com/in/competitor1",
    "https://linkedin.com/in/competitor2"  
]
analyze_competitor_profiles(competitor_profiles)
```

## Benefits

### 1. **Real-time Monitoring**
- Track LinkedIn automation in real-time
- Identify bottlenecks and failures immediately
- Monitor rate limiting and stealth effectiveness

### 2. **Performance Optimization**
- Compare different LinkedIn profiles/strategies
- Optimize agent configurations based on metrics
- A/B test different automation approaches

### 3. **Compliance Tracking**
- Monitor request rates and delays
- Track detection/blocking incidents
- Ensure respectful automation practices

### 4. **Intelligence Quality**
- Measure insight generation quality
- Track data completeness and accuracy
- Optimize analysis algorithms

## Dashboard URL

After running ReactionReach with W&B, visit:
```
https://wandb.ai/your-username/reaction-reach
```

This provides comprehensive tracking and monitoring for your LinkedIn intelligence operations! 🚀