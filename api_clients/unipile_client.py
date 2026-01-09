"""Unipile API client for LinkedIn DM automation."""

import httpx
import os
from typing import Dict, Any, Optional
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)


class UnipileClient:
    """Client for Unipile API - LinkedIn messaging.
    
    Note: Unipile requires a DSN (Data Source Name) specific to your account.
    Set UNIPILE_DSN environment variable to your DSN from the Unipile dashboard.
    Example: api1.unipile.com or your-custom-dsn.unipile.com
    """
    
    def __init__(self, api_key: Optional[str] = None, dsn: Optional[str] = None):
        self.api_key = api_key or config.UNIPILE_API_KEY
        self.dsn = dsn or os.getenv("UNIPILE_DSN", "api1.unipile.com")
        self.base_url = f"https://{self.dsn}"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "accept": "application/json"
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
        url = f"{self.base_url}/api/v1/chats"
        
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
    
    def list_accounts(self) -> Dict[str, Any]:
        """List connected accounts to verify API connection."""
        url = f"{self.base_url}/api/v1/accounts"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Unipile: Listed accounts successfully")
                return {
                    "success": True,
                    "accounts": data.get("items", data) if isinstance(data, dict) else data
                }
        except httpx.HTTPError as e:
            logger.error(f"Unipile API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "accounts": []
            }


