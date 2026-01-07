"""Test script for the Agency Apex Swarm system."""

from utils.config import config
from utils.logger import get_logger
from models.lead import Lead
from main import LeadGenerationOrchestrator

logger = get_logger(__name__)


def test_configuration():
    """Test that all API keys are configured."""
    logger.info("Testing configuration...")
    
    missing = config.validate_required_keys()
    if missing:
        logger.error(f"Missing API keys: {missing}")
        return False
    
    logger.info("✓ All API keys configured")
    return True


def test_single_lead():
    """Test processing a single lead."""
    logger.info("Testing single lead processing...")
    
    # Create a test lead
    test_lead = Lead(
        name="Test Creator",
        handle="test_creator_2024",
        platform="instagram",
        bio="Fashion and lifestyle content creator with 50K followers"
    )
    
    # Initialize orchestrator
    orchestrator = LeadGenerationOrchestrator()
    
    # Process the lead
    try:
        result = orchestrator.process_lead(test_lead)
        logger.info(f"Processing result: {result['status']}")
        logger.info(f"Steps completed: {list(result.get('steps', {}).keys())}")
        return result
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        return None


def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("Agency Apex Swarm System Test")
    logger.info("=" * 50)
    
    # Test 1: Configuration
    if not test_configuration():
        logger.error("Configuration test failed. Please check your .env file.")
        return
    
    # Test 2: Single lead processing
    logger.info("\n" + "=" * 50)
    result = test_single_lead()
    
    if result:
        logger.info("\n" + "=" * 50)
        logger.info("Test completed successfully!")
        logger.info(f"Final status: {result.get('status')}")
    else:
        logger.error("Test failed. Check logs for details.")


if __name__ == "__main__":
    main()

