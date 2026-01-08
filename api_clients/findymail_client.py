"""Findymail API client for email discovery."""

import httpx
from typing import Dict, Any, Optional, List
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)

FINDYMAIL_BASE_URL = "https://app.findymail.com/api"


class FindymailClient:
    """Client for Findymail API - email discovery from social handles."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.FINDYMAIL_API_KEY
        self.base_url = FINDYMAIL_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    def find_email(
        self,
        name: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        domain: Optional[str] = None,
        linkedin_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find email address from name and domain or LinkedIn URL.
        
        Args:
            name: Full name (or will be constructed from first_name + last_name)
            first_name: First name (used if name not provided)
            last_name: Last name (used if name not provided)
            domain: Company domain (required for name search)
            linkedin_url: LinkedIn profile URL (alternative to name+domain)
        
        Returns:
            Email discovery results
        """
        # Build full name if not provided
        if not name and first_name:
            name = f"{first_name} {last_name or ''}".strip()
        
        # Use LinkedIn endpoint if LinkedIn URL provided
        if linkedin_url:
            url = f"{self.base_url}/search/linkedin"
            payload = {"linkedin_url": linkedin_url}
        else:
            url = f"{self.base_url}/search/name"
            payload = {"name": name, "domain": domain}
        
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
    
    def find_from_linkedin(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Find email from a LinkedIn profile URL.
        
        Args:
            linkedin_url: LinkedIn profile URL
        
        Returns:
            Email discovery results
        """
        return self.find_email(linkedin_url=linkedin_url)
    
    def find_from_name_domain(self, name: str, domain: str) -> Dict[str, Any]:
        """
        Find email from a person's name and company domain.
        
        Args:
            name: Full name
            domain: Company domain
        
        Returns:
            Email discovery results
        """
        return self.find_email(name=name, domain=domain)

