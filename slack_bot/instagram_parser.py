"""Instagram URL and handle parser."""

import re
from typing import Optional, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


# Regex patterns for Instagram URLs and handles
INSTAGRAM_PATTERNS = [
    # Full URLs
    r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)/?(?:\?.*)?',
    # Post URLs (extract username)
    r'(?:https?://)?(?:www\.)?instagram\.com/p/[a-zA-Z0-9_-]+/?',
    # Reel URLs
    r'(?:https?://)?(?:www\.)?instagram\.com/reel/[a-zA-Z0-9_-]+/?',
    # Story URLs
    r'(?:https?://)?(?:www\.)?instagram\.com/stories/([a-zA-Z0-9_.]+)/',
    # Just handle with @
    r'@([a-zA-Z0-9_.]+)',
]


def extract_instagram_handle(text: str) -> Optional[str]:
    """
    Extract Instagram handle from various URL formats or @mention.
    
    Supported formats:
    - https://instagram.com/username
    - https://www.instagram.com/username/
    - https://instagram.com/username?igsh=...
    - https://instagram.com/p/POST_ID (requires API lookup)
    - https://instagram.com/reel/REEL_ID
    - https://instagram.com/stories/username/
    - @username
    
    Args:
        text: Text containing Instagram URL or handle
        
    Returns:
        Extracted handle (without @) or None
    """
    if not text:
        return None
    
    text = text.strip()
    
    # Pattern 1: Profile URL - instagram.com/username
    profile_pattern = r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)/?(?:\?.*)?$'
    match = re.search(profile_pattern, text)
    if match:
        handle = match.group(1)
        # Filter out non-profile paths
        if handle.lower() not in ['p', 'reel', 'reels', 'stories', 'explore', 'direct', 'accounts']:
            logger.info(f"Extracted handle from profile URL: {handle}")
            return handle
    
    # Pattern 2: Stories URL - instagram.com/stories/username/
    stories_pattern = r'(?:https?://)?(?:www\.)?instagram\.com/stories/([a-zA-Z0-9_.]+)/'
    match = re.search(stories_pattern, text)
    if match:
        handle = match.group(1)
        logger.info(f"Extracted handle from stories URL: {handle}")
        return handle
    
    # Pattern 3: @ mention
    mention_pattern = r'@([a-zA-Z0-9_.]+)'
    match = re.search(mention_pattern, text)
    if match:
        handle = match.group(1)
        logger.info(f"Extracted handle from @mention: {handle}")
        return handle
    
    # Pattern 4: Just the username (alphanumeric with dots/underscores)
    if re.match(r'^[a-zA-Z0-9_.]+$', text) and len(text) <= 30:
        logger.info(f"Treating as raw handle: {text}")
        return text
    
    logger.warning(f"Could not extract Instagram handle from: {text}")
    return None


def parse_instagram_url(url: str) -> Dict[str, Any]:
    """
    Parse Instagram URL and extract all available information.
    
    Args:
        url: Instagram URL
        
    Returns:
        Dictionary with parsed information
    """
    result = {
        "original_url": url,
        "handle": None,
        "url_type": None,
        "post_id": None,
        "is_valid": False
    }
    
    url = url.strip()
    
    # Check if it's an Instagram URL
    if 'instagram.com' not in url.lower() and not url.startswith('@'):
        return result
    
    # Profile URL
    profile_match = re.search(
        r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)/?(?:\?.*)?$',
        url
    )
    if profile_match:
        handle = profile_match.group(1)
        if handle.lower() not in ['p', 'reel', 'reels', 'stories', 'explore']:
            result["handle"] = handle
            result["url_type"] = "profile"
            result["is_valid"] = True
            return result
    
    # Post URL
    post_match = re.search(
        r'(?:https?://)?(?:www\.)?instagram\.com/p/([a-zA-Z0-9_-]+)',
        url
    )
    if post_match:
        result["post_id"] = post_match.group(1)
        result["url_type"] = "post"
        result["is_valid"] = True
        # Note: Handle extraction from post requires API call
        return result
    
    # Reel URL
    reel_match = re.search(
        r'(?:https?://)?(?:www\.)?instagram\.com/reel/([a-zA-Z0-9_-]+)',
        url
    )
    if reel_match:
        result["post_id"] = reel_match.group(1)
        result["url_type"] = "reel"
        result["is_valid"] = True
        return result
    
    # Stories URL
    stories_match = re.search(
        r'(?:https?://)?(?:www\.)?instagram\.com/stories/([a-zA-Z0-9_.]+)/',
        url
    )
    if stories_match:
        result["handle"] = stories_match.group(1)
        result["url_type"] = "stories"
        result["is_valid"] = True
        return result
    
    # @ mention
    if url.startswith('@'):
        mention_match = re.match(r'@([a-zA-Z0-9_.]+)', url)
        if mention_match:
            result["handle"] = mention_match.group(1)
            result["url_type"] = "mention"
            result["is_valid"] = True
            return result
    
    return result


def validate_instagram_handle(handle: str) -> bool:
    """
    Validate Instagram handle format.
    
    Rules:
    - 1-30 characters
    - Only letters, numbers, periods, underscores
    - Cannot start/end with period
    - Cannot have consecutive periods
    
    Args:
        handle: Instagram handle to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not handle:
        return False
    
    # Length check
    if len(handle) < 1 or len(handle) > 30:
        return False
    
    # Character check
    if not re.match(r'^[a-zA-Z0-9_.]+$', handle):
        return False
    
    # Cannot start or end with period
    if handle.startswith('.') or handle.endswith('.'):
        return False
    
    # Cannot have consecutive periods
    if '..' in handle:
        return False
    
    return True


def find_all_instagram_urls(text: str) -> list:
    """
    Find all Instagram URLs/handles in a block of text.
    
    Args:
        text: Text to search
        
    Returns:
        List of extracted handles
    """
    handles = set()
    
    # Find profile URLs
    profile_matches = re.findall(
        r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_.]+)/?(?:\?[^\s]*)?',
        text
    )
    for match in profile_matches:
        if match.lower() not in ['p', 'reel', 'reels', 'stories', 'explore', 'direct']:
            if validate_instagram_handle(match):
                handles.add(match)
    
    # Find @ mentions
    mention_matches = re.findall(r'@([a-zA-Z0-9_.]+)', text)
    for match in mention_matches:
        if validate_instagram_handle(match):
            handles.add(match)
    
    # Find stories URLs
    stories_matches = re.findall(
        r'instagram\.com/stories/([a-zA-Z0-9_.]+)/',
        text
    )
    for match in stories_matches:
        if validate_instagram_handle(match):
            handles.add(match)
    
    return list(handles)

