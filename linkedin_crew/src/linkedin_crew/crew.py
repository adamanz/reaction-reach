from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from linkedin_crew.tools import LinkedInBrowserTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any
import os
import json
import time
from datetime import datetime

@CrewBase
class LinkedinCrew():
    """LinkedIn Reactions Extractor Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        super().__init__()
        # Initialize custom LinkedIn browser tool
        self.linkedin_tool = LinkedInBrowserTool()
        self.reactor_data = []
        
    @before_kickoff
    def prepare_extraction(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize browser session with optional context"""
        print("🚀 LinkedIn Reactions Extractor (CrewAI + StagehandTool)")
        print("=" * 60)
        print("🌐 Initializing browser session...")
        
        # Get optional context ID for pre-authenticated session
        self.context_id = inputs.get("context_id", os.getenv("BROWSERBASE_CONTEXT_ID"))
        if self.context_id:
            print(f"📱 Using pre-authenticated context: {self.context_id}")
        
        return inputs
    
    @after_kickoff
    def save_results(self, output):
        """Save extraction results and cleanup"""
        print("\n🧹 Cleaning up browser session...")
        self.linkedin_tool.close()
        
        # Generate timestamp for file names
        timestamp = str(int(time.time()))
        
        # Save JSON data
        if self.reactor_data:
            json_filename = f"reactions_data_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.reactor_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Data saved to: {json_filename}")
        
        print("\n🏁 Extraction complete!")
        return output

    @agent
    def navigator(self) -> Agent:
        return Agent(
            config=self.agents_config['navigator'],
            tools=[self.linkedin_tool],
            verbose=True
        )

    @agent
    def extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['extractor'],
            tools=[self.linkedin_tool],
            verbose=True
        )

    @agent
    def reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['reporter'],
            verbose=True
        )

    @task
    def navigate_to_post_task(self) -> Task:
        return Task(
            config=self.tasks_config['navigate_to_post_task']
        )

    @task
    def open_reactions_task(self) -> Task:
        return Task(
            config=self.tasks_config['open_reactions_task']
        )

    @task
    def extract_reactions_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_reactions_task'],
            callback=self._store_reactor_data
        )

    @task
    def generate_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_report_task'],
            output_file=f'reactions_summary_{int(time.time())}.md'
        )
    
    def _store_reactor_data(self, task_output):
        """Callback to store extracted reactor data"""
        try:
            # Parse the extraction output
            if isinstance(task_output.raw, str):
                # Try to parse JSON from the output
                import re
                json_match = re.search(r'\{.*"reactors".*\}', task_output.raw, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    self.reactor_data = data.get("reactors", [])
        except Exception as e:
            print(f"⚠️ Error storing reactor data: {e}")

    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn Reactions Extractor crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,  # Enable memory for context sharing
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        )
