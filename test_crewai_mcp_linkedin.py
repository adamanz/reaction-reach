#!/usr/bin/env python3
"""
CrewAI + MCP Tools LinkedIn Extraction Test
Uses Stagehand MCP server for LinkedIn automation
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from mcp import StdioServerParameters

# Load environment
load_dotenv()

def test_mcp_tools_available():
    """Test that we can load MCP tools"""
    print("🔧 Testing MCP Tools Availability...")
    
    try:
        from crewai_tools import MCPServerAdapter
        print("   ✅ MCPServerAdapter imported successfully")
        
        # Stagehand MCP server configuration
        stagehand_params = StdioServerParameters(
            command="node",
            args=["./node_modules/@browserbasehq/mcp-stagehand/dist/index.js"],
            env={
                "BROWSERBASE_API_KEY": os.getenv("BROWSERBASE_API_KEY"),
                "BROWSERBASE_PROJECT_ID": os.getenv("BROWSERBASE_PROJECT_ID"),
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "CONTEXT_ID": os.getenv("LINKEDIN_CONTEXT_ID", "b03b0494-a12d-4e4c-b99f-59651591529e"),
                **os.environ
            }
        )
        
        print("   🌐 Testing Stagehand MCP server connection...")
        
        # Test connection with context manager
        with MCPServerAdapter(stagehand_params) as mcp_tools:
            available_tools = [tool.name for tool in mcp_tools]
            print(f"   ✅ Available tools: {available_tools}")
            
            # Look for specific Stagehand tools
            expected_tools = ["stagehand_navigate", "stagehand_act", "stagehand_extract", "stagehand_observe"]
            found_tools = [tool for tool in expected_tools if tool in available_tools]
            
            print(f"   ✅ Stagehand tools found: {found_tools}")
            
            return len(found_tools) > 0
            
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        print("   💡 Try: pip install 'crewai-tools[mcp]'")
        return False
    except Exception as e:
        print(f"   ❌ MCP connection failed: {e}")
        return False

def create_linkedin_extraction_crew():
    """Create a CrewAI crew with MCP tools for LinkedIn extraction"""
    print("\n🤖 Creating LinkedIn Extraction Crew...")
    
    try:
        from crewai import Agent, Crew, Task
        from crewai_tools import MCPServerAdapter
        
        # Stagehand MCP server configuration
        stagehand_params = StdioServerParameters(
            command="node",
            args=["./node_modules/@browserbasehq/mcp-stagehand/dist/index.js"],
            env={
                "BROWSERBASE_API_KEY": os.getenv("BROWSERBASE_API_KEY"),
                "BROWSERBASE_PROJECT_ID": os.getenv("BROWSERBASE_PROJECT_ID"), 
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "CONTEXT_ID": os.getenv("LINKEDIN_CONTEXT_ID", "b03b0494-a12d-4e4c-b99f-59651591529e"),
                **os.environ
            }
        )
        
        with MCPServerAdapter(stagehand_params) as stagehand_tools:
            print(f"   ✅ Loaded MCP tools: {[tool.name for tool in stagehand_tools]}")
            
            # LinkedIn Navigator Agent - uses Stagehand for automation
            navigator = Agent(
                role="LinkedIn Navigator",
                goal="Navigate to LinkedIn profile and access recent activity feed",
                backstory="""You are an expert at LinkedIn navigation using Stagehand automation.
                You can authenticate, navigate profiles, and access activity feeds while avoiding detection.""",
                tools=stagehand_tools,
                verbose=True
            )
            
            # Post Extractor Agent - uses Stagehand for data extraction
            extractor = Agent(
                role="Post Data Extractor", 
                goal="Extract structured data from LinkedIn posts using browser automation",
                backstory="""You are a data extraction specialist who can identify and extract
                post content, engagement metrics, and metadata from LinkedIn activity feeds.""",
                tools=stagehand_tools,
                verbose=True
            )
            
            # Navigation Task
            navigate_task = Task(
                description="""
                Navigate to the LinkedIn profile: https://linkedin.com/in/adamanz
                Then navigate to the recent activity page: https://linkedin.com/in/adamanz/recent-activity/all/
                Ensure the page loads completely and is ready for data extraction.
                Take note of any authentication required or errors encountered.
                """,
                agent=navigator,
                expected_output="Confirmation that LinkedIn activity page is loaded and accessible"
            )
            
            # Extraction Task  
            extract_task = Task(
                description="""
                Extract the last 10 LinkedIn posts from the activity feed.
                For each post, extract:
                1. Post content/text
                2. Timestamp/date
                3. Number of reactions
                4. Number of comments  
                5. Post type (text, image, video, etc.)
                6. Post URL if available
                
                Focus on recent posts and ensure data quality.
                """,
                agent=extractor,
                expected_output="JSON list of 10 LinkedIn posts with complete metadata",
                context=[navigate_task]
            )
            
            # Create and configure the crew
            crew = Crew(
                agents=[navigator, extractor],
                tasks=[navigate_task, extract_task],
                verbose=True,
                memory=True
            )
            
            print("   ✅ CrewAI crew created successfully")
            return crew
            
    except Exception as e:
        print(f"   ❌ Failed to create crew: {e}")
        return None

def run_linkedin_extraction():
    """Run the complete LinkedIn extraction process"""
    print("\n🚀 Running LinkedIn Extraction with CrewAI + MCP...")
    
    try:
        crew = create_linkedin_extraction_crew()
        if not crew:
            print("   ❌ Failed to create crew")
            return None
        
        print("   🎯 Target: https://linkedin.com/in/adamanz")
        print("   📊 Extracting last 10 posts...")
        
        # Execute the crew
        result = crew.kickoff()
        
        print("   ✅ Extraction completed!")
        
        # Save results
        output_file = Path("data") / f"mcp_linkedin_extraction_{int(os.time.time() if hasattr(os, 'time') else 0)}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        # Convert result to JSON if it's not already
        if hasattr(result, '__dict__'):
            result_data = result.__dict__
        else:
            result_data = {"result": str(result)}
        
        with open(output_file, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)
        
        print(f"   💾 Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test execution"""
    print("🎯 CrewAI + MCP LinkedIn Post Extraction Test")
    print("=" * 60)
    print("Testing integration of Stagehand MCP tools with CrewAI")
    print("Target: Extract last 10 posts from linkedin.com/in/adamanz")
    print()
    
    # Validate environment
    required_vars = ["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables validated")
    
    # Test MCP tools availability
    if not test_mcp_tools_available():
        print("\n❌ MCP tools test failed")
        return False
    
    # Run extraction
    result = run_linkedin_extraction()
    
    if result:
        print("\n🎉 Test completed successfully!")
        print("\nResults Summary:")
        print(f"   📊 Extraction result: {str(result)[:200]}...")
        print("\nNext Steps:")
        print("1. Review the saved results file")
        print("2. Analyze extracted post data")
        print("3. Implement reaction harvesting for each post")
        return True
    else:
        print("\n❌ Test failed")
        print("\nTroubleshooting:")
        print("1. Check Stagehand MCP server is installed: npm install @browserbasehq/mcp-stagehand")
        print("2. Verify Browserbase API keys are valid")
        print("3. Ensure LinkedIn profile is publicly accessible")
        return False

if __name__ == "__main__":
    import sys
    
    # Install dependencies if needed
    try:
        import crewai
        from crewai_tools import MCPServerAdapter
    except ImportError:
        print("Installing required dependencies...")
        os.system("pip install 'crewai-tools[mcp]' crewai")
        print("Please run the script again after installation completes")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)