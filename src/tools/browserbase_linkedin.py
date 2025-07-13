import os
import json
import random
from crewai_tools import tool
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from html2text import html2text
from time import sleep
from typing import Optional, Dict, Any
import sys
import asyncio
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))
from auth.linkedin_auth import LinkedInAuth, create_authenticated_browserbase_session

@tool("Authenticated LinkedIn Navigator")
def browserbase_linkedin(
    url: str, 
    action: str = "extract_content",
    wait_time: Optional[int] = None,
    scroll_count: int = 3,
    require_auth: bool = True
) -> str:
    """
    Navigates LinkedIn using Browserbase with authentication and stealth capabilities
    
    :param url: The LinkedIn URL to navigate to
    :param action: Action to perform - 'extract_content', 'extract_posts', 'extract_reactions', 'scroll_and_extract'
    :param wait_time: Custom wait time in seconds (default: intelligent based on action)
    :param scroll_count: Number of times to scroll for infinite scroll content
    :param require_auth: Whether to authenticate before navigation (default: True)
    :return: The extracted content as text or JSON
    """
    print(f"🚀 Navigating to LinkedIn: {url} with action: {action}")
    
    # Intelligent wait times based on action
    if wait_time is None:
        wait_times = {
            "extract_content": 5,
            "extract_posts": 10, 
            "extract_reactions": 8,
            "scroll_and_extract": 15
        }
        wait_time = wait_times.get(action, 7)
    
    # Use new event loop if not available
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(_authenticated_browse(url, action, wait_time, scroll_count, require_auth))

async def _authenticated_browse(url: str, action: str, wait_time: int, scroll_count: int, require_auth: bool) -> str:
    """Async LinkedIn browsing with authentication"""
    try:
        # Get authenticated Browserbase connection
        connect_url, session_config = create_authenticated_browserbase_session()
        
        async with async_playwright() as playwright:
            try:
                print("   🌐 Connecting to Browserbase with stealth mode...")
                browser = await playwright.chromium.connect_over_cdp(connect_url)
                
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page() if not context.pages else context.pages[0]
                
                # Set LinkedIn-optimized viewport
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Authenticate if required
                if require_auth:
                    auth = LinkedInAuth()
                    authenticated = await auth.authenticate(page, context)
                    if not authenticated:
                        return "❌ Authentication failed. Please check your LinkedIn credentials."
                
                # Navigate with error handling
                try:
                    print(f"   📄 Navigating to: {url}")
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                except Exception as e:
                    print(f"   ❌ Navigation error: {e}")
                    return f"Error navigating to {url}: {str(e)}"
                
                # Handle different actions
                if action == "scroll_and_extract":
                    return await _scroll_and_extract_async(page, scroll_count, wait_time)
                elif action == "extract_posts":
                    return await _extract_posts_async(page, wait_time)
                elif action == "extract_reactions":
                    return await _extract_reactions_async(page, wait_time)
                else:
                    # Default: extract_content
                    return await _extract_basic_content_async(page, wait_time)
                    
            except Exception as e:
                print(f"   ❌ Browser error: {e}")
                return f"Browser error: {str(e)}"
            finally:
                try:
                    await browser.close()
                except:
                    pass
                    
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return f"Connection error: {str(e)}"

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

# Async versions for authenticated browsing

async def _extract_basic_content_async(page, wait_time: int) -> str:
    """Extract basic page content (async)"""
    # Wait for content to load
    await asyncio.sleep(wait_time)
    
    # Add random human-like delay
    await asyncio.sleep(random.uniform(1, 3))
    
    try:
        content = await page.content()
        return html2text(content)
    except Exception as e:
        return f"Content extraction error: {str(e)}"

async def _scroll_and_extract_async(page, scroll_count: int, base_wait: int) -> str:
    """Scroll through infinite content and extract (async)"""
    all_content = []
    
    for i in range(scroll_count):
        print(f"   📜 Scroll iteration {i+1}/{scroll_count}")
        
        # Scroll down to load more content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for new content to load with variation
        wait_time = base_wait + random.uniform(1, 4)
        await asyncio.sleep(wait_time)
        
        # Extract current content
        try:
            current_content = await page.content()
            all_content.append(f"--- Scroll {i+1} ---\n{html2text(current_content)}")
        except Exception as e:
            all_content.append(f"--- Scroll {i+1} Error ---\n{str(e)}")
    
    return "\n\n".join(all_content)

async def _extract_posts_async(page, wait_time: int) -> str:
    """Extract posts with metadata (async)"""
    await asyncio.sleep(wait_time)
    
    try:
        # Look for LinkedIn post selectors
        posts = await page.query_selector_all('[data-urn*="activity"]')
        
        if not posts:
            # Try alternative selectors
            alternative_selectors = [
                '.feed-shared-update-v2',
                '.occludable-update',
                'article[data-id]',
                '.update-components-article',
                '[data-urn*="urn:li:activity"]'
            ]
            
            for selector in alternative_selectors:
                posts = await page.query_selector_all(selector)
                if posts:
                    print(f"   ✅ Found {len(posts)} posts using selector: {selector}")
                    break
        
        extracted_posts = []
        for i, post in enumerate(posts[:10]):  # Limit to first 10 posts
            try:
                post_text = await post.text_content()
                post_html = await post.inner_html()
                
                extracted_posts.append({
                    "post_index": i + 1,
                    "text_preview": post_text[:200] + "..." if len(post_text) > 200 else post_text,
                    "has_reactions": "reactions" in post_html.lower() or "liked" in post_html.lower(),
                    "has_comments": "comment" in post_html.lower(),
                    "has_shares": "share" in post_html.lower(),
                    "element_found": True
                })
            except Exception as e:
                extracted_posts.append({
                    "post_index": i + 1, 
                    "error": str(e),
                    "element_found": False
                })
        
        result = {
            "total_posts_found": len(posts),
            "extracted_posts": extracted_posts,
            "page_url": page.url,
            "extraction_method": "authenticated_async"
        }
        
        print(f"   📝 Extracted {len(extracted_posts)} posts")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        page_content = await page.content()
        return f"Post extraction error: {str(e)}\n\n{html2text(page_content)}"

async def _extract_reactions_async(page, wait_time: int) -> str:
    """Extract reaction details from a post (async)"""
    await asyncio.sleep(wait_time)
    
    try:
        # Wait for reactions modal or content to load
        await page.wait_for_selector('[data-test-id*="reaction"]', timeout=10000)
        
        # Look for reaction elements
        reaction_selectors = [
            '[data-test-id*="reaction"]', 
            '.reactions-detail', 
            '.social-details-reactors',
            '.social-action',
            '[aria-label*="reaction"]'
        ]
        
        all_reactions = []
        for selector in reaction_selectors:
            reactions = await page.query_selector_all(selector)
            for reaction in reactions:
                try:
                    reaction_text = await reaction.text_content()
                    if reaction_text and reaction_text.strip():
                        all_reactions.append({
                            "selector": selector,
                            "text": reaction_text.strip(),
                            "element_found": True
                        })
                except:
                    continue
        
        result = {
            "reactions_found": len(all_reactions),
            "reaction_details": all_reactions,
            "page_url": page.url,
            "extraction_method": "authenticated_async"
        }
        
        print(f"   💝 Extracted {len(all_reactions)} reactions")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        page_content = await page.content()
        return f"Reaction extraction error: {str(e)}\n\n{html2text(page_content)}"