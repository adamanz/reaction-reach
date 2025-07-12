# CrewAI Implementation Patterns for ReactionReach

## Agent Design Patterns

### Role-Goal-Backstory Pattern
```python
Agent(
    role="Specific functional title",
    goal="Clear, measurable objective", 
    backstory="Context that shapes agent behavior",
    tools=[relevant_tools],
    memory=True,  # Enable for context sharing
    verbose=True,  # For debugging
    allow_delegation=False  # Control task delegation
)
```

### Tool Integration Pattern
```python
from crewai_tools import StagehandTool

# Initialize tool with Browserbase
stagehand_tool = StagehandTool(
    api_key=os.environ["BROWSERBASE_API_KEY"],
    project_id=os.environ["BROWSERBASE_PROJECT_ID"], 
    model_api_key=os.environ["OPENAI_API_KEY"],
    model_name=AvailableModel.GPT_4O,
)

# Assign to agents
agent = Agent(
    role="Web Navigator",
    tools=[stagehand_tool],
    # ... other config
)
```

## Task Design Patterns

### Sequential Task Dependencies
```python
# Task 1: Authentication
auth_task = Task(
    description="Navigate to LinkedIn and authenticate",
    expected_output="Confirmation of successful login",
    agent=navigator_agent,
)

# Task 2: Discovery (depends on auth)
discovery_task = Task(
    description="Find user posts from last 30 days",
    expected_output="List of post URLs and metadata", 
    agent=post_hunter_agent,
    context=[auth_task],  # Access auth_task output
)
```

### Parameterized Task Descriptions
```python
extraction_task = Task(
    description="""
    Extract reaction data from posts: {post_urls}
    For each post:
    1. Navigate to URL
    2. Click reaction counts
    3. Extract reactor details
    4. Handle pagination
    
    Use delays of {delay_seconds} seconds between actions.
    """,
    expected_output="JSON array of reaction data",
    agent=harvester_agent,
)

# Pass parameters when running
crew.kickoff(inputs={
    "post_urls": ["url1", "url2"], 
    "delay_seconds": 3
})
```

## Crew Configuration Patterns

### Production Crew Setup
```python
crew = Crew(
    agents=[navigator, hunter, harvester, analyst, reporter],
    tasks=[auth_task, discovery_task, extraction_task, analysis_task, report_task],
    process=Process.sequential,  # Execute tasks in order
    verbose=True,                # Enable logging
    memory=True,                 # Share context between agents
    max_rpm=10,                  # Rate limiting
    manager_llm=ChatOpenAI(model="gpt-4o"),  # Manager for complex coordination
)
```

### Error Handling Pattern
```python
try:
    result = crew.kickoff(inputs={"profile_url": profile_url})
except Exception as e:
    # Handle specific CrewAI errors
    if "rate limit" in str(e).lower():
        print("Rate limited - waiting before retry")
        time.sleep(60)
        result = crew.kickoff(inputs={"profile_url": profile_url})
    else:
        print(f"Crew execution failed: {e}")
        # Fallback behavior
```

## Memory Management Patterns

### Agent Memory Configuration
```python
# Short-term memory for task context
agent = Agent(
    role="Data Processor",
    memory=True,  # Enables automatic memory
    # CrewAI handles memory persistence automatically
)
```

### Cross-Agent Context Sharing
```python
# Context flows automatically between tasks
task2 = Task(
    description="Use the data from the previous task to analyze patterns",
    agent=analyst_agent,
    context=[task1],  # Gets task1 output automatically
)
```

## Tool Development Patterns

### Custom Tool Creation
```python
from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class LinkedInReactionTool(BaseTool):
    name: str = "LinkedIn Reaction Extractor"
    description: str = "Extracts reaction data from LinkedIn posts"
    
    class LinkedInReactionInput(BaseModel):
        post_url: str = Field(..., description="LinkedIn post URL")
        max_reactions: int = Field(100, description="Max reactions to extract")
    
    args_schema: Type[BaseModel] = LinkedInReactionInput
    
    def _run(self, post_url: str, max_reactions: int = 100) -> str:
        # Implementation using Stagehand/Browserbase
        # Return structured data as string
        pass
```

### Tool Error Handling
```python
def _run(self, post_url: str) -> str:
    try:
        # Tool implementation
        return reaction_data
    except Exception as e:
        return f"Error extracting reactions: {str(e)}"
```

## Debugging Patterns

### Verbose Logging
```python
import logging

# Enable CrewAI debug logging
logging.basicConfig(level=logging.DEBUG)

crew = Crew(
    agents=[...],
    tasks=[...],
    verbose=True,  # Agent-level verbosity
)
```

### Task Result Inspection
```python
result = crew.kickoff(inputs={"profile_url": url})

# Access individual task results
for task_result in result.tasks_output:
    print(f"Task: {task_result.description}")
    print(f"Output: {task_result.raw}")
    print(f"Agent: {task_result.agent}")
```

## Performance Patterns

### Parallel Execution (when possible)
```python
# For independent tasks, use hierarchical process
crew = Crew(
    agents=[...],
    tasks=[...], 
    process=Process.hierarchical,  # Enables parallelization
    manager_llm=ChatOpenAI(model="gpt-4o"),
)
```

### Resource Management
```python
# Cleanup pattern
try:
    result = crew.kickoff(inputs=inputs)
finally:
    # Cleanup Browserbase sessions
    stagehand_tool.close()
```

## Integration Patterns

### Environment Configuration
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Validate required environment variables
required_vars = [
    "BROWSERBASE_API_KEY",
    "BROWSERBASE_PROJECT_ID", 
    "OPENAI_API_KEY"
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")
```

### Output Processing
```python
def process_crew_output(result):
    """Process CrewAI output into structured data"""
    
    # Extract final task output
    final_output = result.tasks_output[-1].raw
    
    # Parse and structure the data
    structured_data = parse_intelligence_report(final_output)
    
    # Save to files
    save_json(structured_data, "data/reactions.json")
    save_markdown(final_output, "data/report.md")
    
    return structured_data
```

These patterns provide a solid foundation for implementing the ReactionReach system using CrewAI best practices.