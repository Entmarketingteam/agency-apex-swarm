"""OpenAI GPT-5.2 Pro client for persuasive writing."""

from typing import Dict, Any, Optional
from openai import OpenAI
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Client for GPT-5.2 Pro - persuasive writing and high-stakes outreach."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key or config.OPENAI_API_KEY
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(Exception,))
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.8
    ) -> str:
        """
        Generate text using GPT.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI generation completed ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> list[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            model: Embedding model to use
        
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding ({len(embedding)} dimensions)")
            return embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    def write_email(
        self,
        lead_data: Dict[str, Any],
        research_data: Optional[Dict[str, Any]] = None,
        vibe_check_data: Optional[Dict[str, Any]] = None,
        tone: str = "professional but friendly"
    ) -> Dict[str, str]:
        """
        Write a persuasive email for outreach.
        
        Args:
            lead_data: Lead information
            research_data: Research findings
            vibe_check_data: Visual vibe check results
            tone: Email tone
        
        Returns:
            Email subject and body
        """
        system_prompt = """You are an expert email copywriter specializing in influencer outreach.
        Write compelling, personalized emails that get responses. Be concise, value-focused, and authentic."""
        
        prompt = f"""
        Write a persuasive outreach email for this lead:
        
        Lead: {lead_data}
        Research: {research_data or {}}
        Vibe Check: {vibe_check_data or {}}
        Tone: {tone}
        
        Create:
        1. A compelling subject line (under 60 characters)
        2. An email body (3-4 paragraphs max) that:
           - Opens with a personalized hook
           - Shows you've done research
           - Clearly states the value proposition
           - Includes a clear call-to-action
           - Maintains the {tone} tone
        
        Return the subject and body separately.
        """
        
        result = self.generate(prompt, system_prompt=system_prompt, temperature=0.7)
        
        # Parse result (simple extraction - could be improved)
        lines = result.split("\n")
        subject = ""
        body = ""
        
        in_body = False
        for line in lines:
            if "subject" in line.lower() and ":" in line:
                subject = line.split(":", 1)[1].strip()
            elif "body" in line.lower() and ":" in line:
                in_body = True
                body = line.split(":", 1)[1].strip() + "\n"
            elif in_body:
                body += line + "\n"
        
        return {
            "subject": subject or "Partnership Opportunity",
            "body": body or result
        }
    
    def write_linkedin_dm(
        self,
        lead_data: Dict[str, Any],
        research_data: Optional[Dict[str, Any]] = None,
        tone: str = "casual and friendly"
    ) -> str:
        """
        Write a LinkedIn DM for outreach.
        
        Args:
            lead_data: Lead information
            research_data: Research findings
            tone: Message tone
        
        Returns:
            DM message text
        """
        system_prompt = """You are an expert at writing LinkedIn DMs that get responses.
        Keep it short, personal, and value-focused. LinkedIn DMs should be conversational and authentic."""
        
        prompt = f"""
        Write a LinkedIn DM for this lead:
        
        Lead: {lead_data}
        Research: {research_data or {}}
        Tone: {tone}
        
        Create a short, personalized message (2-3 sentences max) that:
        - Opens with a personalized connection
        - Shows genuine interest
        - Includes a clear value proposition
        - Ends with a soft call-to-action
        
        Keep it under 300 characters.
        """
        
        message = self.generate(prompt, system_prompt=system_prompt, temperature=0.7, max_tokens=200)
        return message.strip()


