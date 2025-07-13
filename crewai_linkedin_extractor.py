#!/usr/bin/env python3
"""
LinkedIn Reactions Extractor - CrewAI Version
Uses CrewAI framework with Stagehand/Browserbase for intelligent LinkedIn navigation
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from crewai import Agent, Task, Crew
from crewai_tools import StagehandTool
from stagehand.schemas import AvailableModel

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
    
    def create_agents(self, stagehand_tool: StagehandTool) -> tuple:
        """Create specialized agents for LinkedIn automation"""
        
        # Navigation Agent - Expert at finding posts
        navigator = Agent(
            role='LinkedIn Navigator',
            goal='Navigate LinkedIn to find the most recent post and open reactions',
            backstory="""You are an expert at navigating LinkedIn's interface. 
            You understand LinkedIn's DOM structure and can intelligently find posts, 
            notifications, and reaction elements. You use AI-powered navigation to 
            handle dynamic content and changing layouts.""",
            tools=[stagehand_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=3
        )
        
        # Data Extractor Agent - Expert at extracting profile data
        extractor = Agent(
            role='Profile Data Extractor',
            goal='Extract detailed profile information from LinkedIn reaction lists',
            backstory="""You are a data extraction specialist who can parse LinkedIn 
            profiles and extract structured information including names, titles, 
            companies, connection degrees, and profile URLs. You handle edge cases 
            and missing data gracefully.""",
            tools=[stagehand_tool],
            verbose=True,
            allow_delegation=False,
            max_iter=2
        )
        
        # Report Generator Agent - Creates formatted output
        reporter = Agent(
            role='Data Report Generator',
            goal='Generate well-formatted JSON and Markdown reports from extracted data',
            backstory="""You are a data visualization expert who creates clear, 
            structured reports. You generate both machine-readable JSON and 
            human-friendly Markdown summaries with statistics and insights.""",
            verbose=True,
            allow_delegation=False
        )
        
        return navigator, extractor, reporter
    
    def create_tasks(self, navigator: Agent, extractor: Agent, reporter: Agent) -> List[Task]:
        """Create tasks for the LinkedIn extraction workflow"""
        
        # Task 1: Navigate to recent post
        navigate_task = Task(
            description="""
            1. Navigate to LinkedIn notifications page (filter=my_posts_all)
            2. Use the Act command to find and click on the most recent post notification
            3. Once on the post page, use the Act command to click on the reactions area 
               (look for "and X others" or reaction counts)
            4. Wait for the reactions modal to fully load
            5. Take a screenshot of the reactions modal for verification
            
            Important: Use natural language instructions with the Act command, like:
            - "Click on the first post notification"
            - "Click on the reactions count that says 'and X others'"
            """,
            expected_output="Successfully navigated to reactions modal with screenshot confirmation",
            agent=navigator
        )
        
        # Task 2: Extract reactor data
        extract_task = Task(
            description="""
            1. Use the Extract command to get all reactor profiles from the modal
            2. For each reactor, extract:
               - Full name
               - Job title/headline
               - Company name
               - Connection degree (1st, 2nd, 3rd)
               - Profile URL
            3. Use this extraction schema:
               {
                 "reactors": [{
                   "name": "string",
                   "title": "string",
                   "company": "string",
                   "connection_degree": "string",
                   "profile_url": "string"
                 }]
               }
            4. Handle missing fields gracefully (use "N/A" for missing data)
            5. Ensure all profile URLs are complete LinkedIn URLs
            """,
            expected_output="JSON array of reactor profiles with all available data",
            agent=extractor,
            context=[navigate_task]
        )
        
        # Task 3: Generate reports
        report_task = Task(
            description="""
            Using the extracted reactor data:
            1. Create a timestamped JSON file with all reactor profiles
            2. Generate a Markdown summary report including:
               - Total reactor count
               - List of all reactors with their details
               - Summary statistics:
                 - Top companies (with counts)
                 - Connection degree distribution
               - Extraction timestamp
            3. Format the Markdown with clear headers and bullet points
            4. Save both files with timestamp in filename
            """,
            expected_output="Generated JSON data file and Markdown summary report",
            agent=reporter,
            context=[extract_task]
        )
        
        return [navigate_task, extract_task, report_task]
    
    def save_results(self, data: Dict[str, Any]) -> tuple:
        """Save extraction results to files"""
        timestamp = str(int(time.time()))
        
        # Parse the crew output to extract reactor data
        try:
            # The crew output contains the extracted data
            if isinstance(data, str):
                # Try to parse JSON from the output
                import re
                json_match = re.search(r'\{.*"reactors".*\}', data, re.DOTALL)
                if json_match:
                    reactor_data = json.loads(json_match.group())
                else:
                    reactor_data = {"reactors": []}
            else:
                reactor_data = data
            
            # Save JSON data
            json_filename = f"reactions_data_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(reactor_data.get("reactors", []), f, indent=2, ensure_ascii=False)
            
            # Generate and save Markdown summary
            md_filename = f"reactions_summary_{timestamp}.md"
            self._generate_markdown_summary(reactor_data.get("reactors", []), md_filename)
            
            return json_filename, md_filename
            
        except Exception as e:
            print(f"Error saving results: {e}")
            return None, None
    
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
    
    def run(self):
        """Execute the CrewAI LinkedIn extraction workflow"""
        print("🚀 LinkedIn Reactions Extractor (CrewAI + Browserbase)")
        print("=" * 60)
        
        # Use context manager for proper resource cleanup
        with StagehandTool(
            api_key=self.browserbase_api_key,
            project_id=self.browserbase_project_id,
            model_api_key=self.openai_api_key,
            model_name=AvailableModel.GPT_4O,
            context_id=self.context_id  # Use existing LinkedIn session if available
        ) as stagehand_tool:
            
            # Create agents
            print("🤖 Creating specialized agents...")
            navigator, extractor, reporter = self.create_agents(stagehand_tool)
            
            # Create tasks
            print("📋 Defining extraction tasks...")
            tasks = self.create_tasks(navigator, extractor, reporter)
            
            # Assemble crew
            print("👥 Assembling the crew...")
            crew = Crew(
                agents=[navigator, extractor, reporter],
                tasks=tasks,
                verbose=True,
                planning=True,  # Enable planning for better coordination
                memory=True     # Enable memory for context sharing
            )
            
            # Execute the extraction
            print("🔄 Starting extraction process...")
            try:
                result = crew.kickoff()
                
                # Save results
                json_file, md_file = self.save_results(result)
                
                if json_file and md_file:
                    print(f"\n✅ Successfully extracted reactor profiles!")
                    print(f"💾 Data saved to: {json_file}")
                    print(f"📄 Summary report created: {md_file}")
                else:
                    print("\n⚠️ Extraction completed but failed to save results")
                
                print("\n🏁 RESULT: SUCCESS ✅")
                
            except Exception as e:
                print(f"\n❌ Error during extraction: {e}")
                print("\n🏁 RESULT: FAILED ❌")


def main():
    """Main entry point"""
    try:
        extractor = LinkedInReactionsCrewAI()
        extractor.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())