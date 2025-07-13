#!/usr/bin/env python3
"""
Gmail MCP Integration for LinkedIn Reactions Extractor
Automatically drafts personalized emails to extracted LinkedIn contacts
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GmailMCPIntegration:
    """
    Integration class for Gmail MCP Server operations
    Handles drafting personalized emails to LinkedIn contacts
    """
    
    def __init__(self):
        self.mcp_server_path = os.environ.get("GMAIL_MCP_SERVER_PATH", "npx @gongrzhe/server-gmail-autoauth-mcp")
        
    def is_gmail_mcp_available(self) -> bool:
        """Check if Gmail MCP server is available and authenticated"""
        try:
            # Check if credentials exist
            credentials_path = os.path.expanduser("~/.gmail-mcp/credentials.json")
            if not os.path.exists(credentials_path):
                logger.warning("Gmail MCP credentials not found. Run authentication first.")
                return False
            
            # Try a simple test call
            result = subprocess.run([
                "npx", "@gongrzhe/server-gmail-autoauth-mcp", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Gmail MCP availability check failed: {e}")
            return False
    
    def create_personalized_email_content(self, contact: Dict, context: Dict = None) -> Dict[str, str]:
        """
        Create personalized email content based on contact information
        
        Args:
            contact: Contact information from LinkedIn extraction
            context: Additional context (post content, mutual connections, etc.)
            
        Returns:
            Dict with 'subject' and 'body' keys
        """
        name = contact.get('name', 'there')
        first_name = name.split()[0] if name != 'there' else 'there'
        company = contact.get('company', 'your company')
        title = contact.get('title', 'your role')
        connection_degree = contact.get('connection_degree', 'N/A')
        
        # Create personalized subject line
        subject_templates = [
            f"Great connecting on LinkedIn, {first_name}!",
            f"Following up on your reaction to my LinkedIn post",
            f"Thanks for engaging with my LinkedIn content, {first_name}",
            f"Connecting after your LinkedIn interaction"
        ]
        
        # Choose subject based on connection degree
        if connection_degree == "1st":
            subject = subject_templates[0]
        else:
            subject = subject_templates[1]
            
        # Create personalized email body
        body_template = f"""Hi {first_name},

I hope this email finds you well! I noticed you reacted to my recent LinkedIn post and wanted to reach out personally to thank you for the engagement.

{self._get_personalized_opening(contact)}

I'd love to learn more about your work{f" at {company}" if company != "N/A" and company != "your company" else ""} and explore potential ways we might collaborate or share insights in our respective fields.

{self._get_connection_specific_content(contact)}

Would you be open to a brief coffee chat or video call in the coming weeks? I'm always interested in connecting with thoughtful professionals who engage with content that resonates with them.

Best regards,
[Your Name]

P.S. Feel free to connect with me on LinkedIn as well if we haven't already: [Your LinkedIn URL]

---
This message was sent following your interaction with my LinkedIn post. If you'd prefer not to receive these types of messages, please let me know and I'll respect your preference."""

        return {
            "subject": subject,
            "body": body_template
        }
    
    def _get_personalized_opening(self, contact: Dict) -> str:
        """Generate personalized opening based on contact info"""
        title = contact.get('title', '').lower()
        company = contact.get('company', 'N/A')
        
        if 'engineer' in title or 'developer' in title:
            return "As someone in the tech space, I thought you might find value in the discussions around innovation and technology trends that my posts often generate."
        elif 'manager' in title or 'director' in title or 'vp' in title:
            return "I appreciate leaders like yourself taking time to engage with professional content, and I'd value your perspective on the topics I share."
        elif 'founder' in title or 'ceo' in title or 'entrepreneur' in title:
            return "I have great respect for fellow entrepreneurs and founders, and I'd love to hear about your journey and current ventures."
        elif company != "N/A" and company.lower() not in ['your company', 'n/a']:
            return f"Your work at {company} caught my attention, and I'd be interested to learn more about what you're building there."
        else:
            return "I appreciate professionals who take time to engage with thoughtful content, and I'd value the opportunity to connect."
    
    def _get_connection_specific_content(self, contact: Dict) -> str:
        """Generate content based on connection degree"""
        connection_degree = contact.get('connection_degree', 'N/A')
        
        if connection_degree == "1st":
            return "Since we're already connected on LinkedIn, I thought it would be great to take our professional relationship beyond the platform."
        elif connection_degree == "2nd":
            return "I see we have mutual connections on LinkedIn, which suggests we likely move in similar professional circles."
        else:
            return "While we may not be directly connected yet, your engagement with my content suggests we share common professional interests."
    
    def draft_email_via_mcp(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        Draft an email using Gmail MCP server
        
        Args:
            recipient_email: Target email address
            subject: Email subject line
            body: Email body content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare MCP call data
            mcp_data = {
                "to": [recipient_email],
                "subject": subject,
                "body": body
            }
            
            # Create temporary file for MCP input
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(mcp_data, f, indent=2)
                temp_file = f.name
            
            try:
                # Call Gmail MCP server to draft email
                result = subprocess.run([
                    "npx", "@gongrzhe/server-gmail-autoauth-mcp", 
                    "draft_email",
                    "--input", temp_file
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info(f"✅ Email draft created successfully for {recipient_email}")
                    logger.info(f"Subject: {subject}")
                    return True
                else:
                    logger.error(f"❌ Failed to create email draft: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    
        except Exception as e:
            logger.error(f"❌ Error drafting email via MCP: {e}")
            return False
    
    def batch_draft_emails(self, contacts: List[Dict], context: Dict = None) -> Dict[str, int]:
        """
        Create draft emails for multiple contacts
        
        Args:
            contacts: List of contact dictionaries from LinkedIn extraction
            context: Additional context for personalization
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        logger.info(f"🚀 Starting batch email drafting for {len(contacts)} contacts...")
        
        for i, contact in enumerate(contacts, 1):
            name = contact.get('name', f'Contact {i}')
            logger.info(f"📧 Processing {i}/{len(contacts)}: {name}")
            
            # Check if we have enough info to create a meaningful email
            if not contact.get('name') or contact.get('name') in ['N/A', 'Unknown']:
                logger.warning(f"⚠️ Skipping contact with insufficient info: {contact}")
                results["skipped"] += 1
                continue
            
            # For demo purposes, we'll use a placeholder email since we don't have real emails
            # In practice, you'd integrate with Apollo or other enrichment services
            placeholder_email = self._generate_placeholder_email(contact)
            
            if not placeholder_email:
                logger.warning(f"⚠️ No email available for {name}, skipping")
                results["skipped"] += 1
                continue
            
            # Generate personalized content
            email_content = self.create_personalized_email_content(contact, context)
            
            # Create draft email
            success = self.draft_email_via_mcp(
                placeholder_email,
                email_content["subject"],
                email_content["body"]
            )
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
                
            # Add small delay between requests to be respectful
            import time
            time.sleep(1)
        
        logger.info(f"📊 Batch drafting complete: {results}")
        return results
    
    def _generate_placeholder_email(self, contact: Dict) -> Optional[str]:
        """
        Generate placeholder email for demonstration
        In production, integrate with email finding services
        """
        name = contact.get('name', '').lower().replace(' ', '.')
        company = contact.get('company', 'example.com').lower()
        
        # Skip if no name
        if not name or name in ['n/a', 'unknown']:
            return None
            
        # Simple placeholder generation for demo
        if company and company != 'n/a' and company != 'your company':
            domain = company.split()[0].replace(',', '').replace('.', '') + '.com'
            return f"{name}@{domain}"
        else:
            return f"{name}@example.com"
    
    def create_summary_report(self, contacts: List[Dict], results: Dict[str, int]) -> str:
        """
        Create a summary report of the email drafting process
        
        Args:
            contacts: Original contacts list
            results: Results from batch_draft_emails
            
        Returns:
            Formatted summary report
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""# LinkedIn Outreach Email Summary Report

**Generated:** {timestamp}
**Total Contacts Processed:** {len(contacts)}

## 📊 Results Summary

- ✅ **Successfully Drafted:** {results['success']} emails
- ❌ **Failed:** {results['failed']} emails  
- ⚠️ **Skipped:** {results['skipped']} contacts (insufficient data)

## 📈 Success Rate

**{(results['success'] / len(contacts) * 100):.1f}%** of contacts had draft emails created

## 📋 Contact Details

### ✅ Successfully Processed Contacts:
"""
        
        # Add details for each contact type
        for i, contact in enumerate(contacts, 1):
            name = contact.get('name', f'Contact {i}')
            company = contact.get('company', 'N/A')
            title = contact.get('title', 'N/A')
            
            if i <= results['success']:
                report += f"\n{i}. **{name}**\n"
                report += f"   - Company: {company}\n"
                report += f"   - Title: {title}\n"
                report += f"   - Status: ✅ Draft Created\n"
        
        if results['skipped'] > 0:
            report += f"\n### ⚠️ Skipped Contacts:\n"
            skipped_count = 0
            for i, contact in enumerate(contacts, 1):
                if skipped_count >= results['skipped']:
                    break
                name = contact.get('name', f'Contact {i}')
                if not name or name in ['N/A', 'Unknown']:
                    skipped_count += 1
                    report += f"\n- **{name}** (insufficient data)\n"
        
        report += f"\n## 📧 Next Steps\n\n"
        report += f"1. Review and customize the {results['success']} draft emails in your Gmail drafts folder\n"
        report += f"2. Add personal touches based on your specific relationship with each contact\n"
        report += f"3. Verify email addresses and update with real contact information\n"
        report += f"4. Send emails at appropriate times for maximum engagement\n"
        
        return report


def integrate_gmail_with_extractor(contacts_data: List[Dict], context: Dict = None) -> bool:
    """
    Main integration function to add Gmail drafting to LinkedIn extraction workflow
    
    Args:
        contacts_data: List of contacts from LinkedIn extraction
        context: Additional context for email personalization
        
    Returns:
        True if integration successful, False otherwise
    """
    logger.info("🚀 Starting Gmail MCP integration...")
    
    # Initialize Gmail integration
    gmail = GmailMCPIntegration()
    
    # Check if Gmail MCP is available
    if not gmail.is_gmail_mcp_available():
        logger.error("❌ Gmail MCP server not available. Please install and authenticate first.")
        logger.info("📋 Setup instructions:")
        logger.info("1. npm install -g @gongrzhe/server-gmail-autoauth-mcp")
        logger.info("2. npx @gongrzhe/server-gmail-autoauth-mcp auth")
        return False
    
    # Filter contacts with sufficient information
    valid_contacts = [
        contact for contact in contacts_data 
        if contact.get('name') and contact.get('name') not in ['N/A', 'Unknown']
    ]
    
    if not valid_contacts:
        logger.warning("⚠️ No valid contacts found for email drafting")
        return False
    
    logger.info(f"📧 Found {len(valid_contacts)} valid contacts for email drafting")
    
    # Create draft emails
    results = gmail.batch_draft_emails(valid_contacts, context)
    
    # Generate summary report
    summary = gmail.create_summary_report(contacts_data, results)
    
    # Save summary report
    timestamp = int(datetime.now().timestamp())
    summary_filename = f"gmail_outreach_summary_{timestamp}.md"
    with open(summary_filename, 'w') as f:
        f.write(summary)
    
    logger.info(f"📄 Summary report saved: {summary_filename}")
    
    # Print quick summary
    logger.info(f"✅ Gmail integration complete!")
    logger.info(f"📊 Created {results['success']} draft emails")
    logger.info(f"📧 Check your Gmail drafts folder to review and send")
    
    return results['success'] > 0


if __name__ == "__main__":
    # Test the Gmail integration with sample data
    sample_contacts = [
        {
            "name": "John Doe",
            "title": "Senior Software Engineer at Google",
            "company": "Google",
            "connection_degree": "1st",
            "profile_url": "https://linkedin.com/in/johndoe"
        },
        {
            "name": "Jane Smith", 
            "title": "Product Manager at Microsoft",
            "company": "Microsoft",
            "connection_degree": "2nd",
            "profile_url": "https://linkedin.com/in/janesmith"
        }
    ]
    
    # Test integration
    integrate_gmail_with_extractor(sample_contacts)