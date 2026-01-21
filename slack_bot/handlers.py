"""Slack event handlers for lead intake."""

import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from utils.logger import get_logger
from utils.config import config
from slack_bot.instagram_parser import extract_instagram_handle, parse_instagram_url, find_all_instagram_urls

logger = get_logger(__name__)


class SlackLeadHandler:
    """Handle Slack messages containing Instagram URLs."""
    
    def __init__(self, slack_client=None):
        """
        Initialize handler.
        
        Args:
            slack_client: Slack WebClient instance (optional, created if not provided)
        """
        self.slack_client = slack_client
        self.channel_id = os.getenv("SLACK_CHANNEL_ID", "")
        
    async def handle_message(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle incoming Slack message event.
        
        Args:
            event: Slack message event payload
            
        Returns:
            Processing result or None
        """
        # Ignore bot messages
        if event.get("bot_id") or event.get("subtype") == "bot_message":
            return None
        
        text = event.get("text", "")
        channel = event.get("channel", "")
        user = event.get("user", "")
        ts = event.get("ts", "")
        
        # Check if message contains Instagram content
        handles = find_all_instagram_urls(text)
        
        if not handles:
            return None
        
        logger.info(f"Found {len(handles)} Instagram handle(s) in message from {user}")
        
        results = []
        for handle in handles:
            result = await self.process_instagram_handle(
                handle=handle,
                channel=channel,
                user=user,
                thread_ts=ts
            )
            results.append(result)
        
        return {"handles_processed": len(handles), "results": results}
    
    async def process_instagram_handle(
        self,
        handle: str,
        channel: str,
        user: str,
        thread_ts: str
    ) -> Dict[str, Any]:
        """
        Process a single Instagram handle.
        
        Args:
            handle: Instagram handle (without @)
            channel: Slack channel ID
            user: Slack user ID who sent the message
            thread_ts: Thread timestamp for replies
            
        Returns:
            Processing result
        """
        # Send acknowledgment
        await self.send_acknowledgment(channel, handle, thread_ts)
        
        # Create lead and add to Google Sheets
        lead_data = await self.create_lead_from_handle(handle, user)
        
        if lead_data.get("error"):
            await self.send_error_message(channel, handle, lead_data["error"], thread_ts)
            return lead_data
        
        # Start async processing (don't wait for completion)
        asyncio.create_task(
            self.process_lead_async(lead_data, channel, thread_ts)
        )
        
        return lead_data
    
    async def create_lead_from_handle(self, handle: str, source_user: str) -> Dict[str, Any]:
        """
        Create a lead entry from Instagram handle.
        
        Args:
            handle: Instagram handle
            source_user: Slack user who submitted
            
        Returns:
            Lead data dictionary
        """
        from api_clients.google_sheets_client import GoogleSheetsClient
        from api_clients.pinecone_client import PineconeClient
        
        try:
            # Check for duplicates first
            from ai_models.openai_client import OpenAIClient
            
            pinecone = PineconeClient()
            openai = OpenAIClient()
            
            # Generate embedding for duplicate check
            lead_text = f"{handle} instagram"
            embedding = openai.generate_embedding(lead_text)
            duplicate_id = pinecone.check_duplicate(embedding, threshold=0.95)
            
            if duplicate_id:
                return {
                    "handle": handle,
                    "status": "duplicate",
                    "error": f"Already processed: @{handle}"
                }
            
            # Add to Google Sheets
            sheets = GoogleSheetsClient()
            
            lead_data = {
                "name": "",  # Will be filled by research
                "handle": f"@{handle}",
                "platform": "instagram",
                "email": "",
                "linkedin": "",
                "bio": "",
                "status": "pending",
                "source": f"slack:{source_user}",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Append to sheet immediately so it can be updated later
            append_success = sheets.append_lead(lead_data)
            if append_success:
                logger.info(f"Added lead @{handle} to Google Sheet")
            else:
                logger.warning(f"Failed to add lead @{handle} to Google Sheet, will try to update later")
            
            logger.info(f"Created lead for @{handle} from Slack")
            
            return {
                "handle": handle,
                "status": "queued",
                "data": lead_data
            }
            
        except Exception as e:
            logger.error(f"Error creating lead for @{handle}: {e}")
            return {
                "handle": handle,
                "status": "error",
                "error": str(e)
            }
    
    async def process_lead_async(
        self,
        lead_data: Dict[str, Any],
        channel: str,
        thread_ts: str
    ):
        """
        Process lead asynchronously and send updates.
        
        Args:
            lead_data: Lead information
            channel: Slack channel for updates
            thread_ts: Thread for replies
        """
        handle = lead_data["handle"]
        
        try:
            # Import processing modules
            from main import LeadGenerationOrchestrator
            from models.lead import Lead
            from api_clients.google_sheets_client import GoogleSheetsClient
            
            # Create Lead object
            lead = Lead(
                handle=handle,
                platform="instagram"
            )
            
            # Process the lead
            orchestrator = LeadGenerationOrchestrator()
            result = orchestrator.process_lead(lead)
            
            # Update Google Sheet (will create if doesn't exist)
            sheets_client = GoogleSheetsClient()
            # Remove @ if present for handle lookup
            clean_handle = handle.lstrip("@")
            update_success = sheets_client.update_lead_after_processing(clean_handle, result)
            if update_success:
                logger.info(f"Updated Google Sheet for @{clean_handle}")
            else:
                logger.warning(f"Failed to update Google Sheet for @{clean_handle}")
            
            # Send completion message
            await self.send_completion_message(channel, handle, result, thread_ts)
            
        except Exception as e:
            logger.error(f"Error processing @{handle}: {e}")
            await self.send_error_message(channel, handle, str(e), thread_ts)
    
    async def send_acknowledgment(self, channel: str, handle: str, thread_ts: str):
        """Send acknowledgment message to Slack."""
        if not self.slack_client:
            logger.info(f"[Slack] Would send: Lead detected @{handle}")
            return
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Lead detected:* `@{handle}`"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Platform:*\nInstagram"},
                    {"type": "mrkdwn", "text": "*Status:*\n⏳ Processing..."}
                ]
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "Estimated completion: 2-3 minutes"}
                ]
            }
        ]
        
        await self.slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"✅ Lead detected: @{handle}",
            blocks=blocks
        )
    
    async def send_completion_message(
        self,
        channel: str,
        handle: str,
        result: Dict[str, Any],
        thread_ts: str
    ):
        """Send completion message with results."""
        if not self.slack_client:
            logger.info(f"[Slack] Would send: Lead processed @{handle}")
            return
        
        # Extract data from result structure
        steps = result.get("steps", {})
        
        # Get email from contact discovery
        contact_data = steps.get("contact_discovery", {})
        email = contact_data.get("email") or "Not found"
        
        # Get vibe score from vibe check
        vibe_check = steps.get("vibe_check", {})
        vibe_score = vibe_check.get("score")
        if vibe_score is None:
            vibe_score = "N/A"
        else:
            # Convert 0-10 scale to 0-100 if needed
            if isinstance(vibe_score, (int, float)) and vibe_score <= 10:
                vibe_score = int(vibe_score * 10)
        
        # Get research summary (Perplexity returns "content", not "summary")
        research_data = steps.get("research", {})
        research = research_data.get("content") or research_data.get("summary") or "No research available"
        if isinstance(research, str) and len(research) > 200:
            research = research[:200] + "..."
        elif not isinstance(research, str):
            research = str(research)[:200] if research else "No research available"
        
        # Get outreach info
        outreach_data = steps.get("outreach", {})
        outreach_channel = "email"
        if outreach_data.get("email", {}).get("success"):
            outreach_channel = "email"
        elif outreach_data.get("linkedin_dm", {}).get("success"):
            outreach_channel = "LinkedIn DM"
        elif outreach_data.get("email", {}) or outreach_data.get("linkedin_dm", {}):
            outreach_channel = "email/LinkedIn"
        
        # Emoji based on vibe score
        if isinstance(vibe_score, (int, float)):
            score_num = int(vibe_score)
            if score_num >= 80:
                vibe_emoji = "✨"
            elif score_num >= 60:
                vibe_emoji = "👍"
            else:
                vibe_emoji = "🤔"
        else:
            vibe_emoji = ""
        
        # Get Google Sheet ID (use config or fallback)
        sheet_id = config.GOOGLE_SHEET_ID or "1Uxspvk_99MSdWmDI6Ur_XqbBukoOcjmeGWyhCk-l8Ew"
        if not sheet_id or sheet_id.strip() == "":
            sheet_id = "1Uxspvk_99MSdWmDI6Ur_XqbBukoOcjmeGWyhCk-l8Ew"
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit" if sheet_id else None
        logger.info(f"Using Google Sheet ID: {sheet_id[:20]}... (URL: {sheet_url})")
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Lead processed:* `@{handle}`"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Email:*\n{email}"},
                    {"type": "mrkdwn", "text": f"*Vibe Score:*\n{vibe_score}/100 {vibe_emoji}"}
                ]
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Research:*\n{research}"},
                    {"type": "mrkdwn", "text": f"*Outreach:*\n📤 Added to {outreach_channel} campaign"}
                ]
            }
        ]
        
        # Add button only if sheet URL is valid
        if sheet_url and sheet_id:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View in Sheet"},
                        "url": sheet_url
                    }
                ]
            })
        
        await self.slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"✅ Lead processed: @{handle}",
            blocks=blocks
        )
    
    async def send_error_message(
        self,
        channel: str,
        handle: str,
        error: str,
        thread_ts: str
    ):
        """Send error message."""
        if not self.slack_client:
            logger.info(f"[Slack] Would send error for @{handle}: {error}")
            return
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"❌ *Error processing:* `@{handle}`"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{error}```"
                }
            }
        ]
        
        await self.slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"❌ Error processing @{handle}: {error}",
            blocks=blocks
        )
    
    async def send_duplicate_message(
        self,
        channel: str,
        handle: str,
        previous_data: Dict[str, Any],
        thread_ts: str
    ):
        """Send duplicate detection message."""
        if not self.slack_client:
            logger.info(f"[Slack] Would send duplicate notice for @{handle}")
            return
        
        processed_at = previous_data.get("processed_at", "Unknown")
        email = previous_data.get("email", "Unknown")
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Duplicate detected:* `@{handle}`"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Previously contacted:*\n{processed_at}"},
                    {"type": "mrkdwn", "text": f"*Email on file:*\n{email}"}
                ]
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "❌ Skipping to avoid double outreach"}
                ]
            }
        ]
        
        await self.slack_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"⚠️ Duplicate detected: @{handle}",
            blocks=blocks
        )


