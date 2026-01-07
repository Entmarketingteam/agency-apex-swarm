"""Unipile API client for LinkedIn DM automation."""

import httpx
from typing import Dict, Any, Optional
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)

UNIPILE_BASE_URL = "https://api.unipile.com"


class UnipileClient:
    """Client for Unipile API - LinkedIn messaging."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.UNIPILE_API_KEY
        self.base_url = UNIPILE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    def send_dm(
        self,
        linkedin_url: str,
        message: str,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a LinkedIn DM.
        
        Args:
            linkedin_url: LinkedIn profile URL of recipient
            message: Message content
            account_id: Unipile account ID (if multiple accounts)
        
        Returns:
            Message sending result
        """
        url = f"{self.base_url}/v1/messages"
        
        payload = {
            "recipient_url": linkedin_url,
            "message": message
        }
        
        if account_id:
            payload["account_id"] = account_id
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Unipile DM sent to {linkedin_url}")
                return {
                    "success": True,
                    "message_id": data.get("id", ""),
                    "status": data.get("status", "sent"),
                    "timestamp": data.get("created_at", "")
                }
        except httpx.HTTPError as e:
            logger.error(f"Unipile API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message_id": None
            }

