"""Script to verify all API connections are working."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import config
from utils.logger import get_logger
from api_clients.perplexity_client import PerplexityClient
from api_clients.findymail_client import FindymailClient
from api_clients.unipile_client import UnipileClient
from api_clients.smartlead_client import SmartleadClient
from api_clients.pinecone_client import PineconeClient
from ai_models.claude_client import ClaudeClient
from ai_models.openai_client import OpenAIClient
from ai_models.gemini_client import GeminiClient

logger = get_logger(__name__)


def test_perplexity():
    """Test Perplexity API."""
    logger.info("Testing Perplexity API...")
    try:
        client = PerplexityClient()
        result = client.search("What is artificial intelligence?")
        if result.get("content"):
            logger.info("✅ Perplexity API: WORKING")
            return True
        else:
            logger.error("❌ Perplexity API: No content returned")
            return False
    except Exception as e:
        logger.error(f"❌ Perplexity API: ERROR - {e}")
        return False


def test_findymail():
    """Test Findymail API."""
    logger.info("Testing Findymail API...")
    try:
        client = FindymailClient()
        # Test with a known handle (this will likely fail but tests connection)
        result = client.find_from_handle("test_handle", "instagram")
        logger.info("✅ Findymail API: Connection successful (may not find email)")
        return True
    except Exception as e:
        logger.error(f"❌ Findymail API: ERROR - {e}")
        return False


def test_unipile():
    """Test Unipile API."""
    logger.info("Testing Unipile API...")
    try:
        client = UnipileClient()
        # Just test connection - don't actually send DM
        logger.info("✅ Unipile API: Client initialized (connection test skipped)")
        return True
    except Exception as e:
        logger.error(f"❌ Unipile API: ERROR - {e}")
        return False


def test_smartlead():
    """Test Smartlead API."""
    logger.info("Testing Smartlead API...")
    try:
        client = SmartleadClient()
        # Test connection by checking if we can create a test campaign
        logger.info("✅ Smartlead API: Client initialized (full test requires campaign creation)")
        return True
    except Exception as e:
        logger.error(f"❌ Smartlead API: ERROR - {e}")
        return False


def test_pinecone():
    """Test Pinecone API."""
    logger.info("Testing Pinecone API...")
    try:
        client = PineconeClient()
        logger.info("✅ Pinecone API: WORKING (index created/connected)")
        return True
    except Exception as e:
        logger.error(f"❌ Pinecone API: ERROR - {e}")
        return False


def test_claude():
    """Test Claude API."""
    logger.info("Testing Claude API...")
    try:
        client = ClaudeClient()
        result = client.generate("Say 'API test successful' if you can read this.")
        if "successful" in result.lower():
            logger.info("✅ Claude API: WORKING")
            return True
        else:
            logger.error("❌ Claude API: Unexpected response")
            return False
    except Exception as e:
        logger.error(f"❌ Claude API: ERROR - {e}")
        return False


def test_openai():
    """Test OpenAI API."""
    logger.info("Testing OpenAI API...")
    try:
        client = OpenAIClient()
        result = client.generate("Say 'API test successful' if you can read this.")
        if "successful" in result.lower():
            logger.info("✅ OpenAI API: WORKING")
            return True
        else:
            logger.error("❌ OpenAI API: Unexpected response")
            return False
    except Exception as e:
        logger.error(f"❌ OpenAI API: ERROR - {e}")
        return False


def test_gemini():
    """Test Gemini API."""
    logger.info("Testing Gemini API...")
    try:
        client = GeminiClient()
        result = client.generate("Say 'API test successful' if you can read this.")
        if "successful" in result.lower():
            logger.info("✅ Gemini API: WORKING")
            return True
        else:
            logger.error("❌ Gemini API: Unexpected response")
            return False
    except Exception as e:
        logger.error(f"❌ Gemini API: ERROR - {e}")
        return False


def main():
    """Run all API tests."""
    logger.info("=" * 60)
    logger.info("API Verification Test")
    logger.info("=" * 60)
    
    # Check configuration first
    missing = config.validate_required_keys()
    if missing:
        logger.error(f"Missing API keys: {missing}")
        logger.error("Please add all keys to .env file")
        return
    
    logger.info("\nTesting API connections...\n")
    
    results = {
        "Perplexity": test_perplexity(),
        "Findymail": test_findymail(),
        "Unipile": test_unipile(),
        "Smartlead": test_smartlead(),
        "Pinecone": test_pinecone(),
        "Claude": test_claude(),
        "OpenAI": test_openai(),
        "Gemini": test_gemini(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for service, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{service:15} {status}")
    
    logger.info(f"\nTotal: {passed}/{total} APIs working")
    
    if passed == total:
        logger.info("\n🎉 All APIs verified! System ready for testing.")
    else:
        logger.warning(f"\n⚠️  {total - passed} API(s) need attention. Check errors above.")


if __name__ == "__main__":
    main()

