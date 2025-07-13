#!/usr/bin/env python3
"""
Smart LinkedIn notifications - automatically click ANY post by index using GPT-4o
Usage: python smart_click_any_post.py [post_index]
Example: python smart_click_any_post.py 2  # clicks second post
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

def get_click_strategy_from_gpt4o(page_content, post_index):
    """Use GPT-4o to determine the best strategy to click the specified post"""
    
    ordinal = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(post_index, f"{post_index}th")
    
    prompt = f"""
    You are a LinkedIn automation expert. I need to click on the {ordinal.upper()} post in a LinkedIn notifications page.
    
    Here's the current page HTML structure:
    {page_content[:3000]}  # Truncate for token limits
    
    Please analyze this and provide a CSS selector or strategy to click on the {ordinal} post notification.
    
    Look for:
    1. Links to posts (like href="/feed/update/...")
    2. Clickable notification items
    3. The {ordinal} post in the list (index {post_index-1} or nth-child({post_index}))
    
    Return ONLY a valid CSS selector that will click on the {ordinal} post, like:
    - 'a[href*="/feed/update/"]:nth-of-type({post_index})'
    - '.notification-item:nth-child({post_index}) a'
    - '[data-urn*="activity"]:nth-child({post_index})'
    
    Be specific and target the {ordinal.upper()} item.
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-2024-11-20",  # Use GPT-4o
            messages=[
                {"role": "system", "content": "You are a web automation expert. Return only CSS selectors."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        selector = response.choices[0].message.content.strip()
        print(f"🧠 GPT-4o suggested selector for {ordinal} post: {selector}")
        return selector
        
    except Exception as e:
        print(f"⚠️ GPT-4o error: {e}")
        # Fallback selectors
        return f'a[href*="/feed/update/"]:nth-of-type({post_index})'

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

def smart_click_any_post(post_index=1):
    """Smart LinkedIn post clicking with GPT-4o intelligence for any post by index"""
    
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    ordinal = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(post_index, f"{post_index}th")
    
    print(f"🚀 Smart LinkedIn {ordinal.upper()} Post Clicker (GPT-4o Powered)")
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
            
            # Get page content for GPT-4o analysis
            print(f"🧠 Analyzing page with GPT-4o for {ordinal} post...")
            page_html = page.content()
            
            # Get smart selector from GPT-4o
            smart_selector = get_click_strategy_from_gpt4o(page_html, post_index)
            
            # Clean the selector if it has backticks
            if smart_selector.startswith('`') and smart_selector.endswith('`'):
                smart_selector = smart_selector[1:-1]
                print(f"🧹 Cleaned selector: {smart_selector}")
            
            # Try the GPT-4o suggested selector first
            print(f"🎯 Trying GPT-4o selector for {ordinal} post: {smart_selector}")
            
            try:
                element = page.query_selector(smart_selector)
                if element:
                    print(f"✅ Found {ordinal} post element with GPT-4o selector!")
                    element.click()
                    time.sleep(5)
                    
                    print(f"📍 After click URL: {page.url}")
                    
                    # Check if we actually navigated to a post (not still on notifications)
                    if "notifications" in page.url:
                        print("⚠️ Still on notifications page, trying to navigate to actual post...")
                        # Look for post links and take the specified index
                        post_links = page.query_selector_all('a[href*="/feed/update/"]')
                        if len(post_links) >= post_index:
                            print(f"🎯 Found {len(post_links)} post links, clicking {ordinal} one...")
                            post_links[post_index-1].click()  # Convert to 0-based index
                            time.sleep(5)
                            print(f"📍 New URL after {ordinal} post link click: {page.url}")
                        else:
                            print(f"❌ Less than {post_index} posts found, cannot click {ordinal} post")
                            return False
                    
                    # Continue with reaction extraction...
                    print(f"🔍 Looking for reactions on the {ordinal} post...")
                    
                    # Scroll to see reactions
                    page.evaluate("window.scrollTo(0, 400)")
                    time.sleep(2)
                    
                    # Try to find reactions
                    print("🔍 Looking for 'and X others' reaction text...")
                    others_elements = page.get_by_text("others").all()
                    if others_elements:
                        print(f"✅ Found {len(others_elements)} 'others' text elements")
                        try:
                            others_elements[0].click()
                            time.sleep(3)
                            print("✅ Successfully clicked on 'others' text!")
                            
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
                    
                    # Try other reaction selectors if needed...
                    reaction_detail_selectors = [
                        'button:has-text("and") >> text=/.*and.*others/',
                        '[data-urn*="reaction"] button',
                        'button[aria-label*="See who reacted"]',
                        '.feed-shared-social-action-bar__reactions',
                    ]
                    
                    for reaction_selector in reaction_detail_selectors:
                        try:
                            print(f"🎯 Trying reaction selector: {reaction_selector}")
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
                    
                    return True
                else:
                    print(f"❌ GPT-4o selector didn't find {ordinal} post element")
                    
            except Exception as e:
                print(f"❌ GPT-4o selector failed: {e}")
            
            # Fallback: Try common selectors
            print(f"🔄 Trying fallback selectors for {ordinal} post...")
            
            fallback_selectors = [
                f'a[href*="/feed/update/"]:nth-of-type({post_index})',
                f'[data-urn*="activity"]:nth-child({post_index}) a',
                f'.notification-item:nth-child({post_index}) a',
                f'.artdeco-list__item:nth-child({post_index}) a',
                f'li[data-urn]:nth-child({post_index}) a'
            ]
            
            for selector in fallback_selectors:
                print(f"🎯 Trying fallback selector: {selector}")
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with: {selector}")
                    try:
                        elements[0].click()
                        time.sleep(5)
                        
                        print(f"📍 Clicked {ordinal} post! New URL: {page.url}")
                        
                        # Continue with reactions extraction...
                        
                        return True
                    except Exception as e:
                        print(f"❌ Fallback failed: {e}")
                        continue
            
            print(f"❌ All selectors failed for {ordinal} post")
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
    
    success = smart_click_any_post(post_index)
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'FAILED ❌'}")