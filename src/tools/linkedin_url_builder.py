from crewai_tools import tool
from typing import Optional
import urllib.parse

@tool("LinkedIn URL Builder")
def linkedin_url_builder(
    profile_url: str, 
    action: str = "posts",
    days_back: int = 30,
    post_id: Optional[str] = None
) -> str:
    """
    Generates LinkedIn URLs for different actions like viewing posts, reactions, etc.
    
    :param profile_url: The LinkedIn profile URL (e.g., 'https://linkedin.com/in/username')
    :param action: The action to perform - 'posts', 'activity', 'post_reactions', 'post_detail'
    :param days_back: Number of days to look back for posts (default: 30)
    :param post_id: Specific post ID for reaction details (required for 'post_reactions' action)
    :return: The LinkedIn URL for the specified action
    """
    print(f"Building LinkedIn URL for {action} on profile {profile_url}")
    
    # Extract username from profile URL
    if '/in/' in profile_url:
        username = profile_url.split('/in/')[-1].rstrip('/')
    else:
        raise ValueError("Invalid LinkedIn profile URL format")
    
    base_profile = f"https://www.linkedin.com/in/{username}"
    
    if action == "posts":
        # Navigate to user's posts/activity feed
        return f"{base_profile}/recent-activity/all/"
    
    elif action == "activity": 
        # Alternative activity view
        return f"{base_profile}/detail/recent-activity/"
    
    elif action == "post_reactions":
        if not post_id:
            raise ValueError("post_id required for post_reactions action")
        # URL to view reactions on a specific post
        return f"https://www.linkedin.com/feed/update/{post_id}/reactions/"
    
    elif action == "post_detail":
        if not post_id:
            raise ValueError("post_id required for post_detail action") 
        # URL to view full post details
        return f"https://www.linkedin.com/feed/update/{post_id}/"
    
    else:
        # Default to profile page
        return base_profile