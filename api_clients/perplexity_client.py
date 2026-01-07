"""Perplexity API client for research and real-time information."""

import httpx
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
        model: str = "llama-3.1-sonar-large-128k-online"
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

