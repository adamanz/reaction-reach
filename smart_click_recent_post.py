#!/usr/bin/env python3
"""
Smart LinkedIn notifications - automatically click most recent post using GPT-4o
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
    """Use GPT-4o to determine the best strategy to click the most recent post"""
    
    prompt = f"""
    You are a LinkedIn automation expert. I need to click on the MOST RECENT post in a LinkedIn notifications page.
    
    Here's the current page HTML structure:
    {page_content[:3000]}  # Truncate for token limits
    
    Please analyze this and provide a CSS selector or strategy to click on the FIRST/MOST RECENT post notification.
    
    Look for:
    1. Links to posts (like href="/feed/update/...")
    2. Clickable notification items
    3. The topmost/first post in the list
    
    Return ONLY a valid CSS selector that will click on the most recent post, like:
    - 'a[href*="/feed/update/"]:first-of-type'
    - '.notification-item:first-child a'
    - '[data-urn*="activity"]:first-child'
    
    Be specific and target the FIRST/MOST RECENT item.
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
        # Fallback selectors
        return 'a[href*="/feed/update/"]:first-of-type'

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
    
    summary_filename = f"reactions_summary_{timestamp}.md"
    
    with open(summary_filename, 'w') as f:
        f.write("# LinkedIn Post Reactions Analysis\n\n")
        f.write(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Reactors:** {len(reactor_data)}\n\n")
        
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

def smart_click_recent_post():
    """Smart LinkedIn recent post clicking with GPT-4o intelligence"""
    
    context_id = "929c2463-a010-4425-b900-4fde8a7ca327"
    
    print(f"🚀 Smart LinkedIn Recent Post Clicker (GPT-4o Powered)")
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
            notifications_screenshot = f"notifications_before_click_{int(time.time())}.png"
            page.screenshot(path=notifications_screenshot)
            print(f"📸 Before click: {notifications_screenshot}")
            
            # Get page content for GPT-4o analysis
            print("🧠 Analyzing page with GPT-4o...")
            page_html = page.content()
            
            # Get smart selector from GPT-4o
            smart_selector = get_click_strategy_from_gpt4o(page_html)
            
            # Clean the selector if it has backticks
            if smart_selector.startswith('`') and smart_selector.endswith('`'):
                smart_selector = smart_selector[1:-1]
                print(f"🧹 Cleaned selector: {smart_selector}")
            
            # Try the GPT-4o suggested selector first
            print(f"🎯 Trying GPT-4o selector: {smart_selector}")
            
            try:
                element = page.query_selector(smart_selector)
                if element:
                    print("✅ Found element with GPT-4o selector!")
                    element.click()
                    time.sleep(5)
                    
                    print(f"📍 After click URL: {page.url}")
                    
                    # Check if we actually navigated to a post (not still on notifications)
                    if "notifications" in page.url:
                        print("⚠️ Still on notifications page, trying to navigate to actual post...")
                        # Look for a direct link to the post
                        post_links = page.query_selector_all('a[href*="/feed/update/"]')
                        if post_links:
                            print(f"🎯 Found {len(post_links)} post links, clicking first one...")
                            post_links[0].click()
                            time.sleep(5)
                            print(f"📍 New URL after post link click: {page.url}")
                    
                    # Screenshot after clicking
                    post_screenshot = f"post_after_click_{int(time.time())}.png"
                    page.screenshot(path=post_screenshot)
                    print(f"📸 After click: {post_screenshot}")
                    
                    # Look for reactions
                    print("🔍 Looking for reactions on the post...")
                    
                    # Scroll to see reactions
                    page.evaluate("window.scrollTo(0, 400)")
                    time.sleep(2)
                    
                    # First try to click on the "Reactions" text or the reaction images area
                    print("🎯 Looking for reaction details to expand...")
                    
                    # Enhanced selectors to find the reactions area
                    reaction_detail_selectors = [
                        # Try clicking on "Reactions" text
                        'text="Reactions"',
                        # Try clicking on the reaction avatars area
                        '.feed-shared-social-action-bar__reactions',
                        '.social-actions-bar .reactions-list',
                        '.feed-shared-social-counts-bar',
                        # Try the reaction button itself
                        'button[aria-label*="reactions"]',
                        'button[aria-label*="likes"]',
                        'button[aria-label*="See who"]',
                        # Try clicking on reaction images
                        '.feed-shared-social-action-bar img:first-of-type',
                        '[data-urn*="reaction"]',
                        # Generic social actions
                        '.social-actions-bar button:first-child',
                        '.feed-shared-social-action-bar button:first-child'
                    ]
                    
                    reactions_expanded = False
                    for reaction_selector in reaction_detail_selectors:
                        try:
                            print(f"🎯 Trying reaction selector: {reaction_selector}")
                            
                            if reaction_selector.startswith('text='):
                                # Handle text selector differently
                                elements = page.get_by_text("Reactions").all()
                            else:
                                elements = page.query_selector_all(reaction_selector)
                            
                            if elements:
                                print(f"✅ Found {len(elements)} elements with: {reaction_selector}")
                                try:
                                    if reaction_selector.startswith('text='):
                                        elements[0].click()
                                    else:
                                        elements[0].click()
                                    
                                    time.sleep(3)
                                    print(f"✅ Successfully clicked reaction area!")
                                    reactions_expanded = True
                                    
                                    # Screenshot reaction details modal/popup
                                    reactions_screenshot = f"reactions_details_{int(time.time())}.png"
                                    page.screenshot(path=reactions_screenshot)
                                    print(f"📸 Reaction details: {reactions_screenshot}")
                                    
                                    # Check if a modal opened and take another screenshot after a moment
                                    time.sleep(2)
                                    modal_screenshot = f"reactions_modal_{int(time.time())}.png"
                                    page.screenshot(path=modal_screenshot)
                                    print(f"📸 Modal view: {modal_screenshot}")
                                    
                                    break
                                    
                                except Exception as e:
                                    print(f"   ❌ Click failed: {e}")
                                    continue
                            else:
                                print(f"   ❌ No elements found")
                        except Exception as e:
                            print(f"   ❌ Selector error: {e}")
                            continue
                    
                    if not reactions_expanded:
                        print("⚠️ Could not expand reactions, but captured post view")
                        # Take a screenshot anyway
                        reactions_screenshot = f"post_reactions_view_{int(time.time())}.png"
                        page.screenshot(path=reactions_screenshot)
                        print(f"📸 Post reactions view: {reactions_screenshot}")
                    
                    print("\n🎉 SUCCESS! Screenshots captured:")
                    print(f"   📸 {notifications_screenshot}")
                    print(f"   📸 {post_screenshot}")
                    if 'reactions_screenshot' in locals():
                        print(f"   📸 {reactions_screenshot}")
                    
                    return True
                else:
                    print("❌ GPT-4o selector didn't find element")
                    
            except Exception as e:
                print(f"❌ GPT-4o selector failed: {e}")
            
            # Fallback: Try common selectors
            print("🔄 Trying fallback selectors...")
            
            fallback_selectors = [
                'a[href*="/feed/update/"]:first-of-type',
                '[data-urn*="activity"]:first-child a',
                '.notification-item:first-child a',
                '.artdeco-list__item:first-child a',
                'li[data-urn]:first-child a'
            ]
            
            for selector in fallback_selectors:
                print(f"🎯 Trying fallback: {selector}")
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with: {selector}")
                    try:
                        elements[0].click()
                        time.sleep(5)
                        
                        print(f"📍 Clicked! New URL: {page.url}")
                        
                        # Check if we actually navigated to a post (not still on notifications)
                        if "notifications" in page.url:
                            print("⚠️ Still on notifications page, trying to navigate to actual post...")
                            # Look for a direct link to the post
                            post_links = page.query_selector_all('a[href*="/feed/update/"]')
                            if post_links:
                                print(f"🎯 Found {len(post_links)} post links, trying to open post in new tab...")
                                
                                # Get the href directly and navigate to it
                                post_url = post_links[0].get_attribute('href')
                                if post_url:
                                    if post_url.startswith('/'):
                                        post_url = f"https://linkedin.com{post_url}"
                                    
                                    print(f"🔗 Navigating directly to post: {post_url}")
                                    page.goto(post_url, wait_until="networkidle", timeout=30000)
                                    time.sleep(3)
                                    print(f"📍 New URL after direct navigation: {page.url}")
                                    
                                    # Verify we're on a post page
                                    if "/feed/update/" in page.url:
                                        print("✅ Successfully navigated to individual post!")
                                    else:
                                        print("❌ Still not on individual post page")
                                        return False
                        
                        # Screenshot
                        fallback_screenshot = f"fallback_click_{int(time.time())}.png"
                        page.screenshot(path=fallback_screenshot)
                        print(f"📸 Fallback result: {fallback_screenshot}")
                        
                        # Look for reactions since we successfully clicked
                        print("🔍 Looking for reactions on the post...")
                        
                        # Scroll to see reactions
                        page.evaluate("window.scrollTo(0, 400)")
                        time.sleep(2)
                        
                        # First try to click on the "Reactions" text or the reaction images area
                        print("🎯 Looking for reaction details to expand...")
                        
                        # FIRST: Try to find and click the "Robert Khirallah and 7 others" text directly
                        print("🔍 Looking for 'and X others' reaction text...")
                        others_elements = page.get_by_text("others").all()
                        if others_elements:
                            print(f"✅ Found {len(others_elements)} 'others' text elements")
                            try:
                                others_elements[0].click()
                                time.sleep(3)
                                print("✅ Successfully clicked on 'others' text!")
                                reactions_expanded = True
                                
                                # Screenshot the modal
                                reactions_screenshot = f"reactions_details_{int(time.time())}.png"
                                page.screenshot(path=reactions_screenshot)
                                print(f"📸 Reaction details: {reactions_screenshot}")
                                
                                time.sleep(2)
                                modal_screenshot = f"reactions_modal_{int(time.time())}.png"
                                page.screenshot(path=modal_screenshot)
                                print(f"📸 Modal view: {modal_screenshot}")
                                
                                # Extract the data
                                print("\n📊 EXTRACTING REACTOR DATA...")
                                reactor_data = extract_reactor_profiles(page)
                                
                                if reactor_data:
                                    print(f"✅ Successfully extracted {len(reactor_data)} reactor profiles!")
                                    
                                    # Save the data
                                    data_filename = f"reactions_data_{int(time.time())}.json"
                                    with open(data_filename, 'w') as f:
                                        json.dump(reactor_data, f, indent=2)
                                    print(f"💾 Data saved to: {data_filename}")
                                    
                                    # Create summary
                                    create_reactor_summary(reactor_data, int(time.time()))
                                    return True
                                else:
                                    print("⚠️ No reactor data extracted")
                            except Exception as e:
                                print(f"❌ Failed to click 'others' text: {e}")
                        
                        # If that didn't work, try other selectors
                        # Enhanced selectors to find the reactions area - targeting the specific "Robert Khirallah and 7 others" area
                        reaction_detail_selectors = [
                            # Target the specific reactions area with names
                            'button:has-text("and") >> text=/.*and.*others/',
                            'button:has-text("Robert Khirallah")',
                            # Try the reaction count area
                            '[data-urn*="reaction"] button',
                            'button[aria-label*="See who reacted"]',
                            'button[aria-label*="reactions"]',
                            # Try clicking on the text that shows "Robert Khirallah and 7 others"
                            'text="Robert Khirallah and 7 others"',
                            # Try broader selectors for the reaction area
                            '.feed-shared-social-action-bar__reactions',
                            '.social-counts-reactions',
                            '.feed-shared-social-counts-bar button',
                            # Try the reaction images/icons area
                            '.feed-shared-social-action-bar img:first-of-type',
                            # Generic fallbacks
                            'button[aria-label*="likes"]',
                            '.social-actions-bar button:first-child'
                        ]
                        
                        reactions_expanded = False
                        for reaction_selector in reaction_detail_selectors:
                            try:
                                print(f"🎯 Trying reaction selector: {reaction_selector}")
                                
                                if reaction_selector.startswith('text='):
                                    # Handle text selector differently
                                    text_to_find = reaction_selector.replace('text=', '').strip('"')
                                    reaction_elements = page.get_by_text(text_to_find).all()
                                elif 'has-text' in reaction_selector or reaction_selector.startswith('text='):
                                    # Handle complex text selectors
                                    try:
                                        reaction_elements = page.query_selector_all(reaction_selector)
                                    except:
                                        # Fallback to simpler approach
                                        reaction_elements = page.get_by_text("and").all()
                                else:
                                    reaction_elements = page.query_selector_all(reaction_selector)
                                
                                if reaction_elements:
                                    print(f"✅ Found {len(reaction_elements)} elements with: {reaction_selector}")
                                    try:
                                        if reaction_selector.startswith('text='):
                                            reaction_elements[0].click()
                                        else:
                                            reaction_elements[0].click()
                                        
                                        time.sleep(3)
                                        print(f"✅ Successfully clicked reaction area!")
                                        reactions_expanded = True
                                        
                                        # Screenshot reaction details modal/popup
                                        reactions_screenshot = f"reactions_details_{int(time.time())}.png"
                                        page.screenshot(path=reactions_screenshot)
                                        print(f"📸 Reaction details: {reactions_screenshot}")
                                        
                                        # Check if a modal opened and take another screenshot after a moment
                                        time.sleep(2)
                                        modal_screenshot = f"reactions_modal_{int(time.time())}.png"
                                        page.screenshot(path=modal_screenshot)
                                        print(f"📸 Modal view: {modal_screenshot}")
                                        
                                        # NOW EXTRACT THE REACTOR DATA
                                        print("\n📊 EXTRACTING REACTOR DATA...")
                                        reactor_data = extract_reactor_profiles(page)
                                        
                                        if reactor_data:
                                            print(f"✅ Successfully extracted {len(reactor_data)} reactor profiles!")
                                            
                                            # Save the data
                                            import json
                                            data_filename = f"reactions_data_{int(time.time())}.json"
                                            with open(data_filename, 'w') as f:
                                                json.dump(reactor_data, f, indent=2)
                                            print(f"💾 Data saved to: {data_filename}")
                                            
                                            # Create a readable summary
                                            create_reactor_summary(reactor_data, int(time.time()))
                                        else:
                                            print("⚠️ No reactor data extracted")
                                        
                                        break
                                        
                                    except Exception as e:
                                        print(f"   ❌ Click failed: {e}")
                                        continue
                                else:
                                    print(f"   ❌ No elements found")
                            except Exception as e:
                                print(f"   ❌ Selector error: {e}")
                                continue
                        
                        if not reactions_expanded:
                            print("⚠️ Could not expand reactions, but captured post view")
                            # Take a screenshot anyway
                            final_reactions_screenshot = f"post_reactions_view_{int(time.time())}.png"
                            page.screenshot(path=final_reactions_screenshot)
                            print(f"📸 Post reactions view: {final_reactions_screenshot}")
                        
                        return True
                    except Exception as e:
                        print(f"❌ Fallback failed: {e}")
                        continue
            
            print("❌ All selectors failed")
            return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    success = smart_click_recent_post()
    print(f"\n🏁 RESULT: {'SUCCESS ✅' if success else 'FAILED ❌'}")