#!/usr/bin/env python3
"""Simple entry point for Railway deployment."""

import os
import sys
import time
import schedule

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import config
from utils.logger import get_logger

logger = get_logger(__name__)


def process_leads():
    """Process leads from queue."""
    logger.info("=" * 60)
    logger.info("Starting lead processing...")
    logger.info("=" * 60)
    
    try:
        # Import here to avoid circular imports
        from main import LeadGenerationOrchestrator
        from models.lead import Lead
        
        # Check if queue file exists
        queue_file = "leads/queue.csv"
        if not os.path.exists(queue_file):
            logger.info(f"No queue file found at {queue_file}")
            logger.info("Create leads/queue.csv to start processing leads")
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
            logger.info("No leads in queue")
            return
        
        logger.info(f"Found {len(leads)} leads to process")
        
        # Process batch
        orchestrator = LeadGenerationOrchestrator()
        results = orchestrator.process_batch(leads[:10])  # Max 10 at a time
        
        # Log results
        successful = sum(1 for r in results if r.get('status') == 'completed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        skipped = sum(1 for r in results if r.get('status') == 'skipped')
        
        logger.info(f"Batch complete: {successful} successful, {failed} failed, {skipped} skipped")
        
    except Exception as e:
        logger.error(f"Error processing leads: {e}", exc_info=True)


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
    
    # Schedule: Process leads every hour
    schedule.every().hour.do(process_leads)
    
    logger.info("Scheduler running - processing leads every hour")
    logger.info("Waiting for scheduled tasks...")
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()

