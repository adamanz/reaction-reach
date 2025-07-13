"""
LinkedIn Reaction Reach CrewAI Implementation
Orchestrates agents to extract LinkedIn reactions and enrich with emails
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Import custom tools
from .tools import LinkedInReactionsTool, ApolloEnrichmentTool

# Load environment variables
load_dotenv()


@CrewBase
class LinkedInReactionReachCrew():
    """LinkedIn Reaction Reach crew for extracting and enriching LinkedIn engagement data"""
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        """Initialize tools with API keys"""
        # Initialize LinkedIn tool
        self.linkedin_tool = LinkedInReactionsTool(
            browserbase_api_key=os.getenv("BROWSERBASE_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            project_id=os.getenv("BROWSERBASE_PROJECT_ID")
        )
        
        # Initialize Apollo tool
        self.apollo_tool = ApolloEnrichmentTool(
            apollo_api_key=os.getenv("APOLLO_API_KEY")
        )
    
    @before_kickoff
    def before_kickoff_function(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and validate inputs before crew execution"""
        print("🚀 LinkedIn Reaction Reach Crew starting...")
        print(f"📊 Configuration: {inputs}")
        
        # Set default context_id if not provided
        if 'context_id' not in inputs:
            inputs['context_id'] = "929c2463-a010-4425-b900-4fde8a7ca327"
            print(f"ℹ️ Using default Browserbase context ID: {inputs['context_id']}")
        
        return inputs
    
    @after_kickoff
    def after_kickoff_function(self, result: Any) -> Any:
        """Process results after crew execution"""
        print("✅ LinkedIn Reaction Reach Crew completed!")
        print(f"📄 Results saved to: output/linkedin_reactions_report.md")
        
        # You could add additional processing here like:
        # - Sending email notifications
        # - Uploading to CRM
        # - Creating follow-up tasks
        
        return result
    
    @agent
    def linkedin_extractor(self) -> Agent:
        """Agent for extracting LinkedIn reactions"""
        return Agent(
            config=self.agents_config['linkedin_extractor'],
            tools=[self.linkedin_tool],
            verbose=True,
            memory=True
        )
    
    @agent
    def apollo_enricher(self) -> Agent:
        """Agent for enriching profiles with Apollo.io"""
        return Agent(
            config=self.agents_config['apollo_enricher'],
            tools=[self.apollo_tool],
            verbose=True,
            memory=True
        )
    
    @agent
    def outreach_strategist(self) -> Agent:
        """Agent for analyzing data and creating outreach strategies"""
        return Agent(
            config=self.agents_config['outreach_strategist'],
            verbose=True,
            memory=True
        )
    
    @agent
    def report_generator(self) -> Agent:
        """Agent for generating comprehensive reports"""
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True,
            memory=True
        )
    
    @task
    def extract_reactions_task(self) -> Task:
        """Task to extract LinkedIn reactions"""
        return Task(
            config=self.tasks_config['extract_reactions_task'],
            tools=[self.linkedin_tool]
        )
    
    @task
    def enrich_emails_task(self) -> Task:
        """Task to enrich profiles with emails"""
        return Task(
            config=self.tasks_config['enrich_emails_task'],
            tools=[self.apollo_tool]
        )
    
    @task
    def analyze_outreach_task(self) -> Task:
        """Task to analyze data and create outreach strategies"""
        return Task(
            config=self.tasks_config['analyze_outreach_task']
        )
    
    @task
    def generate_report_task(self) -> Task:
        """Task to generate final report"""
        return Task(
            config=self.tasks_config['generate_report_task'],
            output_file='output/linkedin_reactions_report.md'
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the LinkedIn Reaction Reach crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,    # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        )