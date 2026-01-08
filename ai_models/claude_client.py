"""Claude Opus 4.5 client for orchestration and complex logic."""

from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeClient:
    """Client for Claude Opus 4.5 - complex logic and orchestration."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(Exception,))
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Claude.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Build request parameters
            params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            # Add system prompt if provided (as string, not list)
            if system_prompt:
                params["system"] = system_prompt
            
            response = self.client.messages.create(**params)
            
            content = response.content[0].text
            logger.info(f"Claude generation completed ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    def orchestrate_workflow(
        self,
        workflow_description: str,
        available_tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use Claude's programmatic tool calling to orchestrate a workflow.
        
        Args:
            workflow_description: Description of the workflow to execute
            available_tools: List of available tools/functions
            context: Additional context for the workflow
        
        Returns:
            Workflow execution result
        """
        system_prompt = """You are an orchestration agent that coordinates multiple API calls efficiently.
        Use programmatic tool calling to execute multiple operations in parallel where possible.
        Always handle errors gracefully and provide detailed results."""
        
        prompt = f"""
        Workflow: {workflow_description}
        
        Available Tools: {available_tools}
        
        Context: {context or {}}
        
        Plan and execute this workflow using the available tools. Optimize for parallel execution where possible.
        """
        
        result = self.generate(prompt, system_prompt=system_prompt, temperature=0.3)
        
        return {
            "workflow": workflow_description,
            "result": result,
            "context": context
        }
    
    def plan_lead_generation(
        self,
        lead_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan the lead generation workflow for a specific lead.
        
        Args:
            lead_data: Initial lead data
        
        Returns:
            Execution plan
        """
        prompt = f"""
        Analyze this lead and create an execution plan:
        
        Lead Data: {lead_data}
        
        Create a step-by-step plan for:
        1. Research validation
        2. Visual vibe check (if applicable)
        3. Contact discovery
        4. Duplicate checking
        5. Outreach strategy
        
        Return a structured plan with priorities and dependencies.
        """
        
        plan = self.generate(prompt, temperature=0.3)
        
        return {
            "lead": lead_data,
            "plan": plan
        }

