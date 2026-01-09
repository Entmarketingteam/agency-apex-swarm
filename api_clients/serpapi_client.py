"""SerpAPI client for multi-platform creator prospecting searches."""

import os
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import re

import httpx

from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)

SERPAPI_BASE_URL = "https://serpapi.com/search"


class SerpAPIClient:
    """
    Client for SerpAPI Google Search.
    
    Searches for creator profiles across TikTok, Twitter, Instagram with
    visible email addresses for prospecting.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_enabled: bool = True,
        cache_ttl_hours: int = 24
    ):
        """
        Initialize SerpAPI client.
        
        Args:
            api_key: SerpAPI key (defaults to SERPAPI_KEY from config)
            cache_enabled: Whether to cache search results
            cache_ttl_hours: How long to cache results
        """
        self.api_key = api_key or config.SERPAPI_KEY
        if not self.api_key:
            logger.warning("SERPAPI_KEY not configured - searches will fail")
        
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl_hours * 3600
        self.cache_file = Path.home() / ".serpapi_cache.json"
        
        # Usage tracking
        self.requests_today = 0
        self.requests_this_month = 0
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from disk."""
        if self.cache_enabled and self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self._cache = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self._cache = {}
        else:
            self._cache = {}
    
    def _save_cache(self):
        """Save cache to disk."""
        if self.cache_enabled:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(self._cache, f)
            except Exception as e:
                logger.warning(f"Failed to save cache: {e}")
    
    def _cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry:
            return False
        cached_time = cache_entry.get("timestamp", 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    def search(
        self,
        query: str,
        num_results: int = 20,
        skip_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a Google search via SerpAPI.
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 100)
            skip_cache: Force fresh search even if cached
        
        Returns:
            Dict with search results and metadata
        """
        # Check cache first
        cache_key = self._cache_key(query)
        if self.cache_enabled and not skip_cache:
            if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]):
                logger.info(f"Cache hit for query: {query[:50]}...")
                return self._cache[cache_key]["data"]
        
        # Execute search
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": min(num_results, 100),
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(SERPAPI_BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Track usage
                self.requests_today += 1
                self.requests_this_month += 1
                
                # Extract relevant data
                result = {
                    "query": query,
                    "organic_results": data.get("organic_results", []),
                    "total_results": data.get("search_information", {}).get("total_results", 0),
                    "search_time": data.get("search_information", {}).get("time_taken_displayed", 0),
                    "credits_used": 1,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Cache results
                if self.cache_enabled:
                    self._cache[cache_key] = {
                        "data": result,
                        "timestamp": time.time()
                    }
                    self._save_cache()
                
                logger.info(f"SerpAPI search completed: {len(result['organic_results'])} results")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"SerpAPI request failed: {e}")
            raise
    
    def search_creators(
        self,
        platform: str = "tiktok",
        hashtags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        email_domains: Optional[List[str]] = None,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search for creators with visible email addresses.
        
        Args:
            platform: Platform to search (tiktok, twitter, instagram, youtube)
            hashtags: Hashtags to filter by (e.g., ["LTK", "amazonfinds"])
            keywords: Keywords to filter by (e.g., ["wellness", "fitness"])
            email_domains: Email domains to look for (default: gmail)
            max_results: Maximum results to return
        
        Returns:
            Search results with creator profiles
        """
        query_string = self._build_creator_query(
            platform=platform,
            hashtags=hashtags or [],
            keywords=keywords or [],
            email_domains=email_domains or ["gmail.com"]
        )
        
        logger.info(f"Searching creators with query: {query_string}")
        return self.search(query_string, num_results=max_results)
    
    def _build_creator_query(
        self,
        platform: str,
        hashtags: List[str],
        keywords: List[str],
        email_domains: List[str]
    ) -> str:
        """Build Google search query for creator prospecting."""
        parts = []
        
        # Platform site restriction
        site_map = {
            "tiktok": "site:tiktok.com",
            "twitter": "site:twitter.com OR site:x.com",
            "instagram": "site:instagram.com",
            "youtube": "site:youtube.com",
        }
        parts.append(site_map.get(platform.lower(), "site:tiktok.com"))
        
        # Email domain filter
        if email_domains:
            email_parts = [f'"@{domain}"' for domain in email_domains]
            if len(email_parts) == 1:
                parts.append(email_parts[0])
            else:
                parts.append(f"({' OR '.join(email_parts)})")
        
        # Hashtag filter
        if hashtags:
            hashtag_parts = [f'"#{tag.lstrip("#")}"' for tag in hashtags]
            if len(hashtag_parts) == 1:
                parts.append(hashtag_parts[0])
            else:
                parts.append(f"({' OR '.join(hashtag_parts)})")
        
        # Keyword filter
        if keywords:
            keyword_parts = [f'"{kw}"' for kw in keywords]
            if len(keyword_parts) == 1:
                parts.append(keyword_parts[0])
            else:
                parts.append(f"({' OR '.join(keyword_parts)})")
        
        return " ".join(parts)
    
    def search_tiktok_creators(
        self,
        hashtags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        email_domain: str = "gmail.com",
        max_results: int = 20
    ) -> Dict[str, Any]:
        """Convenience method for TikTok creator search."""
        return self.search_creators(
            platform="tiktok",
            hashtags=hashtags,
            keywords=keywords,
            email_domains=[email_domain],
            max_results=max_results
        )
    
    def search_twitter_creators(
        self,
        hashtags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        email_domain: str = "gmail.com",
        max_results: int = 20
    ) -> Dict[str, Any]:
        """Convenience method for Twitter/X creator search."""
        return self.search_creators(
            platform="twitter",
            hashtags=hashtags,
            keywords=keywords,
            email_domains=[email_domain],
            max_results=max_results
        )
    
    def search_instagram_creators(
        self,
        hashtags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        email_domain: str = "gmail.com",
        max_results: int = 20
    ) -> Dict[str, Any]:
        """Convenience method for Instagram creator search."""
        return self.search_creators(
            platform="instagram",
            hashtags=hashtags,
            keywords=keywords,
            email_domains=[email_domain],
            max_results=max_results
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current API usage statistics."""
        return {
            "requests_today": self.requests_today,
            "requests_this_month": self.requests_this_month,
            "cache_enabled": self.cache_enabled,
            "cache_entries": len(self._cache),
        }
    
    def clear_cache(self):
        """Clear the search cache."""
        self._cache = {}
        self._save_cache()
        logger.info("SerpAPI cache cleared")


class QueryParser:
    """Parse natural language queries into search parameters."""
    
    PLATFORM_PATTERNS = {
        "tiktok": ["tiktok", "tik tok", "tt"],
        "twitter": ["twitter", "x", "tweet"],
        "instagram": ["instagram", "ig", "insta"],
        "youtube": ["youtube", "yt"],
    }
    
    EMAIL_PATTERNS = {
        "gmail": "gmail.com",
        "yahoo": "yahoo.com",
        "outlook": "outlook.com",
        "hotmail": "hotmail.com",
    }
    
    @classmethod
    def parse(cls, query: str) -> Dict[str, Any]:
        """
        Parse natural language query into search parameters.
        
        Examples:
            "Find TikTok wellness creators with gmail who post #LTK"
            "Search for fitness creators on Instagram"
        """
        query_lower = query.lower()
        
        # Detect platform
        platform = "tiktok"
        for plat, patterns in cls.PLATFORM_PATTERNS.items():
            if any(p in query_lower for p in patterns):
                platform = plat
                break
        
        # Detect email domain
        email_domain = "gmail.com"
        for domain_key, domain in cls.EMAIL_PATTERNS.items():
            if domain_key in query_lower:
                email_domain = domain
                break
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', query)
        
        # Extract keywords
        niche_keywords = [
            "wellness", "fitness", "health", "beauty", "skincare", "makeup",
            "fashion", "lifestyle", "mom", "parenting", "food", "travel",
            "tech", "gaming", "supplements", "nutrition", "workout", "yoga",
            "meditation", "mindfulness", "amazon", "ltk", "affiliate"
        ]
        keywords = [kw for kw in niche_keywords if kw in query_lower]
        
        # Detect max results
        max_results = 20
        number_match = re.search(r'(\d+)\s*(creators?|results?|prospects?)', query_lower)
        if number_match:
            max_results = min(int(number_match.group(1)), 100)
        
        return {
            "platform": platform,
            "hashtags": hashtags,
            "keywords": keywords,
            "email_domain": email_domain,
            "max_results": max_results
        }


def search_from_natural_language(query: str) -> Dict[str, Any]:
    """
    Execute search from natural language query.
    
    Example:
        search_from_natural_language("Find 20 TikTok wellness creators with gmail")
    """
    params = QueryParser.parse(query)
    client = SerpAPIClient()
    
    return client.search_creators(
        platform=params["platform"],
        hashtags=params["hashtags"],
        keywords=params["keywords"],
        email_domains=[params["email_domain"]],
        max_results=params["max_results"]
    )
