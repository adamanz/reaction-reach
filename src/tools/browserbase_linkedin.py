import os
import json
import random
from crewai_tools import tool
from playwright.sync_api import sync_playwright
from html2text import html2text
from time import sleep
from typing import Optional, Dict, Any

@tool("Browserbase LinkedIn Navigator")
def browserbase_linkedin(
    url: str, 
    action: str = "extract_content",
    wait_time: Optional[int] = None,
    scroll_count: int = 3
) -> str:
    """
    Navigates LinkedIn using Browserbase with stealth capabilities
    
    :param url: The LinkedIn URL to navigate to
    :param action: Action to perform - 'extract_content', 'extract_posts', 'extract_reactions', 'scroll_and_extract'
    :param wait_time: Custom wait time in seconds (default: intelligent based on action)
    :param scroll_count: Number of times to scroll for infinite scroll content
    :return: The extracted content as text or JSON
    """
    print(f"Navigating to LinkedIn: {url} with action: {action}")
    
    # Intelligent wait times based on action
    if wait_time is None:
        wait_times = {
            "extract_content": 5,
            "extract_posts": 10, 
            "extract_reactions": 8,
            "scroll_and_extract": 15
        }
        wait_time = wait_times.get(action, 7)
    
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.connect_over_cdp(
                "wss://connect.browserbase.com?apiKey="
                + os.environ["BROWSERBASE_API_KEY"]
                + f"&projectId={os.environ['BROWSERBASE_PROJECT_ID']}"
            )
            
            context = browser.contexts[0]
            page = context.pages[0]
            
            # Set LinkedIn-optimized user agent and viewport
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate with error handling
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                print(f"Navigation error: {e}")
                return f"Error navigating to {url}: {str(e)}"
            
            # Handle different actions
            if action == "scroll_and_extract":
                return _scroll_and_extract(page, scroll_count, wait_time)
            elif action == "extract_posts":
                return _extract_posts(page, wait_time)
            elif action == "extract_reactions":
                return _extract_reactions(page, wait_time)
            else:
                # Default: extract_content
                return _extract_basic_content(page, wait_time)
                
        except Exception as e:
            print(f"Browserbase error: {e}")
            return f"Browser error: {str(e)}"
        finally:
            try:
                browser.close()
            except:
                pass

def _extract_basic_content(page, wait_time: int) -> str:
    """Extract basic page content"""
    # Wait for content to load
    sleep(wait_time)
    
    # Add random human-like delay
    sleep(random.uniform(1, 3))
    
    try:
        content = html2text(page.content())
        return content
    except Exception as e:
        return f"Content extraction error: {str(e)}"

def _scroll_and_extract(page, scroll_count: int, base_wait: int) -> str:
    """Scroll through infinite content and extract"""
    all_content = []
    
    for i in range(scroll_count):
        print(f"Scroll iteration {i+1}/{scroll_count}")
        
        # Scroll down to load more content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for new content to load with variation
        wait_time = base_wait + random.uniform(1, 4)
        sleep(wait_time)
        
        # Extract current content
        try:
            current_content = html2text(page.content())
            all_content.append(f"--- Scroll {i+1} ---\n{current_content}")
        except Exception as e:
            all_content.append(f"--- Scroll {i+1} Error ---\n{str(e)}")
    
    return "\n\n".join(all_content)

def _extract_posts(page, wait_time: int) -> str:
    """Extract posts with metadata"""
    sleep(wait_time)
    
    try:
        # Look for LinkedIn post selectors
        posts = page.query_selector_all('[data-urn*="activity"]')
        
        extracted_posts = []
        for i, post in enumerate(posts[:10]):  # Limit to first 10 posts
            try:
                post_text = post.text_content()
                post_html = post.inner_html()
                
                extracted_posts.append({
                    "post_index": i,
                    "text_preview": post_text[:200] + "..." if len(post_text) > 200 else post_text,
                    "has_reactions": "reactions" in post_html.lower(),
                    "has_comments": "comment" in post_html.lower()
                })
            except Exception as e:
                extracted_posts.append({"post_index": i, "error": str(e)})
        
        result = {
            "total_posts_found": len(posts),
            "extracted_posts": extracted_posts,
            "page_content": html2text(page.content())
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Post extraction error: {str(e)}\n\n{html2text(page.content())}"

def _extract_reactions(page, wait_time: int) -> str:
    """Extract reaction details from a post"""
    sleep(wait_time)
    
    try:
        # Wait for reactions modal or content to load
        page.wait_for_selector('[data-test-id*="reaction"]', timeout=10000)
        
        # Look for reaction elements
        reactions = page.query_selector_all('[data-test-id*="reaction"], .reactions-detail, .social-details-reactors')
        
        extracted_reactions = []
        for reaction in reactions:
            try:
                reaction_text = reaction.text_content()
                extracted_reactions.append(reaction_text)
            except:
                continue
        
        result = {
            "reactions_found": len(extracted_reactions),
            "reaction_details": extracted_reactions,
            "page_content": html2text(page.content())
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Reaction extraction error: {str(e)}\n\n{html2text(page.content())}"