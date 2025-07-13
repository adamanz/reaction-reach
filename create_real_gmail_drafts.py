#!/usr/bin/env python3
"""
Create actual Gmail drafts for the extracted LinkedIn contacts
Uses your real email address so you can see the drafts
"""
import json
import subprocess
import tempfile
import os
from datetime import datetime

def create_real_gmail_drafts():
    """Create Gmail drafts using real email addresses"""
    
    print("📧 Creating Real Gmail Drafts for LinkedIn Contacts")
    print("=" * 60)
    
    # Load the most recent LinkedIn data
    data_files = [
        'reactions_data_1752379497.json',
        'reactions_data_1752379004.json'
    ]
    
    contacts_data = None
    for data_file in data_files:
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    contacts_data = json.load(f)
                print(f"✅ Loaded data from: {data_file}")
                break
            except Exception as e:
                continue
    
    if not contacts_data:
        print("❌ No LinkedIn data found")
        return False
    
    # Your actual email address for drafts
    your_email = "adam@mysimplestack.com"
    
    print(f"📧 Creating drafts to: {your_email}")
    print(f"📊 Processing {len(contacts_data)} LinkedIn contacts...")
    
    drafts_created = 0
    
    for i, contact in enumerate(contacts_data, 1):
        name = contact.get('name', 'Unknown')
        first_name = name.split()[0] if name != 'Unknown' else 'there'
        
        # Extract better job info from element_text
        element_text = contact.get('element_text', '')
        job_title = "N/A"
        company = contact.get('company', 'N/A')
        
        if element_text:
            lines = element_text.split('\n')
            for line in lines:
                line = line.strip()
                if (len(line) > 10 and 
                    name not in line and 
                    'View' not in line and 
                    'profile' not in line and 
                    'connection' not in line and
                    '1st' not in line and '2nd' not in line and '3rd' not in line):
                    job_title = line
                    break
        
        connection_degree = contact.get('connection_degree', 'N/A')
        profile_url = contact.get('profile_url', '')
        
        # Create personalized email
        subject = f"LinkedIn Outreach: {name}" if connection_degree != "1st" else f"Following up with {first_name}"
        
        body = f"""LinkedIn Contact: {name}

Contact Details:
- Name: {name}
- Title: {job_title}
- Company: {company}
- Connection: {connection_degree}
- Profile: {profile_url}

Personalized Outreach Email Draft:
---

Hi {first_name},

I hope this email finds you well! I noticed you reacted to my recent LinkedIn post and wanted to reach out personally to thank you for the engagement.

{get_personalized_opening(job_title, company)}

I'd love to learn more about your work{f" at {company}" if company not in ["N/A", "your company"] else ""} and explore potential ways we might collaborate or share insights in our respective fields.

{get_connection_specific_content(connection_degree)}

Would you be open to a brief coffee chat or video call in the coming weeks? I'm always interested in connecting with thoughtful professionals who engage with content that resonates with them.

Best regards,
Adam Anzuoni

P.S. Feel free to connect with me on LinkedIn as well: https://linkedin.com/in/adamanz

---
This draft was generated from LinkedIn reactions analysis.
Contact extracted on: {contact.get('extraction_timestamp', 'N/A')}
"""

        # Create email data
        email_data = {
            "to": [your_email],
            "subject": subject,
            "body": body
        }
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(email_data, f, indent=2)
                temp_file = f.name
            
            # Call Gmail MCP
            result = subprocess.run([
                "npx", "@gongrzhe/server-gmail-autoauth-mcp",
                "draft_email",
                "--input", temp_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ {i}/9: Draft created for {name}")
                drafts_created += 1
            else:
                print(f"❌ {i}/9: Failed to create draft for {name}")
                
        except Exception as e:
            print(f"❌ {i}/9: Error creating draft for {name}: {e}")
        finally:
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.unlink(temp_file)
    
    print(f"\n🏁 Results:")
    print(f"📧 Created {drafts_created} Gmail drafts")
    print(f"📊 Success rate: {drafts_created/len(contacts_data)*100:.1f}%")
    print(f"\n💡 Check your Gmail drafts folder now!")
    print(f"🔍 Look for subjects starting with 'LinkedIn Outreach:' or 'Following up with'")
    
    return drafts_created > 0

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

if __name__ == "__main__":
    create_real_gmail_drafts()