"""
Apollo.io Email Enrichment Tool for CrewAI
Enriches LinkedIn profiles with email addresses using Apollo.io API
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import requests
import json


class ApolloEnrichmentToolSchema(BaseModel):
    """Input schema for Apollo Enrichment Tool"""
    profiles: List[Dict[str, Any]] = Field(
        description="List of profile dictionaries containing name and optional company info"
    )
    reveal_personal_emails: Optional[bool] = Field(
        default=False,
        description="Whether to reveal personal email addresses (consumes credits)"
    )


class ApolloEnrichmentTool(BaseTool):
    name: str = "Apollo Email Enricher"
    description: str = "Enriches LinkedIn profiles with email addresses using Apollo.io API"
    args_schema: type[BaseModel] = ApolloEnrichmentToolSchema
    
    def __init__(self, apollo_api_key: str):
        super().__init__()
        self.api_key = apollo_api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }
    
    def _run(self, profiles: List[Dict[str, Any]], reveal_personal_emails: bool = False) -> str:
        """Enrich profiles with email addresses from Apollo"""
        
        print(f"🚀 Starting Apollo enrichment for {len(profiles)} profiles...")
        
        enriched_profiles = []
        
        for i, profile in enumerate(profiles):
            print(f"\n📧 Processing {i+1}/{len(profiles)}: {profile.get('name', 'Unknown')}")
            
            # Prepare enrichment data
            enrichment_data = {
                "name": profile.get("name", ""),
                "reveal_personal_emails": reveal_personal_emails
            }
            
            # Add company/organization if available
            if profile.get("company") and profile["company"] not in ["N/A", "Unknown", ""]:
                enrichment_data["organization_name"] = profile["company"]
            
            # Parse first and last name if possible
            name_parts = profile.get("name", "").split()
            if len(name_parts) >= 2:
                enrichment_data["first_name"] = name_parts[0]
                enrichment_data["last_name"] = " ".join(name_parts[1:])
            
            # Call Apollo API
            try:
                response = requests.post(
                    f"{self.base_url}/people/match",
                    headers=self.headers,
                    json=enrichment_data
                )
                
                if response.status_code == 200:
                    apollo_data = response.json()
                    person = apollo_data.get("person", {})
                    
                    enriched_profile = {
                        "name": profile.get("name"),
                        "original_data": profile,
                        "apollo_id": person.get("id"),
                        "email": person.get("email"),
                        "email_status": person.get("email_status"),
                        "title": person.get("title") or profile.get("title"),
                        "company": person.get("organization", {}).get("name") or profile.get("company"),
                        "linkedin_url": person.get("linkedin_url") or profile.get("profile_url"),
                        "city": person.get("city"),
                        "state": person.get("state"),
                        "country": person.get("country"),
                        "departments": person.get("departments", []),
                        "seniority": person.get("seniority"),
                        "phone_numbers": person.get("phone_numbers", []),
                        "employment_history": person.get("employment_history", [])[:3]  # Last 3 jobs
                    }
                    
                    if enriched_profile["email"]:
                        print(f"✅ Found email: {enriched_profile['email']}")
                    else:
                        print(f"❌ No email found")
                    
                    enriched_profiles.append(enriched_profile)
                    
                else:
                    print(f"❌ Apollo API error: {response.status_code}")
                    enriched_profiles.append({
                        "name": profile.get("name"),
                        "original_data": profile,
                        "error": f"API error: {response.status_code}",
                        "email": None
                    })
                    
            except Exception as e:
                print(f"❌ Error enriching profile: {e}")
                enriched_profiles.append({
                    "name": profile.get("name"),
                    "original_data": profile,
                    "error": str(e),
                    "email": None
                })
        
        # Summary statistics
        emails_found = sum(1 for p in enriched_profiles if p.get("email"))
        
        result = {
            "success": True,
            "total_profiles": len(profiles),
            "emails_found": emails_found,
            "enriched_profiles": enriched_profiles,
            "summary": {
                "emails_found": emails_found,
                "emails_not_found": len(profiles) - emails_found,
                "success_rate": f"{(emails_found / len(profiles) * 100):.1f}%" if profiles else "0%"
            }
        }
        
        print(f"\n📊 Enrichment complete: {emails_found}/{len(profiles)} emails found")
        
        return json.dumps(result, indent=2)