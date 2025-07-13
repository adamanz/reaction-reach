#!/usr/bin/env python3
"""
Demo Gmail Integration for LinkedIn Reactions Extractor
Shows how email drafting would work with extracted LinkedIn contacts
"""
import json
import os
from datetime import datetime

def demo_gmail_integration():
    """Demonstrate Gmail integration with extracted LinkedIn data"""
    
    print("📧 Demo: Gmail Integration for LinkedIn Reactions")
    print("=" * 60)
    
    # Load the actual extracted LinkedIn data
    try:
        with open('reactions_data_1752379004.json', 'r') as f:
            contacts = json.load(f)
        print(f"✅ Loaded {len(contacts)} LinkedIn contacts from extraction")
    except FileNotFoundError:
        print("❌ No LinkedIn data found. Run smart_linkedin_extractor.py first.")
        return
    
    # Demo email generation for each contact
    print("\n📝 Generating personalized email drafts...\n")
    
    draft_emails = []
    
    for i, contact in enumerate(contacts, 1):
        name = contact.get('name', 'Unknown')
        first_name = name.split()[0] if name != 'Unknown' else 'there'
        company = contact.get('company', 'N/A')
        connection_degree = contact.get('connection_degree', 'N/A')
        profile_url = contact.get('profile_url', '')
        
        # Extract better job info from element_text
        element_text = contact.get('element_text', '')
        
        # Try to extract actual job title from element text
        job_title = "N/A"
        if element_text:
            lines = element_text.split('\n')
            for line in lines:
                line = line.strip()
                # Look for lines that contain job titles (usually after the name)
                if (len(line) > 10 and 
                    name not in line and 
                    'View' not in line and 
                    'profile' not in line and 
                    'connection' not in line and
                    '1st' not in line and '2nd' not in line and '3rd' not in line):
                    job_title = line
                    break
        
        # Generate personalized email
        email_draft = generate_personalized_email(name, first_name, job_title, company, connection_degree, profile_url)
        
        print(f"📧 {i}. Draft for {name}")
        print(f"   📍 Company: {company}")
        print(f"   💼 Title: {job_title}")
        print(f"   🤝 Connection: {connection_degree}")
        print(f"   📧 Subject: {email_draft['subject']}")
        print(f"   📄 Preview: {email_draft['body'][:100]}...")
        print()
        
        draft_emails.append({
            "contact": contact,
            "email_draft": email_draft,
            "extracted_title": job_title
        })
    
    # Save the demo drafts
    timestamp = int(datetime.now().timestamp())
    demo_file = f"demo_email_drafts_{timestamp}.json"
    
    with open(demo_file, 'w') as f:
        json.dump(draft_emails, f, indent=2)
    
    print(f"💾 Demo email drafts saved to: {demo_file}")
    
    # Generate summary report
    create_demo_summary_report(draft_emails, timestamp)
    
    print("\n🎯 Gmail MCP Integration Status:")
    print("✅ Email templates generated successfully")
    print("✅ Personalization logic working")
    print("⚠️  Gmail MCP authentication needed for actual drafting")
    print("\n📋 To complete setup:")
    print("1. Create OAuth credentials in Google Cloud Console")
    print("2. Replace ~/.gmail-mcp/gcp-oauth.keys.json with real credentials") 
    print("3. Run: npx @gongrzhe/server-gmail-autoauth-mcp auth")
    print("4. Re-run smart_linkedin_extractor.py for automatic drafting")

def generate_personalized_email(name, first_name, job_title, company, connection_degree, profile_url):
    """Generate personalized email content"""
    
    # Create subject line
    if connection_degree == "1st":
        subject = f"Great connecting on LinkedIn, {first_name}!"
    else:
        subject = f"Following up on your reaction to my LinkedIn post"
    
    # Create personalized opening
    opening = get_personalized_opening(job_title, company)
    
    # Create connection-specific content
    connection_content = get_connection_specific_content(connection_degree)
    
    # Create email body
    body = f"""Hi {first_name},

I hope this email finds you well! I noticed you reacted to my recent LinkedIn post and wanted to reach out personally to thank you for the engagement.

{opening}

I'd love to learn more about your work{f" at {company}" if company not in ["N/A", "your company"] else ""} and explore potential ways we might collaborate or share insights in our respective fields.

{connection_content}

Would you be open to a brief coffee chat or video call in the coming weeks? I'm always interested in connecting with thoughtful professionals who engage with content that resonates with them.

Best regards,
[Your Name]

P.S. Feel free to connect with me on LinkedIn as well if we haven't already: [Your LinkedIn URL]

---
This message was sent following your interaction with my LinkedIn post. If you'd prefer not to receive these types of messages, please let me know and I'll respect your preference."""

    return {
        "subject": subject,
        "body": body
    }

def get_personalized_opening(job_title, company):
    """Generate personalized opening based on job info"""
    
    title_lower = job_title.lower() if job_title != "N/A" else ""
    
    if any(term in title_lower for term in ['engineer', 'developer', 'technical', 'software']):
        return "As someone in the tech space, I thought you might find value in the discussions around innovation and technology trends that my posts often generate."
    elif any(term in title_lower for term in ['manager', 'director', 'vp', 'vice president', 'lead']):
        return "I appreciate leaders like yourself taking time to engage with professional content, and I'd value your perspective on the topics I share."
    elif any(term in title_lower for term in ['founder', 'ceo', 'entrepreneur', 'co-founder']):
        return "I have great respect for fellow entrepreneurs and founders, and I'd love to hear about your journey and current ventures."
    elif any(term in title_lower for term in ['analyst', 'consultant', 'specialist']):
        return "Your expertise caught my attention, and I'd be interested to learn more about your professional insights and experience."
    elif company not in ["N/A", "your company"] and company:
        return f"Your work at {company} caught my attention, and I'd be interested to learn more about what you're building there."
    else:
        return "I appreciate professionals who take time to engage with thoughtful content, and I'd value the opportunity to connect."

def get_connection_specific_content(connection_degree):
    """Generate content based on connection degree"""
    
    if connection_degree == "1st":
        return "Since we're already connected on LinkedIn, I thought it would be great to take our professional relationship beyond the platform."
    elif connection_degree == "2nd":
        return "I see we have mutual connections on LinkedIn, which suggests we likely move in similar professional circles."
    else:
        return "While we may not be directly connected yet, your engagement with my content suggests we share common professional interests."

def create_demo_summary_report(draft_emails, timestamp):
    """Create a summary report of the demo email drafts"""
    
    report_file = f"demo_gmail_summary_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write("# LinkedIn → Gmail Integration Demo Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Email Drafts:** {len(draft_emails)}\n\n")
        
        f.write("## 📧 Email Draft Summary\n\n")
        
        # Company distribution
        companies = [draft["contact"].get("company", "N/A") for draft in draft_emails]
        company_counts = {}
        for company in companies:
            if company != "N/A":
                company_counts[company] = company_counts.get(company, 0) + 1
        
        if company_counts:
            f.write("### Companies Represented\n")
            for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {company}: {count} contact(s)\n")
            f.write("\n")
        
        # Connection degrees
        degrees = [draft["contact"].get("connection_degree", "N/A") for draft in draft_emails]
        degree_counts = {}
        for degree in degrees:
            degree_counts[degree] = degree_counts.get(degree, 0) + 1
        
        f.write("### Connection Degrees\n")
        for degree, count in sorted(degree_counts.items()):
            f.write(f"- {degree}: {count} contact(s)\n")
        f.write("\n")
        
        f.write("## 📝 Sample Email Drafts\n\n")
        
        # Show first 3 email drafts as examples
        for i, draft in enumerate(draft_emails[:3], 1):
            contact = draft["contact"]
            email = draft["email_draft"]
            
            f.write(f"### {i}. {contact.get('name', 'Unknown')}\n")
            f.write(f"**Subject:** {email['subject']}\n\n")
            f.write("**Email Body:**\n")
            f.write("```\n")
            f.write(email['body'])
            f.write("\n```\n\n")
        
        f.write("## 🚀 Next Steps\n\n")
        f.write("1. Set up Gmail OAuth credentials in Google Cloud Console\n")
        f.write("2. Authenticate Gmail MCP server\n")
        f.write("3. Run smart_linkedin_extractor.py for automatic email drafting\n")
        f.write("4. Review and customize drafts in Gmail before sending\n")
    
    print(f"📄 Demo summary report: {report_file}")

if __name__ == "__main__":
    demo_gmail_integration()