"""Profile scraper for extracting emails and metadata from search results."""

import re
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from urllib.parse import urlparse

import httpx

from utils.logger import get_logger

logger = get_logger(__name__)

# Email regex pattern - matches common email formats
EMAIL_REGEX = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    re.IGNORECASE
)

# Hashtag regex pattern
HASHTAG_REGEX = re.compile(r'#(\w+)', re.UNICODE)

# Common spam/invalid email patterns to filter out
SPAM_EMAIL_PATTERNS = [
    r'.*@example\.com$',
    r'.*@test\.com$',
    r'.*noreply.*',
    r'.*no-reply.*',
    r'support@.*',
    r'info@.*',
    r'contact@.*',
    r'admin@.*',
]


def extract_email_from_text(text: str) -> Optional[str]:
    """
    Extract the first valid email address from text.
    
    Args:
        text: Text to search for email
    
    Returns:
        First valid email found, or None
    """
    if not text:
        return None
    
    matches = EMAIL_REGEX.findall(text)
    
    for email in matches:
        email_lower = email.lower()
        # Filter out spam/invalid patterns
        is_spam = any(
            re.match(pattern, email_lower) 
            for pattern in SPAM_EMAIL_PATTERNS
        )
        if not is_spam:
            return email.lower()
    
    return None


def extract_hashtags_from_text(text: str) -> List[str]:
    """
    Extract all hashtags from text.
    
    Args:
        text: Text to search for hashtags
    
    Returns:
        List of hashtags (without # prefix)
    """
    if not text:
        return []
    
    return list(set(HASHTAG_REGEX.findall(text)))


def extract_username_from_url(url: str, platform: str) -> Optional[str]:
    """
    Extract username from profile URL.
    
    Args:
        url: Profile URL
        platform: Platform name (tiktok, twitter, instagram)
    
    Returns:
        Username without @ prefix, or None
    """
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if platform.lower() == "tiktok":
            # TikTok: tiktok.com/@username or tiktok.com/@username/video/...
            if path.startswith('@'):
                username = path.split('/')[0]
                return username.lstrip('@')
        
        elif platform.lower() in ("twitter", "x"):
            # Twitter: twitter.com/username or x.com/username
            parts = path.split('/')
            if parts and parts[0] not in ['search', 'hashtag', 'i', 'intent']:
                return parts[0]
        
        elif platform.lower() == "instagram":
            # Instagram: instagram.com/username or instagram.com/p/...
            parts = path.split('/')
            if parts and parts[0] not in ['p', 'reel', 'stories', 'explore']:
                return parts[0]
        
        elif platform.lower() == "youtube":
            # YouTube: youtube.com/@username or youtube.com/channel/...
            if path.startswith('@'):
                return path.split('/')[0].lstrip('@')
            elif path.startswith('channel/'):
                return path.split('/')[1] if len(path.split('/')) > 1 else None
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to parse URL {url}: {e}")
        return None


class ProfileScraper:
    """
    Scrapes social media profiles for emails and metadata.
    
    Extracts information from SerpAPI search results and optionally
    fetches additional data from profile pages.
    """
    
    def __init__(self, rate_limit_per_second: float = 1.0):
        """
        Initialize scraper.
        
        Args:
            rate_limit_per_second: Max requests per second for scraping
        """
        self.rate_limit = rate_limit_per_second
        self._last_request_time = 0
    
    async def _respect_rate_limit(self):
        """Wait if necessary to respect rate limit."""
        import time
        now = time.time()
        elapsed = now - self._last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        
        self._last_request_time = time.time()
    
    def extract_from_search_result(
        self,
        result: Dict[str, Any],
        platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract prospect data from a single SerpAPI search result.
        
        Args:
            result: Single organic result from SerpAPI
            platform: Platform being searched
        
        Returns:
            Dict with extracted data, or None if no email found
        """
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        
        # Combine text sources for email extraction
        combined_text = f"{title} {snippet}"
        
        # Extract email
        email = extract_email_from_text(combined_text)
        if not email:
            return None
        
        # Extract username
        username = extract_username_from_url(link, platform)
        if not username:
            # Try to extract from title
            username_match = re.search(r'@(\w+)', title)
            if username_match:
                username = username_match.group(1)
            else:
                username = email.split('@')[0]  # Fallback to email prefix
        
        # Extract hashtags
        hashtags = extract_hashtags_from_text(combined_text)
        
        # Clean bio (use snippet as bio)
        bio = snippet[:500] if snippet else ""
        
        return {
            "platform": platform.lower(),
            "username": username,
            "profile_url": link,
            "email": email,
            "bio": bio,
            "hashtags": hashtags,
            "found_date": datetime.now().isoformat(),
        }
    
    def process_search_results(
        self,
        search_results: Dict[str, Any],
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Process all search results and extract prospect data.
        
        Args:
            search_results: Full SerpAPI response
            platform: Platform that was searched
        
        Returns:
            List of extracted prospect data dicts
        """
        prospects = []
        organic_results = search_results.get("organic_results", [])
        seen_emails = set()
        
        for result in organic_results:
            try:
                extracted = self.extract_from_search_result(result, platform)
                if extracted and extracted["email"] not in seen_emails:
                    extracted["search_query"] = search_results.get("query", "")
                    prospects.append(extracted)
                    seen_emails.add(extracted["email"])
            except Exception as e:
                logger.warning(f"Failed to process result: {e}")
                continue
        
        logger.info(f"Extracted {len(prospects)} prospects from {len(organic_results)} results")
        return prospects
    
    async def scrape_profile_page(
        self,
        url: str,
        platform: str
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape additional data from a profile page.
        
        Note: This makes an actual HTTP request to the profile page.
        Use sparingly to avoid rate limiting.
        
        Args:
            url: Profile URL to scrape
            platform: Platform type
        
        Returns:
            Additional profile data, or None on failure
        """
        await self._respect_rate_limit()
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    return None
                
                html = response.text
                
                # Extract email from page
                email = extract_email_from_text(html)
                
                # Extract hashtags
                hashtags = extract_hashtags_from_text(html)
                
                # Try to extract follower count (platform-specific)
                follower_count = self._extract_follower_count(html, platform)
                
                return {
                    "email": email,
                    "hashtags": hashtags,
                    "follower_count": follower_count,
                }
                
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return None
    
    def _extract_follower_count(self, html: str, platform: str) -> Optional[int]:
        """
        Try to extract follower count from page HTML.
        
        This is best-effort and may not always work.
        """
        try:
            # Common patterns for follower counts
            patterns = [
                r'"followerCount"[:\s]+(\d+)',
                r'"followers_count"[:\s]+(\d+)',
                r'(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)\s*[Ff]ollowers',
                r'[Ff]ollowers[:\s]+(\d+(?:,\d+)*(?:\.\d+)?[KMB]?)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    count_str = match.group(1).replace(',', '')
                    
                    # Handle K/M/B suffixes
                    if count_str.endswith('K'):
                        return int(float(count_str[:-1]) * 1000)
                    elif count_str.endswith('M'):
                        return int(float(count_str[:-1]) * 1000000)
                    elif count_str.endswith('B'):
                        return int(float(count_str[:-1]) * 1000000000)
                    else:
                        return int(count_str)
            
            return None
            
        except Exception:
            return None
    
    async def enrich_prospects(
        self,
        prospects: List[Dict[str, Any]],
        scrape_pages: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Enrich prospect data with additional information.
        
        Args:
            prospects: List of prospect dicts
            scrape_pages: Whether to scrape profile pages for more data
        
        Returns:
            Enriched prospect list
        """
        enriched = []
        
        for prospect in prospects:
            # Derive Instagram username from other platform username
            if prospect.get("platform") != "instagram" and prospect.get("username"):
                prospect["instagram_username"] = prospect["username"]
            
            # Optionally scrape profile page
            if scrape_pages and prospect.get("profile_url"):
                extra_data = await self.scrape_profile_page(
                    prospect["profile_url"],
                    prospect["platform"]
                )
                if extra_data:
                    # Update with scraped data (don't overwrite existing)
                    if extra_data.get("follower_count"):
                        prospect["follower_count"] = extra_data["follower_count"]
                    if extra_data.get("hashtags"):
                        existing = set(prospect.get("hashtags", []))
                        existing.update(extra_data["hashtags"])
                        prospect["hashtags"] = list(existing)
            
            enriched.append(prospect)
        
        return enriched


# Convenience functions
async def scrape_creators_from_search(
    search_results: Dict[str, Any],
    platform: str,
    enrich: bool = False
) -> List[Dict[str, Any]]:
    """
    Extract and optionally enrich creators from search results.
    
    Args:
        search_results: SerpAPI search response
        platform: Platform searched
        enrich: Whether to scrape profile pages for more data
    
    Returns:
        List of prospect data dicts
    """
    scraper = ProfileScraper()
    prospects = scraper.process_search_results(search_results, platform)
    
    if enrich:
        prospects = await scraper.enrich_prospects(prospects, scrape_pages=True)
    
    return prospects
