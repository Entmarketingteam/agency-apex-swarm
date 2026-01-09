"""Main orchestration script for Agency Apex Swarm lead generation system."""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from utils.config import config
from utils.logger import get_logger
from models.lead import Lead, OutreachResult

# API Clients
from api_clients.perplexity_client import PerplexityClient
from api_clients.findymail_client import FindymailClient
from api_clients.unipile_client import UnipileClient
from api_clients.smartlead_client import SmartleadClient
from api_clients.pinecone_client import PineconeClient

# AI Models
from ai_models.claude_client import ClaudeClient
from ai_models.openai_client import OpenAIClient
from ai_models.gemini_client import GeminiClient

logger = get_logger(__name__)


class LeadGenerationOrchestrator:
    """Main orchestrator for lead generation workflow."""
    
    def __init__(self):
        # Validate configuration
        missing_keys = config.validate_required_keys()
        if missing_keys:
            logger.warning(f"Missing API keys: {missing_keys}")
        
        # Initialize clients
        self.perplexity = PerplexityClient()
        self.findymail = FindymailClient()
        self.unipile = UnipileClient()
        self.smartlead = SmartleadClient()
        self.pinecone = PineconeClient()
        
        # Initialize AI models
        self.claude = ClaudeClient()
        self.openai = OpenAIClient()
        self.gemini = GeminiClient()
    
    def process_lead(self, lead: Lead) -> Dict[str, Any]:
        """
        Process a single lead through the complete workflow.
        
        Args:
            lead: Lead object to process
        
        Returns:
            Processing results
        """
        logger.info(f"Processing lead: {lead.handle or lead.name}")
        
        results = {
            "lead_id": lead.id or lead.handle,
            "status": "processing",
            "steps": {}
        }
        
        try:
            # Step 1: Research & Validation
            logger.info("Step 1: Research & Validation")
            research_data = self._research_lead(lead)
            results["steps"]["research"] = research_data
            
            # Step 2: Visual Vibe Check (if applicable)
            if lead.platform in ["instagram", "tiktok"]:
                logger.info("Step 2: Visual Vibe Check")
                vibe_check = self._vibe_check_lead(lead, research_data)
                results["steps"]["vibe_check"] = vibe_check
                
                # Skip if vibe check fails
                if vibe_check.get("recommendation") == "skip":
                    results["status"] = "skipped"
                    results["reason"] = "Low vibe check score"
                    return results
            else:
                vibe_check = None
            
            # Step 3: Contact Discovery
            logger.info("Step 3: Contact Discovery")
            contact_data = self._discover_contact(lead)
            results["steps"]["contact_discovery"] = contact_data
            
            if not contact_data.get("email") and not contact_data.get("linkedin_url"):
                results["status"] = "failed"
                results["reason"] = "No contact information found"
                return results
            
            # Step 4: Duplicate Check
            logger.info("Step 4: Duplicate Check")
            is_duplicate = self._check_duplicate(lead)
            results["steps"]["duplicate_check"] = {"is_duplicate": is_duplicate}
            
            if is_duplicate:
                results["status"] = "skipped"
                results["reason"] = "Duplicate lead"
                return results
            
            # Step 5: Content Generation
            logger.info("Step 5: Content Generation")
            content = self._generate_outreach_content(lead, research_data, vibe_check)
            results["steps"]["content_generation"] = content
            
            # Step 6: Outreach Execution
            logger.info("Step 6: Outreach Execution")
            outreach_results = self._execute_outreach(lead, contact_data, content)
            results["steps"]["outreach"] = outreach_results
            
            # Step 7: Store in Memory
            logger.info("Step 7: Store in Memory")
            self._store_lead(lead, research_data, vibe_check)
            
            results["status"] = "completed"
            logger.info(f"Lead processing completed: {lead.handle or lead.name}")
            
        except Exception as e:
            logger.error(f"Error processing lead: {e}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    def _research_lead(self, lead: Lead) -> Dict[str, Any]:
        """Research a lead using Perplexity."""
        try:
            query = f"Research {lead.name or lead.handle} on {lead.platform or 'social media'}. Find follower count, engagement rate, content style, brand partnerships, and recent activity."
            research = self.perplexity.research_creator(
                creator_name=lead.name or lead.handle or "",
                platform=lead.platform or "instagram"
            )
            return research
        except Exception as e:
            logger.error(f"Research error: {e}")
            return {"error": str(e)}
    
    def _vibe_check_lead(self, lead: Lead, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform visual vibe check using Gemini."""
        try:
            # For now, use text-based analysis
            # In production, you'd download images from the lead's profile
            vibe_check = self.gemini.vibe_check(
                creator_info={
                    "name": lead.name,
                    "handle": lead.handle,
                    "platform": lead.platform,
                    "research": research_data
                }
            )
            
            # Update lead with vibe check data
            lead.vibe_check_score = vibe_check.get("score", 0.0)
            lead.vibe_check_notes = vibe_check.get("notes", "")
            
            return vibe_check
        except Exception as e:
            logger.error(f"Vibe check error: {e}")
            return {"error": str(e), "recommendation": "skip"}
    
    def _discover_contact(self, lead: Lead) -> Dict[str, Any]:
        """Discover contact information using Findymail."""
        try:
            if lead.handle:
                email_result = self.findymail.find_from_handle(
                    handle=lead.handle,
                    platform=lead.platform or "instagram"
                )
                
                if email_result.get("email"):
                    lead.email = email_result["email"]
                
                return {
                    "email": email_result.get("email"),
                    "confidence": email_result.get("confidence", 0),
                    "linkedin_url": lead.linkedin_url
                }
            else:
                return {"email": None, "linkedin_url": lead.linkedin_url}
        except Exception as e:
            logger.error(f"Contact discovery error: {e}")
            return {"error": str(e)}
    
    def _check_duplicate(self, lead: Lead) -> bool:
        """Check if lead is a duplicate using Pinecone."""
        try:
            # Generate embedding for the lead
            lead_text = f"{lead.name} {lead.handle} {lead.bio or ''}"
            embedding = self.openai.generate_embedding(lead_text)
            
            # Check for duplicates
            duplicate_id = self.pinecone.check_duplicate(embedding, threshold=0.95)
            return duplicate_id is not None
        except Exception as e:
            logger.error(f"Duplicate check error: {e}")
            return False  # If check fails, proceed (don't block on errors)
    
    def _generate_outreach_content(
        self,
        lead: Lead,
        research_data: Dict[str, Any],
        vibe_check: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate outreach content using GPT-5.2 Pro."""
        try:
            lead_data = {
                "name": lead.name,
                "handle": lead.handle,
                "bio": lead.bio,
                "platform": lead.platform
            }
            
            # Generate email
            email_content = self.openai.write_email(
                lead_data=lead_data,
                research_data=research_data,
                vibe_check_data=vibe_check
            )
            
            # Generate LinkedIn DM (if applicable)
            linkedin_dm = None
            if lead.linkedin_url:
                linkedin_dm = self.openai.write_linkedin_dm(
                    lead_data=lead_data,
                    research_data=research_data
                )
            
            return {
                "email": email_content,
                "linkedin_dm": linkedin_dm
            }
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return {"error": str(e)}
    
    def _execute_outreach(
        self,
        lead: Lead,
        contact_data: Dict[str, Any],
        content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute outreach via email and/or LinkedIn DM."""
        results = {
            "email": None,
            "linkedin_dm": None
        }
        
        # Send email if available
        if contact_data.get("email") and content.get("email"):
            try:
                email_result = self.smartlead.send_email(
                    email=contact_data["email"],
                    subject=content["email"]["subject"],
                    body=content["email"]["body"],
                    campaign_name=f"Outreach - {lead.handle or lead.name}"
                )
                results["email"] = email_result
                lead.contact_status = "contacted"
                lead.outreach_method = "email"
                lead.outreach_date = datetime.now()
            except Exception as e:
                logger.error(f"Email sending error: {e}")
                results["email"] = {"error": str(e)}
        
        # Send LinkedIn DM if available
        if contact_data.get("linkedin_url") and content.get("linkedin_dm"):
            try:
                dm_result = self.unipile.send_dm(
                    linkedin_url=contact_data["linkedin_url"],
                    message=content["linkedin_dm"]
                )
                results["linkedin_dm"] = dm_result
                if lead.outreach_method:
                    lead.outreach_method = "both"
                else:
                    lead.outreach_method = "linkedin_dm"
            except Exception as e:
                logger.error(f"LinkedIn DM error: {e}")
                results["linkedin_dm"] = {"error": str(e)}
        
        return results
    
    def _store_lead(
        self,
        lead: Lead,
        research_data: Dict[str, Any],
        vibe_check: Optional[Dict[str, Any]]
    ):
        """Store lead in Pinecone for future deduplication."""
        try:
            # Generate embedding
            lead_text = f"{lead.name} {lead.handle} {lead.bio or ''} {research_data.get('content', '')}"
            embedding = self.openai.generate_embedding(lead_text)
            
            # Store metadata
            metadata = {
                "name": lead.name or "",
                "handle": lead.handle or "",
                "platform": lead.platform or "",
                "email": lead.email or "",
                "vibe_score": lead.vibe_check_score or 0.0,
                "contact_status": lead.contact_status or "pending",
                "created_at": lead.created_at.isoformat()
            }
            
            # Upsert to Pinecone
            self.pinecone.upsert_lead(
                lead_id=lead.id or lead.handle or str(lead.created_at),
                embedding=embedding,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Storage error: {e}")
    
    def process_batch(self, leads: List[Lead]) -> List[Dict[str, Any]]:
        """
        Process a batch of leads.
        
        Args:
            leads: List of Lead objects
        
        Returns:
            List of processing results
        """
        logger.info(f"Processing batch of {len(leads)} leads")
        results = []
        
        for lead in leads:
            result = self.process_lead(lead)
            results.append(result)
        
        logger.info(f"Batch processing completed: {len(results)} leads processed")
        return results


def main():
    """Main entry point."""
    logger.info("Starting Agency Apex Swarm Lead Generation System")
    
    # Validate configuration
    if not config.is_configured():
        missing = config.validate_required_keys()
        logger.error(f"Missing required API keys: {missing}")
        logger.error("Please add all required keys to your .env file")
        return
    
    # Initialize orchestrator
    orchestrator = LeadGenerationOrchestrator()
    
    # Example: Process a single lead
    example_lead = Lead(
        name="Example Creator",
        handle="example_creator",
        platform="instagram",
        bio="Fashion and lifestyle content creator"
    )
    
    logger.info("Processing example lead...")
    result = orchestrator.process_lead(example_lead)
    
    logger.info(f"Processing result: {result['status']}")
    logger.info("System ready for production use")


if __name__ == "__main__":
    main()


