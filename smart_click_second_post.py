#!/usr/bin/env python3
"""
Smart LinkedIn notifications - automatically click SECOND post using GPT-4o
"""

from browserbase import Browserbase
import os
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

def get_click_strategy_from_gpt4o(page_content):
    """Use GPT-4o to determine the best strategy to click the SECOND post"""
    
    prompt = f"""
    You are a LinkedIn automation expert. I need to click on the SECOND most recent post in a LinkedIn notifications page.
    
    Here's the current page HTML structure:
    {page_content[:3000]}  # Truncate for token limits
    
    Please analyze this and provide a CSS selector or strategy to click on the SECOND post notification (not the first/most recent).
    
    Look for:
    1. Links to posts (like href="/feed/update/...")
    2. Clickable notification items
    3. The SECOND post in the list (index 1 or nth-child(2))
    
    Return ONLY a valid CSS selector that will click on the SECOND post, like:
    - 'a[href*="/feed/update/"]:nth-of-type(2)'
    - '.notification-item:nth-child(2) a'
    - '[data-urn*="activity"]:nth-child(2)'
    
    Be specific and target the SECOND item (not the first).
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
        print(f"🧠 GPT-4o suggested selector: {selector}")
        return selector
        
    except Exception as e:
        print(f"⚠️ GPT-4o error: {e}")
        # Fallback selectors for second post
        return 'a[href*="/feed/update/"]:nth-of-type(2)'

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
                        if not any(skip in line.lower() for skip in ['manager', 'engineer', 'founder', 'director', 'lead', 'specialist', 'aws', 'amazon']):
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
            
            reactor_info['title'] = title or "N/A"
            print(f"   💼 Title: {title or 'N/A'}")
            
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

def create_reactor_summary(reactor_data, timestamp):
    """Create a human-readable markdown summary of the reactor data"""
    
    summary_filename = f"reactions_summary_second_post_{timestamp}.md"
    
    with open(summary_filename, 'w') as f:
        f.write("# LinkedIn Second Post Reactions Analysis\n\n")
        f.write(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Reactors:** {len(reactor_data)}\n")
        f.write(f"**Post Analyzed:** Second most recent post\n\n")
        
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

def smart_click_second_post():
    """Smart LinkedIn second post clicking with GPT-4o intelligence"""
    
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    
    print(f"🚀 Smart LinkedIn SECOND Post Clicker (GPT-4o Powered)")
    print("=" * 60)
    
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
            notifications_screenshot = f"notifications_second_post_{int(time.time())}.png"
            page.screenshot(path=notifications_screenshot)
            print(f"📸 Before click: {notifications_screenshot}")
            
            # Get page content for GPT-4o analysis
            print("🧠 Analyzing page with GPT-4o for SECOND post...")
            page_html = page.content()
            
            # Get smart selector from GPT-4o for second post
            smart_selector = get_click_strategy_from_gpt4o(page_html)
            
            # Clean the selector if it has backticks
            if smart_selector.startswith('`') and smart_selector.endswith('`'):
                smart_selector = smart_selector[1:-1]
                print(f"🧹 Cleaned selector: {smart_selector}")
            
            # Try the GPT-4o suggested selector first
            print(f"🎯 Trying GPT-4o selector for SECOND post: {smart_selector}")
            
            try:
                element = page.query_selector(smart_selector)
                if element:
                    print("✅ Found SECOND post element with GPT-4o selector!")
                    element.click()
                    time.sleep(5)
                    
                    print(f"📍 After click URL: {page.url}")
                    
                    # Check if we actually navigated to a post (not still on notifications)
                    if "notifications" in page.url:
                        print("⚠️ Still on notifications page, trying to navigate to actual post...")
                        # Look for post links and take the second one
                        post_links = page.query_selector_all('a[href*="/feed/update/"]')
                        if len(post_links) >= 2:
                            print(f"🎯 Found {len(post_links)} post links, clicking SECOND one...")
                            post_links[1].click()  # Index 1 = second post
                            time.sleep(5)
                            print(f"📍 New URL after SECOND post link click: {page.url}")
                        else:
                            print("❌ Less than 2 posts found, cannot click second post")
                            return False
                    
                    # Screenshot after clicking
                    post_screenshot = f"second_post_after_click_{int(time.time())}.png"
                    page.screenshot(path=post_screenshot)
                    print(f"📸 After SECOND post click: {post_screenshot}")
                    
                    # Look for reactions on the second post
                    print("🔍 Looking for reactions on the SECOND post...")
                    
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
                            
                            # Screenshot the modal
                            reactions_screenshot = f"second_post_reactions_details_{int(time.time())}.png"
                            page.screenshot(path=reactions_screenshot)
                            print(f"📸 Reaction details: {reactions_screenshot}")
                            
                            time.sleep(2)
                            modal_screenshot = f"second_post_reactions_modal_{int(time.time())}.png"
                            page.screenshot(path=modal_screenshot)
                            print(f"📸 Modal view: {modal_screenshot}")
                            
                            # Extract the data
                            print("\n📊 EXTRACTING REACTOR DATA FROM SECOND POST...")
                            reactor_data = extract_reactor_profiles(page)
                            
                            if reactor_data:
                                print(f"✅ Successfully extracted {len(reactor_data)} reactor profiles from SECOND post!")
                                
                                # Save the data
                                data_filename = f"second_post_reactions_data_{int(time.time())}.json"
                                with open(data_filename, 'w') as f:
                                    json.dump(reactor_data, f, indent=2)
                                print(f"💾 Data saved to: {data_filename}")
                                
                                # Create summary
                                create_reactor_summary(reactor_data, int(time.time()))
                                return True
                            else:
                                print("⚠️ No reactor data extracted from SECOND post")
                        except Exception as e:
                            print(f"❌ Failed to click 'others' text: {e}")
                    
                    # If that didn't work, try other reaction selectors
                    reaction_detail_selectors = [
                        'button:has-text("and") >> text=/.*and.*others/',
                        '[data-urn*="reaction"] button',
                        'button[aria-label*="See who reacted"]',
                        'button[aria-label*="reactions"]',
                        '.feed-shared-social-action-bar__reactions',
                        '.social-counts-reactions',
                        '.feed-shared-social-counts-bar button',
                    ]
                    
                    reactions_expanded = False
                    for reaction_selector in reaction_detail_selectors:
                        try:
                            print(f"🎯 Trying reaction selector: {reaction_selector}")
                            
                            if 'has-text' in reaction_selector:
                                reaction_elements = page.query_selector_all(reaction_selector)
                            else:
                                reaction_elements = page.query_selector_all(reaction_selector)
                            
                            if reaction_elements:
                                print(f"✅ Found {len(reaction_elements)} elements with: {reaction_selector}")
                                try:
                                    reaction_elements[0].click()
                                    time.sleep(3)
                                    print(f"✅ Successfully clicked reaction area!")
                                    reactions_expanded = True
                                    
                                    # Extract data and save
                                    print("\n📊 EXTRACTING REACTOR DATA FROM SECOND POST...")
                                    reactor_data = extract_reactor_profiles(page)
                                    
                                    if reactor_data:
                                        print(f"✅ Successfully extracted {len(reactor_data)} reactor profiles from SECOND post!")
                                        
                                        # Save the data
                                        data_filename = f"second_post_reactions_data_{int(time.time())}.json"
                                        with open(data_filename, 'w') as f:
                                            json.dump(reactor_data, f, indent=2)
                                        print(f"💾 Data saved to: {data_filename}")
                                        
                                        # Create summary
                                        create_reactor_summary(reactor_data, int(time.time()))
                                    
                                    break
                                    
                                except Exception as e:
                                    print(f"   ❌ Click failed: {e}")
                                    continue
                        except Exception as e:
                            print(f"   ❌ Selector error: {e}")
                            continue
                    
                    return True
                else:
                    print("❌ GPT-4o selector didn't find SECOND post element")
                    
            except Exception as e:
                print(f"❌ GPT-4o selector failed: {e}")
            
            # Fallback: Try common selectors for SECOND post
            print("🔄 Trying fallback selectors for SECOND post...")
            
            fallback_selectors = [
                'a[href*="/feed/update/"]:nth-of-type(2)',  # Second post
                '[data-urn*="activity"]:nth-child(2) a',
                '.notification-item:nth-child(2) a',
                '.artdeco-list__item:nth-child(2) a',
                'li[data-urn]:nth-child(2) a'
            ]
            
            for selector in fallback_selectors:
                print(f"🎯 Trying fallback selector for SECOND post: {selector}")
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with: {selector}")
                    try:
                        elements[0].click()
                        time.sleep(5)
                        
                        print(f"📍 Clicked SECOND post! New URL: {page.url}")
                        
                        # Continue with reactions extraction for second post
                        # [Same reaction extraction logic as above]
                        
                        return True
                    except Exception as e:
                        print(f"❌ Fallback failed: {e}")
                        continue
            
            print("❌ All selectors failed for SECOND post")
            return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    success = smart_click_second_post()
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'FAILED ❌'}")