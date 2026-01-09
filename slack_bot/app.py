"""Slack bot application for APEX lead intake."""

import os
import asyncio
from typing import Optional

from utils.logger import get_logger
from utils.config import config

logger = get_logger(__name__)

# Check for slack_bolt availability
try:
    from slack_bolt.async_app import AsyncApp
    from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    logger.warning("slack_bolt not installed. Run: pip install slack-bolt")


def create_slack_app() -> Optional["AsyncApp"]:
    """
    Create and configure the Slack app.
    
    Returns:
        Configured AsyncApp or None if not available
    """
    if not SLACK_AVAILABLE:
        logger.error("Slack SDK not available")
        return None
    
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    app_token = os.getenv("SLACK_APP_TOKEN")  # For Socket Mode
    
    if not bot_token or not signing_secret:
        logger.error("SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET required")
        return None
    
    # Check if channel restriction is configured
    allowed_channel_id = config.SLACK_CHANNEL_ID
    if allowed_channel_id:
        logger.info(f"🔒 Bot restricted to channel: {allowed_channel_id}")
    else:
        logger.warning("⚠️ No SLACK_CHANNEL_ID set - bot will respond to ALL channels")
    
    app = AsyncApp(
        token=bot_token,
        signing_secret=signing_secret
    )
    
    # Import handlers
    from slack_bot.handlers import SlackLeadHandler
    from slack_bot.instagram_parser import find_all_instagram_urls
    
    handler = SlackLeadHandler(slack_client=app.client)
    
    # Get allowed channel ID from config
    allowed_channel_id = config.SLACK_CHANNEL_ID
    
    @app.event("message")
    async def handle_message_events(event, say, client):
        """Handle all message events - only from allowed channel."""
        # Skip bot messages
        if event.get("bot_id"):
            return
        
        # Check if message is from allowed channel
        channel_id = event.get("channel", "")
        if allowed_channel_id and channel_id != allowed_channel_id:
            # Silently ignore messages from other channels
            logger.debug(f"Ignoring message from channel {channel_id} (not allowed channel)")
            return
        
        text = event.get("text", "")
        
        # Check for Instagram content
        handles = find_all_instagram_urls(text)
        
        if handles:
            logger.info(f"Processing {len(handles)} Instagram handle(s) from channel {channel_id}")
            await handler.handle_message(event)
    
    @app.event("app_mention")
    async def handle_app_mention(event, say):
        """Handle @mentions of the bot - only from allowed channel."""
        # Check if mention is from allowed channel
        channel_id = event.get("channel", "")
        if allowed_channel_id and channel_id != allowed_channel_id:
            # Silently ignore mentions from other channels
            logger.debug(f"Ignoring mention from channel {channel_id} (not allowed channel)")
            return
        
        text = event.get("text", "")
        user = event.get("user", "")
        
        # Check for Instagram URLs in mention
        handles = find_all_instagram_urls(text)
        
        if handles:
            await handler.handle_message(event)
        else:
            await say(
                text=f"Hi <@{user}>! Paste an Instagram URL and I'll process it as a lead.",
                thread_ts=event.get("ts")
            )
    
    @app.command("/apex")
    async def handle_apex_command(ack, body, client):
        """Handle /apex slash command - only from allowed channel."""
        channel_id = body.get("channel_id", "")
        
        # Check if command is from allowed channel
        if allowed_channel_id and channel_id != allowed_channel_id:
            await ack(
                response_type="ephemeral",
                text=f"❌ This command can only be used in the designated lead intake channel."
            )
            return
        
        await ack()
        
        text = body.get("text", "").strip()
        user_id = body.get("user_id", "")
        
        if not text:
            await client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="Usage: `/apex @username` or `/apex https://instagram.com/username`"
            )
            return
        
        handles = find_all_instagram_urls(text)
        
        if not handles:
            await client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text="❌ No valid Instagram handle found. Try: `/apex @username`"
            )
            return
        
        # Process each handle
        for handle in handles:
            await client.chat_postMessage(
                channel=channel_id,
                text=f"🔍 Processing lead: @{handle}..."
            )
            
            result = await handler.process_instagram_handle(
                handle=handle,
                channel=channel_id,
                user=user_id,
                thread_ts=""
            )
    
    @app.shortcut("process_lead")
    async def handle_shortcut(ack, shortcut, client):
        """Handle message shortcut for processing leads."""
        await ack()
        
        # Get the message text
        message = shortcut.get("message", {})
        text = message.get("text", "")
        channel = shortcut.get("channel", {}).get("id", "")
        
        handles = find_all_instagram_urls(text)
        
        if handles:
            for handle in handles:
                await client.chat_postMessage(
                    channel=channel,
                    text=f"🔍 Processing lead from shortcut: @{handle}..."
                )
    
    logger.info("Slack app configured successfully")
    return app


async def run_slack_bot():
    """Run the Slack bot in Socket Mode."""
    if not SLACK_AVAILABLE:
        logger.error("Cannot run Slack bot: slack_bolt not installed")
        return
    
    app = create_slack_app()
    if not app:
        logger.error("Failed to create Slack app")
        return
    
    app_token = os.getenv("SLACK_APP_TOKEN")
    if not app_token:
        logger.error("SLACK_APP_TOKEN required for Socket Mode")
        return
    
    handler = AsyncSocketModeHandler(app, app_token)
    
    logger.info("Starting Slack bot in Socket Mode...")
    await handler.start_async()


def run_slack_bot_sync():
    """Synchronous wrapper to run the Slack bot."""
    asyncio.run(run_slack_bot())


if __name__ == "__main__":
    run_slack_bot_sync()


