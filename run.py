#!/usr/bin/env python3
"""Simple entry point for Railway deployment."""

import os
import sys
import time
import schedule
import threading
import asyncio

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import config
from utils.logger import get_logger

logger = get_logger(__name__)

# Google Sheet configuration
GOOGLE_SHEET_ID = "1R2bYx2-G7cgtkv2GuiYqSZz-A7FOgh1V"
GOOGLE_SHEET_TAB = "TEST SHEET FOR CURSOR"  # Your dedicated sheet tab
USE_GOOGLE_SHEETS = True  # Set to True to use Google Sheets instead of CSV


def process_leads_from_sheets():
    """Process leads from Google Sheets."""
    logger.info("=" * 60)
    logger.info("📊 Fetching leads from Google Sheets...")
    logger.info("=" * 60)
    
    try:
        from api_clients.google_sheets_client import GoogleSheetsClient, convert_sheet_row_to_lead
        from main import LeadGenerationOrchestrator
        
        # Fetch leads from Google Sheet
        sheets_client = GoogleSheetsClient()
        sheet_rows = sheets_client.get_unprocessed_leads()
        
        if not sheet_rows:
            logger.info("No unprocessed leads in Google Sheet")
            return
        
        # Convert to Lead objects
        leads = []
        for row in sheet_rows:
            lead = convert_sheet_row_to_lead(row)
            if lead.handle or lead.name:
                leads.append(lead)
        
        if not leads:
            logger.info("No valid leads found")
            return
        
        logger.info(f"Found {len(leads)} leads to process from Google Sheets")
        
        # Process batch (max 10 at a time)
        orchestrator = LeadGenerationOrchestrator()
        results = orchestrator.process_batch(leads[:10])
        
        # Log results
        successful = sum(1 for r in results if r.get('status') == 'completed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        skipped = sum(1 for r in results if r.get('status') == 'skipped')
        
        logger.info(f"Batch complete: {successful} successful, {failed} failed, {skipped} skipped")
        
    except Exception as e:
        logger.error(f"Error processing leads from sheets: {e}", exc_info=True)


def process_leads_from_csv():
    """Process leads from CSV queue."""
    logger.info("=" * 60)
    logger.info("📁 Processing leads from CSV...")
    logger.info("=" * 60)
    
    try:
        from main import LeadGenerationOrchestrator
        from models.lead import Lead
        
        # Check if queue file exists
        queue_file = "leads/queue.csv"
        if not os.path.exists(queue_file):
            logger.info(f"No queue file found at {queue_file}")
            return
        
        # Import leads
        import csv
        leads = []
        with open(queue_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                lead = Lead(
                    name=row.get('name', '').strip() or None,
                    handle=row.get('handle', '').strip() or None,
                    platform=row.get('platform', 'instagram').strip().lower(),
                    bio=row.get('bio', '').strip() or None
                )
                if lead.handle or lead.name:
                    leads.append(lead)
        
        if not leads:
            logger.info("No leads in CSV queue")
            return
        
        logger.info(f"Found {len(leads)} leads to process from CSV")
        
        # Process batch
        orchestrator = LeadGenerationOrchestrator()
        results = orchestrator.process_batch(leads[:10])
        
        # Log results
        successful = sum(1 for r in results if r.get('status') == 'completed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        skipped = sum(1 for r in results if r.get('status') == 'skipped')
        
        logger.info(f"Batch complete: {successful} successful, {failed} failed, {skipped} skipped")
        
    except Exception as e:
        logger.error(f"Error processing leads from CSV: {e}", exc_info=True)


def process_leads():
    """Process leads from configured source."""
    if USE_GOOGLE_SHEETS:
        process_leads_from_sheets()
    else:
        process_leads_from_csv()


def start_slack_bot():
    """Start the Slack bot in a separate thread."""
    try:
        from slack_bot.app import run_slack_bot_sync
        logger.info("🤖 Starting Slack bot...")
        run_slack_bot_sync()
    except Exception as e:
        logger.error(f"Failed to start Slack bot: {e}", exc_info=True)


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("🚀 Agency Apex Swarm - Starting")
    logger.info("=" * 60)
    
    # Validate configuration
    missing = config.validate_required_keys()
    if missing:
        logger.warning(f"Missing API keys: {missing}")
    else:
        logger.info("✅ All API keys configured")
    
    # Check if Slack tokens are configured
    if config.SLACK_BOT_TOKEN and config.SLACK_SIGNING_SECRET and config.SLACK_APP_TOKEN:
        logger.info("✅ Slack tokens configured - starting Slack bot")
        # Start Slack bot in a separate thread
        slack_thread = threading.Thread(target=start_slack_bot, daemon=True)
        slack_thread.start()
        logger.info("🤖 Slack bot thread started")
    else:
        logger.info("⚠️ Slack tokens not configured - Slack bot disabled")
    
    # Schedule: Process leads every hour
    schedule.every().hour.do(process_leads)
    
    # Process immediately on start
    logger.info("📊 Processing initial batch of leads...")
    process_leads()
    
    logger.info("Scheduler running - processing leads every hour")
    logger.info("Waiting for scheduled tasks...")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()

