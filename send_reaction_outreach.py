#!/usr/bin/env python3
"""
Automated LinkedIn Reaction to Demo Booking Pipeline
Extracts reactions, enriches emails, and sends personalized outreach
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import subprocess
from typing import List, Dict, Any

load_dotenv()

# Configuration
CALENDAR_LINK = "https://cal.com/mystack"
SENDER_NAME = "Adam Anzuoni"
SENDER_TITLE = "Founder"
COMPANY_NAME = "The Simple Company"

# LinkedIn post context (update with your actual post content)
POST_CONTEXT = {
    "topic": "AI automation tools for sales teams",
    "key_points": [
        "How we built 20+ production AI agents in 2 months",
        "Real examples: 97.1% accuracy, 95% cost reduction",
        "Multi-modal AI: text, voice, video, and memory"
    ],
    "post_date": "2025-01-13",
    "engagement_metric": "500+ reactions in 24 hours"
}

def run_linkedin_extractor():
    """Run the LinkedIn reactions extractor"""
    print("🔍 Extracting LinkedIn reactions...")
    
    try:
        # Run the original extractor
        result = subprocess.run(
            ["python", "smart_linkedin_extractor.py"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Find the output file
        import glob
        reaction_files = sorted(glob.glob("reactions_data_*.json"), reverse=True)
        if reaction_files:
            return reaction_files[0]
        else:
            raise Exception("No reactions file found after extraction")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running extractor: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None

def load_reactions(reactions_file: str) -> List[Dict]:
    """Load reactions data from file"""
    with open(reactions_file, 'r') as f:
        return json.load(f)

def enrich_with_apollo(profile: Dict) -> Dict:
    """Enrich profile with email using Apollo
    Note: In production, this would use the Apollo MCP tool"""
    
    # This is a placeholder - in production you'd use the Apollo MCP tool
    # For now, using the emails we found earlier
    known_emails = {
        "Tobin South": "tobin@workos.com",
        "Sasha Manuilova": "sasha.manuilova@wandb.com", 
        "Ashish Patel": "ashish@careset.com",
        "Nicolas Ettlin": "nicolas@convex.dev",
        "Anirudh Kamath": "ani@smithery.ai"
    }
    
    enriched = profile.copy()
    enriched['email'] = known_emails.get(profile['name'])
    
    return enriched

def research_company_with_exa(company_name: str) -> Dict[str, Any]:
    """Research company using Exa to get relevant insights
    Note: In production, this would use the Exa MCP tool"""
    
    # Placeholder for Exa research
    # In production: results = mcp__exa__search(query=f"{company_name} company news funding", num_results=5)
    
    company_insights = {
        "recent_news": [],
        "funding_status": "",
        "employee_count": "",
        "industry_focus": "technology",
        "key_challenges": [],
        "tech_stack": [],
        "competitors": []
    }
    
    # Add some mock data for known companies
    if "DuploCloud" in company_name:
        company_insights["funding_status"] = "$32M Series B funding"
        company_insights["industry_focus"] = "DevOps automation"
    elif "WorkOS" in company_name:
        company_insights["industry_focus"] = "enterprise authentication"
    elif "Weights & Biases" in company_name:
        company_insights["industry_focus"] = "MLOps platform"
    
    return company_insights

def generate_personalized_email(reactor: Dict[str, Any], post_context: Dict) -> Dict[str, str]:
    """Generate personalized email content based on reactor profile and post context"""
    
    name = reactor.get('name', 'there')
    first_name = name.split()[0] if name != 'there' else 'there'
    company = reactor.get('company', 'your company')
    title = reactor.get('title', 'your role')
    connection_degree = reactor.get('connection_degree', '2nd')
    
    # Research company with Exa
    company_insights = research_company_with_exa(company)
    
    # Generate subject line based on connection degree and company insights
    if connection_degree == '1st':
        if company_insights.get('funding_status'):
            subject = f"Re: Your reaction + {company}'s {company_insights['funding_status']}"
        else:
            subject = f"Re: Your reaction to my {post_context['topic']} post, {first_name}"
    else:
        subject = f"Your interest in {post_context['topic']} caught my attention"
    
    # Build company-specific talking points
    company_specific_points = []
    
    if company_insights.get('funding_status'):
        company_specific_points.append(f"Congrats on {company_insights['funding_status']}!")
    
    if company_insights.get('industry_focus'):
        company_specific_points.append(f"Especially relevant for the {company_insights['industry_focus']} space.")
    
    # Create personalized email body
    email_body = f"""Hi {first_name},

I noticed you reacted to my LinkedIn post about {post_context['topic']} - thanks for engaging!

{company_specific_points[0] if company_specific_points else ''}

Given your role{f' as {title}' if title != 'your role' else ''} at {company}, I imagine the idea of building 20+ production AI agents in just 2 months caught your attention. {company_specific_points[1] if len(company_specific_points) > 1 else ''}

At The Simple Company, we've been helping companies achieve remarkable results with AI automation:
• 97.1% accuracy in automated workflows
• 95% cost reduction compared to manual processes
• Multi-modal AI capabilities (text, voice, video, and memory)

Our recent projects include an AI system that detected a 275% increase in invasive species hotspots for environmental monitoring, and podcast/video generation tools that are already in production use.

I'd love to show you how we could build similar AI solutions for {company} - whether it's automating customer interactions, creating content at scale, or streamlining internal processes.

Would you be open to a quick 15-minute demo this week? You can grab any time that works for you here:
{CALENDAR_LINK}

Looking forward to connecting!

Best,
{SENDER_NAME}
{SENDER_TITLE}
{COMPANY_NAME}

P.S. Check out more of our AI projects at simple.company - we're also speaking at Google Cloud Next 2025 about our approach to rapid AI development."""
    
    return {
        "subject": subject,
        "body": email_body,
        "company_insights": company_insights
    }

def send_email_via_gmail(to_email: str, subject: str, body: str) -> Dict:
    """Send email using Gmail
    Note: In production, this would use the Gmail MCP tool"""
    
    print(f"\n📧 [SIMULATION] Would send email to: {to_email}")
    print(f"   Subject: {subject}")
    print(f"   Preview: {body[:150]}...")
    
    # In production, you would use:
    # result = mcp__gmail__send_email(to=to_email, subject=subject, body=body)
    
    # For now, simulate success
    return {'success': True, 'message_id': f'msg_{int(time.time())}'}

def log_outreach(data: Dict):
    """Log outreach activity for tracking"""
    log_file = "outreach_log.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(data) + '\n')

def send_outreach_campaign(reactions_file: str = None, dry_run: bool = False):
    """Main function to run the complete outreach campaign"""
    
    print("🚀 Starting LinkedIn Outreach Campaign")
    if dry_run:
        print("🔍 DRY RUN MODE - No emails will be sent")
    print("=" * 50)
    
    # Step 1: Load reactions data (or extract fresh)
    if reactions_file:
        print(f"📂 Loading existing reactions from: {reactions_file}")
        reactions_data = load_reactions(reactions_file)
    else:
        print("🔍 Extracting fresh LinkedIn reactions...")
        reactions_file = run_linkedin_extractor()
        if not reactions_file:
            print("❌ Failed to extract reactions")
            return
        reactions_data = load_reactions(reactions_file)
    
    print(f"✅ Found {len(reactions_data)} reactions")
    
    # Step 2: Enrich with Apollo
    print("\n📧 Enriching profiles with Apollo...")
    enriched_profiles = []
    
    for profile in reactions_data:
        enriched = enrich_with_apollo(profile)
        if enriched.get('email'):
            enriched_profiles.append(enriched)
            print(f"✅ Found email for {profile['name']}: {enriched['email']}")
        else:
            print(f"❌ No email found for {profile['name']}")
    
    print(f"\n📊 Email enrichment rate: {len(enriched_profiles)}/{len(reactions_data)} ({len(enriched_profiles)/len(reactions_data)*100:.1f}%)")
    
    # Step 3: Generate and send emails
    print(f"\n📨 {'Generating' if dry_run else 'Sending'} {len(enriched_profiles)} personalized emails...")
    
    sent_count = 0
    failed_count = 0
    
    for i, profile in enumerate(enriched_profiles):
        try:
            # Generate personalized content
            email_content = generate_personalized_email(profile, POST_CONTEXT)
            
            if dry_run:
                print(f"\n{'='*60}")
                print(f"EMAIL {i+1}/{len(enriched_profiles)} - {profile['name']} ({profile['email']})")
                print(f"{'='*60}")
                print(f"Subject: {email_content['subject']}")
                print(f"\n{email_content['body']}")
                sent_count += 1
            else:
                # Send email via Gmail API
                result = send_email_via_gmail(
                    to_email=profile['email'],
                    subject=email_content['subject'],
                    body=email_content['body']
                )
                
                if result['success']:
                    sent_count += 1
                    print(f"✅ Sent to {profile['name']} ({profile['email']})")
                    
                    # Log success
                    log_outreach({
                        'timestamp': datetime.now().isoformat(),
                        'reactor': profile,
                        'email_sent': True,
                        'subject': email_content['subject']
                    })
                else:
                    failed_count += 1
                    print(f"❌ Failed to send to {profile['name']}: {result.get('error')}")
                
                # Rate limiting
                time.sleep(2)  # 2 seconds between emails
            
        except Exception as e:
            failed_count += 1
            print(f"❌ Error processing {profile['name']}: {str(e)}")
    
    # Step 4: Generate summary report
    print("\n" + "=" * 50)
    print("📊 CAMPAIGN SUMMARY")
    print(f"Total reactions: {len(reactions_data)}")
    print(f"Emails found: {len(enriched_profiles)}")
    print(f"Emails {'generated' if dry_run else 'sent'}: {sent_count}")
    print(f"Failed: {failed_count}")
    if len(enriched_profiles) > 0:
        print(f"Success rate: {sent_count/len(enriched_profiles)*100:.1f}%")
    
    # Save campaign report
    report = {
        'campaign_date': datetime.now().isoformat(),
        'post_context': POST_CONTEXT,
        'total_reactions': len(reactions_data),
        'emails_found': len(enriched_profiles),
        'emails_sent': sent_count,
        'failed': failed_count,
        'calendar_link': CALENDAR_LINK,
        'dry_run': dry_run,
        'sent_profiles': enriched_profiles[:sent_count]
    }
    
    report_file = f"outreach_campaign_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Campaign report saved: {report_file}")
    if not dry_run:
        print("🎯 Check your calendar for booked demos!")

if __name__ == "__main__":
    import sys
    
    # Check for dry run mode
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    if len(sys.argv) > 1:
        # Use existing reactions file
        send_outreach_campaign(reactions_file=sys.argv[1], dry_run=dry_run)
    else:
        # Extract fresh reactions
        send_outreach_campaign(dry_run=dry_run)