"""Smartlead API client for email automation."""

import httpx
from typing import Dict, Any, Optional, List
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)

SMARTLEAD_BASE_URL = "https://server.smartlead.ai/api/v1"


class SmartleadClient:
    """Client for Smartlead API - email campaign automation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.SMARTLEAD_API_KEY
        self.base_url = SMARTLEAD_BASE_URL
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def _url_with_key(self, endpoint: str) -> str:
        """Add API key as query parameter."""
        separator = "&" if "?" in endpoint else "?"
        return f"{self.base_url}/{endpoint}{separator}api_key={self.api_key}"
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    def create_campaign(
        self,
        campaign_name: str,
        email_subject: str,
        email_body: str,
        sender_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an email campaign.
        
        Args:
            campaign_name: Name of the campaign
            email_subject: Email subject line
            email_body: Email body content
            sender_email: Sender email address
        
        Returns:
            Campaign creation result
        """
        url = self._url_with_key("campaigns/create")
        
        payload = {
            "name": campaign_name
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Smartlead campaign created: {campaign_name}")
                return {
                    "success": True,
                    "campaign_id": data.get("campaign_id", ""),
                    "campaign_name": campaign_name
                }
        except httpx.HTTPError as e:
            logger.error(f"Smartlead API error: {e}")
            raise
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(httpx.HTTPError,))
    def add_leads_to_campaign(
        self,
        campaign_id: str,
        leads: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Add leads to a campaign.
        
        Args:
            campaign_id: Campaign ID
            leads: List of leads with email and optional variables
        
        Returns:
            Lead addition result
        """
        url = self._url_with_key(f"campaigns/{campaign_id}/leads")
        
        payload = {
            "lead_list": leads
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Added {len(leads)} leads to campaign {campaign_id}")
                return {
                    "success": True,
                    "added_count": len(leads),
                    "campaign_id": campaign_id
                }
        except httpx.HTTPError as e:
            logger.error(f"Smartlead API error: {e}")
            raise
    
    def list_campaigns(self) -> List[Dict[str, Any]]:
        """List all campaigns."""
        url = self._url_with_key("campaigns")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Listed {len(data)} campaigns")
                return data
        except httpx.HTTPError as e:
            logger.error(f"Smartlead API error: {e}")
            return []
    
    def send_email(
        self,
        email: str,
        subject: str,
        body: str,
        campaign_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a single email (creates campaign and adds lead).
        
        Args:
            email: Recipient email
            subject: Email subject
            body: Email body
            campaign_name: Optional campaign name
        
        Returns:
            Email sending result
        """
        campaign_name = campaign_name or f"Single Email - {email}"
        
        # Create campaign
        campaign_result = self.create_campaign(campaign_name, subject, body)
        campaign_id = campaign_result.get("campaign_id")
        
        if not campaign_id:
            return {"success": False, "error": "Failed to create campaign"}
        
        # Add lead to campaign
        leads = [{"email": email}]
        add_result = self.add_leads_to_campaign(campaign_id, leads)
        
        return {
            "success": add_result.get("success", False),
            "campaign_id": campaign_id,
            "email": email
        }


