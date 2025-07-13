# src/reaction_reach_v2/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import MCPServerAdapter
from typing import List
import os


@CrewBase
class ReactionReachV2Crew():
    """ReactionReach V2 crew for LinkedIn intelligence gathering"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    # MCP Server configurations matching yolo command setup
    mcp_server_params = [
        # Apollo MCP Server for email enrichment
        {
            "command": "node",
            "args": ["/Users/adamanzuoni/apollo-io-mcp-server/dist/index.js"],
            "env": {
                "APOLLO_IO_API_KEY": os.getenv("APOLLO_API_KEY", "rsNU6yNqQOOaXkQoaur7hg")
            }
        },
        # Stagehand MCP Server for LinkedIn automation  
        {
            "command": "node",
            "args": ["/Users/adamanzuoni/ReactionReach/node_modules/@browserbasehq/mcp-stagehand/dist/index.js"],
            "env": {
                "BROWSERBASE_API_KEY": os.getenv("BROWSERBASE_API_KEY"),
                "BROWSERBASE_PROJECT_ID": os.getenv("BROWSERBASE_PROJECT_ID"),
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "CONTEXT_ID": os.getenv("CONTEXT_ID", "b03b0494-a12d-4e4c-b99f-59651591529e")
            }
        },
        # Gmail MCP Server for email drafting
        {
            "command": "npx",
            "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"]
        }
    ]

    @agent
    def linkedin_navigator(self) -> Agent:
        return Agent(
            config=self.agents_config['linkedin_navigator'],  # type: ignore[index]
            verbose=True,
            tools=self.get_mcp_tools("stagehand_navigate", "stagehand_act", "stagehand_extract")
        )

    @agent
    def post_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['post_analyzer'],  # type: ignore[index]
            verbose=True,
            tools=self.get_mcp_tools("stagehand_extract", "stagehand_observe", "people_enrichment", "organization_enrichment")
        )

    @agent
    def intelligence_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['intelligence_reporter'],  # type: ignore[index]
            verbose=True,
            tools=self.get_mcp_tools("send_email", "draft_email")
        )

    @task
    def navigate_task(self) -> Task:
        return Task(
            config=self.tasks_config['navigate_task'],  # type: ignore[index]
        )

    @task
    def analyze_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_task'],  # type: ignore[index]
        )

    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_task'],  # type: ignore[index]
            output_file='output/linkedin_intelligence_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ReactionReach V2 crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,    # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )