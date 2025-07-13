#!/usr/bin/env python3
"""
LinkedIn Reactions Extractor - CrewAI Version (Simplified)
Uses CrewAI framework without crewai-tools, directly integrating with Stagehand
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from crewai import Agent, Task, Crew
from stagehand import Stagehand

# Load environment variables
load_dotenv()

class LinkedInReactionsCrewAI:
    """CrewAI-based LinkedIn reactions extractor"""
    
    def __init__(self):
        self.browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
        self.browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.context_id = os.getenv("BROWSERBASE_CONTEXT_ID")
        
        if not all([self.browserbase_api_key, self.browserbase_project_id, self.openai_api_key]):
            raise ValueError("Missing required environment variables. Check your .env file.")
        
        # Initialize Stagehand
        self.stagehand = Stagehand(
            api_key=self.browserbase_api_key,
            project_id=self.browserbase_project_id,
            model_api_key=self.openai_api_key,
            model_name="gpt-4o"
        )
    
    async def navigate_to_reactions(self):
        """Navigate to LinkedIn and find reactions"""
        # Navigate to LinkedIn notifications
        await self.stagehand.page.goto("https://www.linkedin.com/notifications/?filter=my_posts_all")
        await self.stagehand.page.wait_for_load_state("networkidle")
        
        # Find and click on the most recent post
        await self.stagehand.act(action="Click on the first post notification")
        await self.stagehand.page.wait_for_load_state("networkidle")
        
        # Click on reactions
        await self.stagehand.act(action="Click on the reactions count that shows 'and others' or similar")
        await self.stagehand.page.wait_for_selector(".artdeco-modal", timeout=5000)
        
        return True
    
    async def extract_reactor_data(self):
        """Extract reactor profiles using Stagehand"""
        schema = {
            "type": "object",
            "properties": {
                "reactors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "title": {"type": "string"},
                            "company": {"type": "string"},
                            "connection_degree": {"type": "string"},
                            "profile_url": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        result = await self.stagehand.extract(
            instruction="Extract all reactor profiles from the reactions modal, including their names, titles, companies, connection degrees, and profile URLs",
            schema=schema
        )
        
        return result.get("reactors", [])
    
    def create_agents(self) -> tuple:
        """Create specialized agents for LinkedIn automation"""
        
        # Navigation Agent
        navigator = Agent(
            role='LinkedIn Navigator',
            goal='Navigate LinkedIn to find the most recent post and open reactions modal',
            backstory="""You are an expert at navigating LinkedIn's interface. 
            You understand how to find posts in notifications and open reaction modals.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Data Processor Agent
        processor = Agent(
            role='Data Processor',
            goal='Process and format extracted LinkedIn reaction data',
            backstory="""You are a data processing specialist who formats raw data 
            into structured JSON and creates readable summaries.""",
            verbose=True,
            allow_delegation=False
        )
        
        return navigator, processor
    
    def create_tasks(self, navigator: Agent, processor: Agent, reactor_data: List[Dict]) -> List[Task]:
        """Create tasks for the workflow"""
        
        # Task 1: Verify navigation success
        verify_task = Task(
            description="""
            Verify that we successfully navigated to the reactions modal.
            Confirm that reactor data was extracted.
            Report the number of reactors found.
            """,
            expected_output="Confirmation of successful extraction with reactor count",
            agent=navigator
        )
        
        # Task 2: Process and format data
        process_task = Task(
            description=f"""
            Process the following reactor data and create:
            1. A formatted JSON structure with all reactor details
            2. A summary report with:
               - Total reactor count
               - Company distribution
               - Connection degree breakdown
               
            Reactor data: {json.dumps(reactor_data)}
            """,
            expected_output="Processed data ready for file output",
            agent=processor,
            context=[verify_task]
        )
        
        return [verify_task, process_task]
    
    def save_results(self, reactor_data: List[Dict]) -> tuple:
        """Save extraction results to files"""
        timestamp = str(int(time.time()))
        
        # Save JSON data
        json_filename = f"reactions_data_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(reactor_data, f, indent=2, ensure_ascii=False)
        
        # Generate and save Markdown summary
        md_filename = f"reactions_summary_{timestamp}.md"
        self._generate_markdown_summary(reactor_data, md_filename)
        
        return json_filename, md_filename
    
    def _generate_markdown_summary(self, reactors: List[Dict], filename: str):
        """Generate a Markdown summary report"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# LinkedIn Post Reactions Analysis\n\n")
            f.write(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Reactors:** {len(reactors)}\n\n")
            
            f.write("## 📊 Reactor Profiles\n\n")
            for i, reactor in enumerate(reactors, 1):
                f.write(f"### {i}. {reactor.get('name', 'Unknown')}\n")
                f.write(f"- **Title:** {reactor.get('title', 'N/A')}\n")
                f.write(f"- **Company:** {reactor.get('company', 'N/A')}\n")
                f.write(f"- **Connection:** {reactor.get('connection_degree', 'N/A')}\n")
                f.write(f"- **Profile:** {reactor.get('profile_url', 'N/A')}\n\n")
            
            # Generate statistics
            f.write("## 📈 Summary Statistics\n\n")
            
            # Company distribution
            companies = {}
            for reactor in reactors:
                company = reactor.get('company', 'N/A')
                if company and company != 'N/A':
                    companies[company] = companies.get(company, 0) + 1
            
            if companies:
                f.write("### Top Companies\n")
                for company, count in sorted(companies.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- {company}: {count}\n")
                f.write("\n")
            
            # Connection degree distribution
            connections = {}
            for reactor in reactors:
                degree = reactor.get('connection_degree', 'N/A')
                if degree and degree != 'N/A':
                    connections[degree] = connections.get(degree, 0) + 1
            
            if connections:
                f.write("### Connection Degrees\n")
                for degree in ['1st', '2nd', '3rd', '3rd+']:
                    if degree in connections:
                        f.write(f"- {degree}: {connections[degree]}\n")
    
    async def run(self):
        """Execute the CrewAI LinkedIn extraction workflow"""
        print("🚀 LinkedIn Reactions Extractor (CrewAI + Stagehand)")
        print("=" * 60)
        
        try:
            # Start Stagehand session
            print("🌐 Starting browser session...")
            await self.stagehand.start(context_id=self.context_id)
            
            # Navigate and extract
            print("📍 Navigating to LinkedIn...")
            await self.navigate_to_reactions()
            
            print("📊 Extracting reactor data...")
            reactor_data = await self.extract_reactor_data()
            
            if not reactor_data:
                print("⚠️ No reactor data found!")
                return
            
            print(f"✅ Found {len(reactor_data)} reactors")
            
            # Create agents and tasks
            print("🤖 Creating CrewAI agents...")
            navigator, processor = self.create_agents()
            
            print("📋 Defining processing tasks...")
            tasks = self.create_tasks(navigator, processor, reactor_data)
            
            # Assemble crew
            print("👥 Assembling the crew...")
            crew = Crew(
                agents=[navigator, processor],
                tasks=tasks,
                verbose=True
            )
            
            # Execute the crew tasks
            print("🔄 Processing data with CrewAI...")
            crew.kickoff()
            
            # Save results
            json_file, md_file = self.save_results(reactor_data)
            
            print(f"\n✅ Successfully extracted reactor profiles!")
            print(f"💾 Data saved to: {json_file}")
            print(f"📄 Summary report created: {md_file}")
            print("\n🏁 RESULT: SUCCESS ✅")
            
        except Exception as e:
            print(f"\n❌ Error during extraction: {e}")
            print("\n🏁 RESULT: FAILED ❌")
        finally:
            # Clean up
            await self.stagehand.stop()


async def main():
    """Main entry point"""
    try:
        extractor = LinkedInReactionsCrewAI()
        await extractor.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main()))