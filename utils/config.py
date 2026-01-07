"""Configuration management and environment variable loading."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration management."""
    
    # AI Model API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Lead Generation APIs
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    FINDYMAIL_API_KEY: str = os.getenv("FINDYMAIL_API_KEY", "")
    UNIPILE_API_KEY: str = os.getenv("UNIPILE_API_KEY", "")
    SMARTLEAD_API_KEY: str = os.getenv("SMARTLEAD_API_KEY", "")
    
    # Vector Database
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    
    # Additional APIs
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    SUPABASE_API_KEY: str = os.getenv("SUPABASE_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    DATA_FOR_SEO_API_KEY: str = os.getenv("DATA_FOR_SEO_API_KEY", "")
    
    # Google Sheets
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SHEET_TAB_NAME: str = os.getenv("GOOGLE_SHEET_TAB_NAME", "TEST SHEET FOR CURSOR")
    
    # Slack Integration
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET", "")
    SLACK_APP_TOKEN: str = os.getenv("SLACK_APP_TOKEN", "")
    SLACK_CHANNEL_ID: str = os.getenv("SLACK_CHANNEL_ID", "")
    
    @classmethod
    def validate_required_keys(cls) -> list[str]:
        """Validate that all required API keys are present."""
        required_keys = [
            ("ANTHROPIC_API_KEY", cls.ANTHROPIC_API_KEY),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("GOOGLE_API_KEY", cls.GOOGLE_API_KEY),
            ("PERPLEXITY_API_KEY", cls.PERPLEXITY_API_KEY),
            ("FINDYMAIL_API_KEY", cls.FINDYMAIL_API_KEY),
            ("UNIPILE_API_KEY", cls.UNIPILE_API_KEY),
            ("SMARTLEAD_API_KEY", cls.SMARTLEAD_API_KEY),
            ("PINECONE_API_KEY", cls.PINECONE_API_KEY),
        ]
        
        missing = [key for key, value in required_keys if not value]
        return missing
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if all required keys are configured."""
        return len(cls.validate_required_keys()) == 0


# Global config instance
config = Config()

