"""
Authentication module for ReactionReach
Handles LinkedIn authentication with Browserbase stealth mode
"""

from .linkedin_auth import LinkedInAuth, create_authenticated_browserbase_session

__all__ = ["LinkedInAuth", "create_authenticated_browserbase_session"]