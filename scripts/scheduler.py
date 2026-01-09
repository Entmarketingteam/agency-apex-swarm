"""Scheduler script to process leads on a schedule."""

import schedule
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.import_leads import import_from_csv
from main import LeadGenerationOrchestrator
from utils.logger import get_logger

logger = get_logger(__name__)


def process_lead_batch():
    """Process a batch of leads from the queue."""
    logger.info("=" * 60)
    logger.info("Starting scheduled lead processing")
    logger.info("=" * 60)
    
    try:
        # Import leads from queue
        queue_file = "leads/queue.csv"
        leads = import_from_csv(queue_file)
        
        if not leads:
            logger.info("No leads in queue")
            return
        
        # Process batch (limit to 10 at a time for rate limiting)
        batch_size = 10
        leads_to_process = leads[:batch_size]
        
        logger.info(f"Processing {len(leads_to_process)} leads (out of {len(leads)} in queue)")
        
        orchestrator = LeadGenerationOrchestrator()
        results = orchestrator.process_batch(leads_to_process)
        
        # Log results
        successful = sum(1 for r in results if r.get('status') == 'completed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        skipped = sum(1 for r in results if r.get('status') == 'skipped')
        
        logger.info(f"Batch complete: {successful} successful, {failed} failed, {skipped} skipped")
        
        # TODO: Move processed leads to archive
        # TODO: Save results to database
        
    except Exception as e:
        logger.error(f"Error in scheduled processing: {e}", exc_info=True)


def main():
    """Run the scheduler."""
    logger.info("Starting Agency Apex Swarm Scheduler")
    logger.info("Processing leads every hour")
    logger.info("Press Ctrl+C to stop")
    
    # Schedule: Process leads every hour
    schedule.every().hour.do(process_lead_batch)
    
    # Also run immediately on start (optional)
    # process_lead_batch()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


if __name__ == "__main__":
    main()


