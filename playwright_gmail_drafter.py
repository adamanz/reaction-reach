#!/usr/bin/env python3
"""
Create Gmail drafts using Playwright automation
This bypasses the Gmail MCP server and creates drafts directly in the Gmail web interface
"""
import json
import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright

class PlaywrightGmailDrafter:
    def __init__(self):
        self.page = None
        self.browser = None
        self.context = None
        
    async def start_browser(self):
        """Start Playwright browser session"""
        playwright = await async_playwright().start()
        
        # Use existing browser profile if available
        self.browser = await playwright.chromium.launch(
            headless=False,  # Keep visible for debugging
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()
        
    async def navigate_to_gmail(self):
        """Navigate to Gmail and wait for it to load"""
        print("🌐 Navigating to Gmail...")
        await self.page.goto('https://mail.google.com/mail/u/0/#drafts')
        
        # Wait for Gmail to load
        try:
            await self.page.wait_for_selector('[role="button"][aria-label*="Compose"]', timeout=10000)
            print("✅ Gmail loaded successfully")
            return True
        except:
            print("⚠️ Gmail may need authentication - continuing...")
            return False
            
    async def create_draft(self, recipient, subject, body):
        """Create a single Gmail draft"""
        try:
            print(f"📝 Creating draft: {subject}")
            
            # Click Compose button
            compose_button = await self.page.query_selector('[role="button"][aria-label*="Compose"]')
            if not compose_button:
                # Try alternative selectors
                compose_button = await self.page.query_selector('div[role="button"]:has-text("Compose")')
            
            if compose_button:
                await compose_button.click()
                print("✅ Clicked Compose button")
            else:
                print("❌ Could not find Compose button")
                return False
            
            # Wait for compose window to open
            await self.page.wait_for_timeout(2000)
            
            # Fill recipient
            to_field = await self.page.query_selector('input[aria-label*="To"]')
            if not to_field:
                to_field = await self.page.query_selector('textarea[aria-label*="To"]')
            
            if to_field:
                await to_field.click()
                await to_field.fill(recipient)
                print(f"✅ Filled recipient: {recipient}")
            else:
                print("❌ Could not find To field")
                return False
            
            # Fill subject
            subject_field = await self.page.query_selector('input[aria-label*="Subject"]')
            if subject_field:
                await subject_field.click()
                await subject_field.fill(subject)
                print(f"✅ Filled subject: {subject}")
            else:
                print("❌ Could not find Subject field")
                return False
            
            # Fill body
            body_field = await self.page.query_selector('div[aria-label*="Message body"]')
            if not body_field:
                body_field = await self.page.query_selector('div[role="textbox"]')
            
            if body_field:
                await body_field.click()
                await body_field.fill(body)
                print("✅ Filled message body")
            else:
                print("❌ Could not find message body field")
                return False
            
            # Save as draft (Ctrl+S or close the compose window)
            await self.page.keyboard.press('Escape')  # Close compose window to save as draft
            print("✅ Draft saved")
            
            # Small delay between drafts
            await self.page.wait_for_timeout(3000)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating draft: {e}")
            return False
    
    async def create_all_drafts(self, contacts_data):
        """Create drafts for all LinkedIn contacts"""
        print(f"📧 Creating {len(contacts_data)} Gmail drafts...")
        
        drafts_created = 0
        
        for i, contact in enumerate(contacts_data, 1):
            name = contact.get('name', 'Unknown')
            first_name = name.split()[0] if name != 'Unknown' else 'there'
            
            # Extract job info
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
            
            # Create email content
            subject = f"LinkedIn Outreach: {name}" if connection_degree != "1st" else f"Following up with {first_name}"
            
            body = f"""Hi {first_name},

I hope this email finds you well! I noticed you reacted to my recent LinkedIn post and wanted to reach out personally to thank you for the engagement.

{self.get_personalized_opening(job_title, company)}

I'd love to learn more about your work{f" at {company}" if company not in ["N/A", "your company"] else ""} and explore potential ways we might collaborate or share insights in our respective fields.

{self.get_connection_specific_content(connection_degree)}

Would you be open to a brief coffee chat or video call in the coming weeks? I'm always interested in connecting with thoughtful professionals who engage with content that resonates with them.

Best regards,
Adam Anzuoni

P.S. Feel free to connect with me on LinkedIn as well: https://linkedin.com/in/adamanz

---
LinkedIn Contact Details:
- Name: {name}
- Title: {job_title}
- Company: {company}
- Connection: {connection_degree}
- Profile: {profile_url}

This draft was generated from LinkedIn reactions analysis.
Contact extracted on: {contact.get('extraction_timestamp', 'N/A')}"""

            # Use recipient email (for now using your email since we don't have real emails)
            recipient = "adam@mysimplestack.com"
            
            success = await self.create_draft(recipient, subject, body)
            
            if success:
                print(f"✅ {i}/{len(contacts_data)}: Draft created for {name}")
                drafts_created += 1
            else:
                print(f"❌ {i}/{len(contacts_data)}: Failed to create draft for {name}")
        
        return drafts_created
    
    def get_personalized_opening(self, job_title, company):
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
    
    def get_connection_specific_content(self, connection_degree):
        """Generate content based on connection degree"""
        if connection_degree == "1st":
            return "Since we're already connected on LinkedIn, I thought it would be great to take our professional relationship beyond the platform."
        elif connection_degree == "2nd":
            return "I see we have mutual connections on LinkedIn, which suggests we likely move in similar professional circles."
        else:
            return "While we may not be directly connected yet, your engagement with my content suggests we share common professional interests."
    
    async def close_browser(self):
        """Close browser session"""
        if self.browser:
            await self.browser.close()

async def main():
    """Main function to create Gmail drafts using Playwright"""
    print("🎭 Starting Playwright Gmail Draft Creation")
    print("=" * 50)
    
    # Load LinkedIn contacts data
    data_files = [
        'reactions_data_1752379497.json',
        'reactions_data_1752379004.json',
        'second_post_reactions_data_1752371102.json'
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
        return
    
    print(f"📊 Found {len(contacts_data)} LinkedIn contacts")
    
    # Create Gmail drafter
    drafter = PlaywrightGmailDrafter()
    
    try:
        # Start browser and navigate to Gmail
        await drafter.start_browser()
        gmail_loaded = await drafter.navigate_to_gmail()
        
        if not gmail_loaded:
            print("⚠️ Please authenticate in Gmail and press Enter to continue...")
            input()
        
        # Create all drafts
        drafts_created = await drafter.create_all_drafts(contacts_data)
        
        print(f"\n🏁 Results:")
        print(f"📧 Created {drafts_created} Gmail drafts")
        print(f"📊 Success rate: {drafts_created/len(contacts_data)*100:.1f}%")
        print(f"\n💡 Check your Gmail drafts folder now!")
        print(f"🔍 Look for subjects starting with 'LinkedIn Outreach:' or 'Following up with'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await drafter.close_browser()

if __name__ == "__main__":
    asyncio.run(main())