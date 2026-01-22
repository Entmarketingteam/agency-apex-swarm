"""Perplexity API client for research and real-time information."""

import httpx
import re
from typing import Dict, Any, Optional
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)

PERPLEXITY_BASE_URL = "https://api.perplexity.ai"


class PerplexityClient:
    """Client for Perplexity Pro API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.PERPLEXITY_API_KEY
        self.base_url = PERPLEXITY_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    def search(
        self,
        query: str,
        model: str = "sonar"
    ) -> Dict[str, Any]:
        """
        Search for real-time information using Perplexity.
        
        Args:
            query: Search query
            model: Model to use (default: sonar-large for real-time)
        
        Returns:
            Search results with citations
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful research assistant. Provide accurate, up-to-date information with citations."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Perplexity search completed: {query[:50]}...")
                return {
                    "content": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "citations": data.get("citations", []),
                    "model": data.get("model", ""),
                    "usage": data.get("usage", {})
                }
        except httpx.HTTPError as e:
            logger.error(f"Perplexity API error: {e}")
            raise
    
    def research_creator(self, creator_name: str, platform: str = "instagram") -> Dict[str, Any]:
        """
        Research a specific creator for lead generation.
        
        Args:
            creator_name: Name or handle of the creator
            platform: Platform to research (instagram, tiktok, etc.)
        
        Returns:
            Research data about the creator
        """
        query = f"Find recent information about {creator_name} on {platform}. Include follower count, engagement rate, content style, brand partnerships, and recent activity."
        
        return self.search(query)
    
    def get_instagram_bio(self, handle: str) -> Dict[str, Any]:
        """
        Get Instagram bio and profile information for a specific handle.
        
        Args:
            handle: Instagram handle (without @)
        
        Returns:
            Dict with bio, email (if in bio), follower count, and other profile data
        """
        # Remove @ if present
        clean_handle = handle.lstrip("@")
        
        query = f"What is the Instagram bio text for @{clean_handle}? Include the exact bio text, any email addresses mentioned in the bio, follower count, and profile description. Format: Bio: [exact text], Email: [if found], Followers: [count]"
        
        result = self.search(query)
        
        # Extract structured data from Perplexity response
        content = result.get("content", "")
        
        # Try to extract bio text
        bio = ""
        email_in_bio = None
        follower_count = None
        
        # Look for "Bio:" pattern
        bio_match = re.search(r'[Bb]io[:\s]+(.+?)(?:[Ee]mail|$)', content, re.DOTALL)
        if bio_match:
            bio = bio_match.group(1).strip()
            # Clean up common prefixes
            bio = re.sub(r'^[:\-\s]+', '', bio)
            bio = bio.split('\n')[0]  # Take first line if multiple
        
        # Extract email from bio or content
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, content)
        if email_matches:
            email_in_bio = email_matches[0]
        
        # Extract follower count
        follower_match = re.search(r'[Ff]ollowers?[:\s]+([\d,]+[KMB]?)', content)
        if follower_match:
            count_str = follower_match.group(1).replace(',', '')
            if count_str.endswith('K'):
                follower_count = int(float(count_str[:-1]) * 1000)
            elif count_str.endswith('M'):
                follower_count = int(float(count_str[:-1]) * 1000000)
            elif count_str.endswith('B'):
                follower_count = int(float(count_str[:-1]) * 1000000000)
            else:
                try:
                    follower_count = int(count_str)
                except:
                    pass
        
        return {
            "content": content,
            "bio": bio[:500] if bio else "",  # Limit length
            "email_in_bio": email_in_bio,
            "follower_count": follower_count,
            "citations": result.get("citations", []),
            "raw": result
        }


