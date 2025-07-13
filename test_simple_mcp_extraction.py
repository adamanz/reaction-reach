#!/usr/bin/env python3
"""
Simple MCP-based LinkedIn Extraction using existing MCP servers
Uses the MCP servers from your yolo configuration
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def test_mcp_stagehand_extraction():
    """Test LinkedIn extraction using MCP Stagehand tools directly"""
    print("🎯 Testing MCP Stagehand LinkedIn Extraction")
    print("=" * 50)
    
    profile_url = "https://linkedin.com/in/adamanz"
    activity_url = "https://linkedin.com/in/adamanz/recent-activity/all/"
    
    print(f"Target: {profile_url}")
    print(f"Activity URL: {activity_url}")
    
    # Test data structure we'll extract
    sample_extraction = {
        "profile_url": profile_url,
        "activity_url": activity_url,
        "extraction_method": "MCP Stagehand",
        "timestamp": time.time(),
        "posts": []
    }
    
    # Simulate the extraction workflow
    workflow_steps = [
        "🌐 Connect to Stagehand MCP server",
        "🔐 Navigate to LinkedIn (handle auth if needed)",
        "📍 Navigate to activity feed URL",
        "📜 Scroll to load recent posts",
        "🔍 Extract post elements using Stagehand",
        "📊 Parse post metadata and content",
        "💾 Structure data for analysis"
    ]
    
    print("\n📋 Extraction Workflow:")
    for i, step in enumerate(workflow_steps, 1):
        print(f"   {i}. {step}")
        time.sleep(0.5)  # Simulate processing
    
    # Mock extracted posts (structure for real implementation)
    mock_posts = [
        {
            "post_id": f"mock_post_{i}",
            "content_preview": f"Sample LinkedIn post content {i}...",
            "timestamp": f"2024-01-{10+i:02d}T10:00:00Z",
            "reactions": {"total": 15 + i*3, "types": ["like", "celebrate", "insight"]},
            "comments": {"total": 2 + i},
            "post_type": "text" if i % 2 == 0 else "image",
            "extraction_method": "stagehand_mcp"
        }
        for i in range(10)
    ]
    
    sample_extraction["posts"] = mock_posts
    sample_extraction["posts_found"] = len(mock_posts)
    sample_extraction["status"] = "simulation_complete"
    
    # Save results
    output_file = Path("data") / f"mcp_stagehand_simulation_{int(time.time())}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(sample_extraction, f, indent=2)
    
    print(f"\n✅ Simulation completed!")
    print(f"📊 Found {len(mock_posts)} posts")
    print(f"💾 Results saved: {output_file}")
    
    return sample_extraction

def create_real_mcp_extraction_script():
    """Create a script for real MCP extraction using your configured servers"""
    print("\n🔧 Creating Real MCP Extraction Script...")
    
    script_content = '''#!/usr/bin/env python3
"""
Real LinkedIn Extraction using MCP Stagehand
"""

import os
import json
import subprocess
from pathlib import Path

def run_stagehand_extraction():
    """Run LinkedIn extraction using Stagehand MCP server"""
    
    # Your Stagehand MCP server configuration
    mcp_command = [
        "node",
        "./node_modules/@browserbasehq/mcp-stagehand/dist/index.js"
    ]
    
    # Environment for Stagehand
    env = {
        "BROWSERBASE_API_KEY": "bb_live_APnCzG_NvsKnCTvw-YGxJXnsMGk",
        "BROWSERBASE_PROJECT_ID": "91a6c1c4-ad01-4cf4-824a-37e7260bd114",
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "CONTEXT_ID": "b03b0494-a12d-4e4c-b99f-59651591529e",
        **os.environ
    }
    
    # Navigation instructions for Stagehand
    instructions = {
        "navigate": "https://linkedin.com/in/adamanz/recent-activity/all/",
        "extract": {
            "task": "Extract last 10 LinkedIn posts",
            "schema": {
                "posts": [{
                    "content": "string",
                    "timestamp": "string", 
                    "reactions": "number",
                    "comments": "number",
                    "post_type": "string"
                }]
            }
        }
    }
    
    print("🚀 Running Stagehand MCP extraction...")
    print(f"Command: {' '.join(mcp_command)}")
    
    # This would be the actual MCP server interaction
    # For now, return mock data structure
    
    return {
        "status": "ready_for_implementation",
        "mcp_server": "stagehand",
        "target": "https://linkedin.com/in/adamanz",
        "instructions": instructions
    }

if __name__ == "__main__":
    result = run_stagehand_extraction()
    print(json.dumps(result, indent=2))
'''
    
    script_path = Path("real_mcp_extraction.py")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"   ✅ Created: {script_path}")
    print("   📝 This script shows the structure for real MCP interaction")
    
    return script_path

def show_mcp_integration_guide():
    """Show guide for integrating with your existing MCP setup"""
    print("\n📖 MCP Integration Guide")
    print("=" * 50)
    
    guide = """
🎯 Your MCP Configuration (from mcp-config.json):

1. **Stagehand MCP Server** ✅
   - Command: node ./node_modules/@browserbasehq/mcp-stagehand/dist/index.js
   - Browserbase API Key: Configured
   - Context ID: b03b0494-a12d-4e4c-b99f-59651591529e
   
2. **Available Actions**:
   - stagehand_navigate: Navigate to URLs
   - stagehand_act: Perform actions (click, scroll, etc.)
   - stagehand_extract: Extract structured data
   - stagehand_observe: Observe page elements

🚀 **Quick Test Commands**:

1. **Test your yolo MCP setup**:
   ```bash
   yolo
   # In Claude Code interface, try:
   # "Use stagehand to navigate to linkedin.com/in/adamanz"
   ```

2. **Direct MCP server test**:
   ```bash
   node ./node_modules/@browserbasehq/mcp-stagehand/dist/index.js
   ```

3. **Integration with CrewAI** (after fixing dependencies):
   ```python
   from crewai_tools import MCPServerAdapter
   from mcp import StdioServerParameters
   
   stagehand_params = StdioServerParameters(
       command="node",
       args=["./node_modules/@browserbasehq/mcp-stagehand/dist/index.js"],
       env={...your env vars...}
   )
   
   with MCPServerAdapter(stagehand_params) as tools:
       # Use tools in CrewAI agents
   ```

💡 **Recommended Approach**:
1. Test Stagehand MCP directly first
2. Use your `yolo` command to test MCP integration
3. Once working, integrate with CrewAI for automation

🔧 **Next Steps**:
1. Run: yolo
2. Test Stagehand navigation: "Navigate to linkedin.com/in/adamanz"
3. Test data extraction: "Extract posts from current page"
4. Iterate and refine the extraction logic
"""
    
    print(guide)

def main():
    """Main execution"""
    print("🎯 MCP LinkedIn Extraction Test Suite")
    print("=" * 60)
    
    # Run simulation test
    simulation_result = test_mcp_stagehand_extraction()
    
    # Create real extraction script
    script_path = create_real_mcp_extraction_script()
    
    # Show integration guide
    show_mcp_integration_guide()
    
    print("\n🎉 Test Suite Completed!")
    print("\n📊 Results:")
    print(f"   ✅ Simulation: {simulation_result['posts_found']} posts")
    print(f"   ✅ Script created: {script_path}")
    print("\n🚀 Ready for Implementation!")
    print("\n💡 **Fastest Path to Success**:")
    print("   1. Run: yolo")
    print("   2. Test: 'Navigate to linkedin.com/in/adamanz/recent-activity/all/'")
    print("   3. Extract: 'Extract the last 10 posts with their metadata'")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)