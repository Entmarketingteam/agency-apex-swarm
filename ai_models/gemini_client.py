"""Gemini 3.0 Ultra client for visual analysis and vibe checks."""

from typing import Dict, Any, Optional, Union
import google.generativeai as genai
from utils.config import config
from utils.retry import exponential_backoff_retry
from utils.logger import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Client for Gemini 3.0 Ultra - visual analysis and multimodal tasks."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro-vision"):
        self.api_key = api_key or config.GOOGLE_API_KEY
        self.model_name = model
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(Exception,))
    def analyze_image(
        self,
        image_path: Union[str, bytes],
        prompt: str
    ) -> str:
        """
        Analyze an image using Gemini vision.
        
        Args:
            image_path: Path to image file or image bytes
            prompt: Analysis prompt
        
        Returns:
            Analysis result
        """
        try:
            import PIL.Image
            
            if isinstance(image_path, str):
                img = PIL.Image.open(image_path)
            else:
                from io import BytesIO
                img = PIL.Image.open(BytesIO(image_path))
            
            response = self.model.generate_content([prompt, img])
            result = response.text
            
            logger.info(f"Gemini image analysis completed")
            return result
        except Exception as e:
            logger.error(f"Gemini image analysis error: {e}")
            raise
    
    @exponential_backoff_retry(max_attempts=3, exceptions=(Exception,))
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Gemini.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        try:
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            result = response.text
            logger.info(f"Gemini generation completed ({len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def vibe_check(
        self,
        image_url: Optional[str] = None,
        image_path: Optional[str] = None,
        creator_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Perform a visual vibe check on creator content.
        
        Args:
            image_url: URL to creator's image/post
            image_path: Local path to image file
            creator_info: Additional creator information
        
        Returns:
            Vibe check results with score and notes
        """
        vibe_prompt = """Analyze this creator's content for brand partnership potential.
        
        Evaluate:
        1. Aesthetic quality (color palette, composition, visual style)
        2. Engagement indicators (likes, comments, overall vibe)
        3. Brand fit potential (professionalism, audience quality)
        4. Content consistency
        5. Authenticity and relatability
        
        Provide:
        - A score from 0-10 for brand partnership fit
        - Detailed notes on strengths and concerns
        - Specific recommendations for outreach approach
        
        Be honest and critical in your assessment."""
        
        try:
            if image_path:
                analysis = self.analyze_image(image_path, vibe_prompt)
            elif image_url:
                # For URL, we'd need to download first or use a different approach
                # For now, use text-based analysis
                full_prompt = f"{vibe_prompt}\n\nCreator Info: {creator_info or {}}\n\nImage URL: {image_url}"
                analysis = self.generate(full_prompt)
            else:
                # Text-only analysis if no image provided
                full_prompt = f"{vibe_prompt}\n\nCreator Info: {creator_info or {}}"
                analysis = self.generate(full_prompt)
            
            # Extract score from analysis (simple parsing - could be improved)
            score = 7.0  # Default
            if "score" in analysis.lower():
                try:
                    import re
                    score_match = re.search(r'(\d+\.?\d*)/10', analysis)
                    if score_match:
                        score = float(score_match.group(1))
                except:
                    pass
            
            return {
                "score": score,
                "notes": analysis,
                "recommendation": "proceed" if score >= 7.0 else "review"
            }
        except Exception as e:
            logger.error(f"Vibe check error: {e}")
            return {
                "score": 0.0,
                "notes": f"Error during vibe check: {str(e)}",
                "recommendation": "error"
            }


