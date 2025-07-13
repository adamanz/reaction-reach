#!/usr/bin/env python3
"""
Test Apollo MCP Integration with ReactionReach
Demonstrates how Apollo.io email enrichment works with extracted LinkedIn data
"""

import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_apollo_integration():
    """Test Apollo MCP integration with real LinkedIn reaction data"""
    
    print("🧪 Testing Apollo MCP Integration with ReactionReach")
    print("=" * 60)
    
    # Load the most recent reactions data
    reaction_files = [f for f in os.listdir('.') if f.startswith('reactions_data_') and f.endswith('.json')]
    if not reaction_files:
        print("❌ No reaction data files found. Run smart_linkedin_extractor.py first.")
        return
    
    latest_file = max(reaction_files)
    print(f"📁 Using reaction data: {latest_file}")
    
    with open(latest_file, 'r') as f:
        reactions_data = json.load(f)
    
    print(f"👥 Found {len(reactions_data)} reactor profiles")
    
    # Test data preparation for Apollo enrichment
    print("\n🔍 Preparing data for Apollo enrichment...")
    
    apollo_candidates = []
    for reactor in reactions_data:
        if reactor.get('name') and reactor['name'] != 'Unknown':
            # Extract company from element_text if available
            company = extract_company_from_text(reactor.get('element_text', ''))
            
            apollo_candidate = {
                'name': reactor['name'],
                'company': company if company else reactor.get('company', 'N/A'),
                'linkedin_url': reactor.get('profile_url'),
                'connection_degree': reactor.get('connection_degree')
            }
            apollo_candidates.append(apollo_candidate)
    
    print(f"✅ Prepared {len(apollo_candidates)} candidates for Apollo enrichment")
    
    # Show what Apollo MCP commands would be used
    print("\n🚀 Apollo MCP Commands that would be executed:")
    print("-" * 50)
    
    for i, candidate in enumerate(apollo_candidates[:3], 1):  # Show first 3 examples
        print(f"\n{i}. {candidate['name']}")
        print(f"   Company: {candidate['company']}")
        
        # Show the MCP command that would be used
        mcp_command = f"""
mcp__apollo__people_enrichment(
    name="{candidate['name']}",
    organization_name="{candidate['company']}" if candidate['company'] != 'N/A' else None,
    linkedin_url="{candidate['linkedin_url']}",
    reveal_personal_emails=True
)"""
        print(f"   MCP Command: {mcp_command}")
    
    if len(apollo_candidates) > 3:
        print(f"\n   ... and {len(apollo_candidates) - 3} more profiles")
    
    # Show expected output structure
    print("\n📊 Expected Apollo Enrichment Output:")
    print("-" * 40)
    
    expected_output = {
        "success": True,
        "total_profiles": len(apollo_candidates),
        "emails_found": "15-25 (typical 30-50% success rate)",
        "enriched_profiles": [
            {
                "name": "Example Reactor",
                "email": "example@company.com",
                "email_status": "verified",
                "title": "Senior Engineer",
                "company": "Tech Company",
                "city": "San Francisco",
                "state": "CA",
                "linkedin_url": "https://linkedin.com/in/...",
                "apollo_id": "12345",
                "phone_numbers": ["available if requested"],
                "employment_history": ["last 3 positions"]
            }
        ]
    }
    
    print(json.dumps(expected_output, indent=2))
    
    # Show CrewAI integration approach
    print("\n🤖 CrewAI + Apollo MCP Integration:")
    print("-" * 40)
    
    crewai_integration = """
# In crew.py - MCP Server Configuration:
mcp_server_params = [
    {
        "command": "node",
        "args": ["/Users/adamanzuoni/apollo-io-mcp-server/dist/index.js"],
        "env": {
            "APOLLO_IO_API_KEY": "your_apollo_key"
        }
    }
]

# Agent with Apollo tools:
@agent
def post_analyzer(self) -> Agent:
    return Agent(
        config=self.agents_config['post_analyzer'],
        tools=self.get_mcp_tools("people_enrichment", "organization_enrichment")
    )

# Task description:
analyze_task:
  description: >
    Extract LinkedIn reactions data, then use Apollo MCP tools to enrich 
    each profile with email addresses using people_enrichment function.
"""
    
    print(crewai_integration)
    
    print("\n✅ Integration Test Complete!")
    print("\n📝 Next Steps:")
    print("1. Ensure Apollo MCP server is running")
    print("2. Update .env with APOLLO_API_KEY")
    print("3. Run CrewAI with MCP integration enabled")
    print("4. Profiles will be automatically enriched with emails")


def extract_company_from_text(element_text):
    """Extract company name from LinkedIn element text"""
    if not element_text:
        return None
    
    lines = element_text.split('\n')
    for line in lines:
        line = line.strip()
        # Look for common company indicators
        if any(indicator in line.lower() for indicator in ['at ', '@ ', 'ceo', 'founder', 'director']):
            # Extract company after 'at' or '@'
            if ' at ' in line:
                company = line.split(' at ')[-1].strip()
                if company and len(company) > 2:
                    return company
            elif ' @ ' in line:
                company = line.split(' @ ')[-1].strip()  
                if company and len(company) > 2:
                    return company
    
    return None


if __name__ == "__main__":
    test_apollo_integration()