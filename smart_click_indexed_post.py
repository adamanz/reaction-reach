#!/usr/bin/env python3
"""
Smart LinkedIn notifications - find all posts first, then click specific index
Usage: python smart_click_indexed_post.py [post_index]
Example: python smart_click_indexed_post.py 2  # clicks second post
"""

from browserbase import Browserbase
import os
import sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time
import openai
import json
import re
from datetime import datetime

load_dotenv()

# Configure OpenAI to use GPT-4o
openai.api_key = os.environ["OPENAI_API_KEY"]

bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

def extract_reactor_profiles(page):
    """Extract detailed profile information from the reactions modal"""
    
    print("🔍 Looking for reactor profile elements...")
    
    reactors = []
    
    # Try multiple selectors to find reactor elements
    reactor_selectors = [
        'div[data-finite-scroll-hotkey-item]',  # LinkedIn's data attribute for list items
        '.artdeco-list__item',  # LinkedIn's list item class
        '[data-view-name="profile-card"]',  # Profile card elements
        '.reaction-list-item',  # Reaction specific items
        '.feed-shared-actor',  # Actor elements
        'li[data-urn]'  # Generic data-urn items
    ]
    
    reactor_elements = []
    
    for selector in reactor_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"✅ Found {len(elements)} elements with selector: {selector}")
            reactor_elements = elements
            break
    
    if not reactor_elements:
        print("❌ No reactor elements found, trying broader search...")
        # Fallback: look for any elements that might contain profile info
        reactor_elements = page.query_selector_all('div:has-text("Manager"), div:has-text("Engineer"), div:has-text("Founder")')
    
    print(f"📊 Processing {len(reactor_elements)} potential reactor elements...")
    
    for i, element in enumerate(reactor_elements[:20]):  # Limit to first 20 to avoid timeouts
        try:
            print(f"🔍 Processing reactor {i+1}/{min(len(reactor_elements), 20)}...")
            
            # Extract basic info
            reactor_info = {}
            
            # Get all text content from the element
            element_text = element.inner_text() if element else ""
            
            # Try to find name (usually the first line or in a specific element)
            name_selectors = ['h3', '.actor-name', '.feed-shared-actor__name', 'span[dir="ltr"]', 'strong']
            name = None
            
            for name_sel in name_selectors:
                name_element = element.query_selector(name_sel)
                if name_element:
                    name = name_element.inner_text().strip()
                    if name and len(name) > 1 and not name.isdigit():
                        break
            
            # If no name found in selectors, try to extract from text
            if not name and element_text:
                lines = element_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 2 and not line.isdigit() and '•' not in line:
                        # Skip obvious non-names
                        if not any(skip in line.lower() for skip in ['manager', 'engineer', 'founder', 'director', 'lead', 'specialist']):
                            name = line
                            break
            
            if not name:
                print(f"   ⚠️ Could not extract name from element {i+1}")
                continue
                
            reactor_info['name'] = name
            print(f"   📝 Name: {name}")
            
            # Extract title/job info (usually follows name)
            title = None
            if element_text:
                lines = element_text.split('\n')
                name_found = False
                for line in lines:
                    line = line.strip()
                    if name_found and line and len(line) > 5:
                        # This is likely the title
                        title = line
                        break
                    if line == name:
                        name_found = True
            
            reactor_info['title'] = title or "View profile"
            print(f"   💼 Title: {title or 'View profile'}")
            
            # Try to extract profile URL
            profile_url = None
            link_elements = element.query_selector_all('a[href*="/in/"]')
            if link_elements:
                href = link_elements[0].get_attribute('href')
                if href:
                    # Clean up the URL
                    if href.startswith('/'):
                        profile_url = f"https://linkedin.com{href}"
                    else:
                        profile_url = href
            
            reactor_info['profile_url'] = profile_url or "N/A"
            print(f"   🔗 Profile: {profile_url or 'N/A'}")
            
            # Extract connection degree (1st, 2nd, 3rd)
            connection_degree = "N/A"
            if element_text:
                degree_match = re.search(r'(\d+)(st|nd|rd|th)', element_text)
                if degree_match:
                    connection_degree = f"{degree_match.group(1)}{degree_match.group(2)}"
            
            reactor_info['connection_degree'] = connection_degree
            print(f"   🤝 Connection: {connection_degree}")
            
            # Try to extract company (often appears in title)
            company = "N/A"
            if title and ' at ' in title:
                company = title.split(' at ')[-1].strip()
            elif element_text and ' at ' in element_text:
                # Look for "at Company" pattern
                at_match = re.search(r' at ([^\n•]+)', element_text)
                if at_match:
                    company = at_match.group(1).strip()
            
            reactor_info['company'] = company
            print(f"   🏢 Company: {company}")
            
            # Add extraction metadata
            reactor_info['extraction_timestamp'] = datetime.now().isoformat()
            reactor_info['element_text'] = element_text[:200]  # First 200 chars for debugging
            
            reactors.append(reactor_info)
            print(f"   ✅ Successfully extracted reactor {i+1}")
            
        except Exception as e:
            print(f"   ❌ Error extracting reactor {i+1}: {e}")
            continue
    
    print(f"\n📊 EXTRACTION SUMMARY:")
    print(f"   Total elements found: {len(reactor_elements)}")
    print(f"   Successfully extracted: {len(reactors)}")
    print(f"   Success rate: {len(reactors)/min(len(reactor_elements), 20)*100:.1f}%")
    
    return reactors

def create_reactor_summary(reactor_data, timestamp, post_index):
    """Create a human-readable markdown summary of the reactor data"""
    
    ordinal = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(post_index, f"{post_index}th")
    summary_filename = f"reactions_summary_{ordinal}_post_{timestamp}.md"
    
    with open(summary_filename, 'w') as f:
        f.write(f"# LinkedIn {ordinal.title()} Post Reactions Analysis\n\n")
        f.write(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Reactors:** {len(reactor_data)}\n")
        f.write(f"**Post Analyzed:** {ordinal.title()} most recent post\n\n")
        
        f.write("## 📊 Reactor Profiles\n\n")
        
        for i, reactor in enumerate(reactor_data, 1):
            f.write(f"### {i}. {reactor.get('name', 'Unknown')}\n")
            f.write(f"- **Title:** {reactor.get('title', 'N/A')}\n")
            f.write(f"- **Company:** {reactor.get('company', 'N/A')}\n")
            f.write(f"- **Connection:** {reactor.get('connection_degree', 'N/A')}\n")
            if reactor.get('profile_url') != 'N/A':
                f.write(f"- **Profile:** {reactor.get('profile_url')}\n")
            f.write("\n")
        
        # Add summary statistics
        f.write("## 📈 Summary Statistics\n\n")
        
        # Company distribution
        companies = [r.get('company', 'N/A') for r in reactor_data if r.get('company') != 'N/A']
        if companies:
            from collections import Counter
            company_counts = Counter(companies)
            f.write("### Top Companies\n")
            for company, count in company_counts.most_common(5):
                f.write(f"- {company}: {count}\n")
            f.write("\n")
        
        # Connection distribution
        connections = [r.get('connection_degree', 'N/A') for r in reactor_data]
        if connections:
            connection_counts = Counter(connections)
            f.write("### Connection Degrees\n")
            for conn, count in connection_counts.most_common():
                f.write(f"- {conn}: {count}\n")
            f.write("\n")
    
    print(f"📄 Summary report created: {summary_filename}")

def smart_click_indexed_post(post_index=1):
    """Smart LinkedIn post clicking - find all posts first, then click by index"""
    
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    ordinal = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(post_index, f"{post_index}th")
    
    print(f"🚀 Smart LinkedIn {ordinal.upper()} Post Clicker")
    print("=" * 60)
    print(f"🎯 Target: {ordinal} most recent post (index {post_index})")
    
    # Create session
    session = bb.sessions.create(
        project_id=os.environ["BROWSERBASE_PROJECT_ID"],
        browser_settings={
            "context": {
                "id": context_id,
                "persist": True
            }
        },
        proxies=[{
            "type": "browserbase",
            "geolocation": {
                "city": "New York",
                "state": "NY", 
                "country": "US"
            }
        }]
    )
    
    print(f"✅ Session: {session.id}")
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(session.connectUrl)
        context = browser.contexts[0]
        page = context.pages[0]
        
        try:
            # Navigate to notifications with posts filter
            print("📍 Navigating to LinkedIn notifications (my posts)...")
            notifications_url = "https://www.linkedin.com/notifications/?filter=my_posts_all"
            
            # Use networkidle for better loading
            page.goto(notifications_url, wait_until="networkidle", timeout=60000)
            time.sleep(3)
            
            print(f"✅ Loaded: {page.url}")
            
            # Take screenshot of notifications page
            notifications_screenshot = f"notifications_{ordinal}_post_{int(time.time())}.png"
            page.screenshot(path=notifications_screenshot)
            print(f"📸 Before click: {notifications_screenshot}")
            
            # Find ALL post links first
            print("🔍 Finding all post links...")
            post_link_selectors = [
                'a[href*="/feed/update/"]',
                'a[href*="/activity-"]',
                '[data-urn*="activity"] a',
                '.notification-item a[href*="/feed/"]'
            ]
            
            all_post_links = []
            for selector in post_link_selectors:
                links = page.query_selector_all(selector)
                if links:
                    print(f"✅ Found {len(links)} post links with selector: {selector}")
                    all_post_links = links
                    break
            
            if not all_post_links:
                print("❌ No post links found")
                return False
            
            print(f"📋 Total post links found: {len(all_post_links)}")
            
            # Check if we have enough posts
            if len(all_post_links) < post_index:
                print(f"❌ Only {len(all_post_links)} posts found, cannot access {ordinal} post (index {post_index})")
                return False
            
            # Click on the specified post (convert to 0-based index)
            target_link = all_post_links[post_index - 1]
            print(f"🎯 Clicking on {ordinal} post link...")
            
            # Get the URL to navigate to
            post_url = target_link.get_attribute('href')
            if post_url:
                if post_url.startswith('/'):
                    post_url = f"https://linkedin.com{post_url}"
                
                print(f"🔗 Navigating to {ordinal} post: {post_url}")
                page.goto(post_url, wait_until="networkidle", timeout=30000)
                time.sleep(3)
                
                print(f"✅ Successfully navigated to {ordinal} post: {page.url}")
                
                # Take screenshot of the post
                post_screenshot = f"{ordinal}_post_view_{int(time.time())}.png"
                page.screenshot(path=post_screenshot)
                print(f"📸 Post view: {post_screenshot}")
                
                # Look for reactions
                print(f"🔍 Looking for reactions on the {ordinal} post...")
                
                # Scroll to see reactions
                page.evaluate("window.scrollTo(0, 400)")
                time.sleep(2)
                
                # Try to find and click reactions
                print("🔍 Looking for 'and X others' reaction text...")
                others_elements = page.get_by_text("others").all()
                if others_elements:
                    print(f"✅ Found {len(others_elements)} 'others' text elements")
                    try:
                        others_elements[0].click()
                        time.sleep(3)
                        print("✅ Successfully clicked on 'others' text!")
                        
                        # Screenshots
                        reactions_screenshot = f"{ordinal}_post_reactions_details_{int(time.time())}.png"
                        page.screenshot(path=reactions_screenshot)
                        print(f"📸 Reaction details: {reactions_screenshot}")
                        
                        time.sleep(2)
                        modal_screenshot = f"{ordinal}_post_reactions_modal_{int(time.time())}.png"
                        page.screenshot(path=modal_screenshot)
                        print(f"📸 Modal view: {modal_screenshot}")
                        
                        # Extract the data
                        print(f"\n📊 EXTRACTING REACTOR DATA FROM {ordinal.upper()} POST...")
                        reactor_data = extract_reactor_profiles(page)
                        
                        if reactor_data:
                            print(f"✅ Successfully extracted {len(reactor_data)} reactor profiles from {ordinal} post!")
                            
                            # Save the data
                            data_filename = f"{ordinal}_post_reactions_data_{int(time.time())}.json"
                            with open(data_filename, 'w') as f:
                                json.dump(reactor_data, f, indent=2)
                            print(f"💾 Data saved to: {data_filename}")
                            
                            # Create summary
                            create_reactor_summary(reactor_data, int(time.time()), post_index)
                            return True
                        else:
                            print(f"⚠️ No reactor data extracted from {ordinal} post")
                    except Exception as e:
                        print(f"❌ Failed to click 'others' text: {e}")
                
                # Try other reaction selectors if the simple approach didn't work
                reaction_detail_selectors = [
                    'button:has-text("and") >> text=/.*and.*others/',
                    '[data-urn*="reaction"] button',
                    'button[aria-label*="See who reacted"]',
                    'button[aria-label*="reactions"]',
                    '.feed-shared-social-action-bar__reactions',
                    '.social-counts-reactions',
                    '.feed-shared-social-counts-bar button',
                ]
                
                for reaction_selector in reaction_detail_selectors:
                    try:
                        print(f"🎯 Trying reaction selector: {reaction_selector}")
                        
                        if 'has-text' in reaction_selector:
                            try:
                                reaction_elements = page.query_selector_all(reaction_selector)
                            except:
                                reaction_elements = page.get_by_text("and").all()
                        else:
                            reaction_elements = page.query_selector_all(reaction_selector)
                        
                        if reaction_elements:
                            print(f"✅ Found {len(reaction_elements)} elements with: {reaction_selector}")
                            try:
                                reaction_elements[0].click()
                                time.sleep(3)
                                print(f"✅ Successfully clicked reaction area!")
                                
                                # Extract data
                                print(f"\n📊 EXTRACTING REACTOR DATA FROM {ordinal.upper()} POST...")
                                reactor_data = extract_reactor_profiles(page)
                                
                                if reactor_data:
                                    print(f"✅ Successfully extracted {len(reactor_data)} reactor profiles from {ordinal} post!")
                                    
                                    # Save the data
                                    data_filename = f"{ordinal}_post_reactions_data_{int(time.time())}.json"
                                    with open(data_filename, 'w') as f:
                                        json.dump(reactor_data, f, indent=2)
                                    print(f"💾 Data saved to: {data_filename}")
                                    
                                    # Create summary
                                    create_reactor_summary(reactor_data, int(time.time()), post_index)
                                
                                return True
                                
                            except Exception as e:
                                print(f"   ❌ Click failed: {e}")
                                continue
                    except Exception as e:
                        print(f"   ❌ Selector error: {e}")
                        continue
                
                print(f"⚠️ Could not expand reactions for {ordinal} post, but successfully navigated to it")
                return True
            else:
                print(f"❌ Could not get URL for {ordinal} post")
                return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    # Get post index from command line argument, default to 2 (second post)
    post_index = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    
    if post_index < 1:
        print("❌ Post index must be 1 or greater")
        sys.exit(1)
    
    success = smart_click_indexed_post(post_index)
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'FAILED ❌'}")