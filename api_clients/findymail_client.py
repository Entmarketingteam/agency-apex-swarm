"""Findymail API client for email discovery."""

import httpx
from typing import Dict, Any, Optional, List
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)

FINDYMAIL_BASE_URL = "https://api.findymail.com"


class FindymailClient:
    """Client for Findymail API - email discovery from social handles."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.FINDYMAIL_API_KEY
        self.base_url = FINDYMAIL_BASE_URL
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    def find_email(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        domain: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        twitter_handle: Optional[str] = None,
        instagram_handle: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find email address from various identifiers.
        
        Args:
            first_name: First name
            last_name: Last name
            domain: Company domain
            linkedin_url: LinkedIn profile URL
            twitter_handle: Twitter/X handle
            instagram_handle: Instagram handle
        
        Returns:
            Email discovery results
        """
        url = f"{self.base_url}/api/v1/email-finder"
        
        payload = {}
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        if domain:
            payload["domain"] = domain
        if linkedin_url:
            payload["linkedin_url"] = linkedin_url
        if twitter_handle:
            payload["twitter_handle"] = twitter_handle
        if instagram_handle:
            payload["instagram_handle"] = instagram_handle
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Findymail email discovery completed")
                return {
                    "email": data.get("email", ""),
                    "confidence": data.get("confidence", 0),
                    "sources": data.get("sources", []),
                    "status": data.get("status", "unknown")
                }
        except httpx.HTTPError as e:
            logger.error(f"Findymail API error: {e}")
            raise
    
    def find_from_handle(self, handle: str, platform: str = "instagram") -> Dict[str, Any]:
        """
        Find email from a social media handle.
        
        Args:
            handle: Social media handle
            platform: Platform (instagram, twitter, etc.)
        
        Returns:
            Email discovery results
        """
        if platform.lower() == "instagram":
            return self.find_email(instagram_handle=handle)
        elif platform.lower() in ["twitter", "x"]:
            return self.find_email(twitter_handle=handle)
        else:
            logger.warning(f"Unsupported platform for email discovery: {platform}")
            return {"email": None, "confidence": 0, "sources": [], "status": "unsupported_platform"}

