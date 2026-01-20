"""
ZoneWise V3 - LLM Router
Smart routing between LLM providers for cost optimization.
Target: 90% FREE tier (Gemini), 10% paid (Claude/OpenAI).
"""

import os
from typing import Optional
from enum import Enum
import structlog

logger = structlog.get_logger()


class ModelTier(str, Enum):
    """LLM tiers for cost optimization."""
    FREE = "free"           # Gemini 2.5 Flash - 90% of calls
    ULTRA_CHEAP = "ultra_cheap"  # DeepSeek V3.2 - 5%
    STANDARD = "standard"   # Claude Sonnet 4.5 - 4%
    PREMIUM = "premium"     # Claude Opus 4.5 - 1%


TIER_MODELS = {
    ModelTier.FREE: "gemini-2.5-flash",
    ModelTier.ULTRA_CHEAP: "deepseek-chat",
    ModelTier.STANDARD: "claude-sonnet-4-5-20250514",
    ModelTier.PREMIUM: "claude-opus-4-5-20250514",
}


class LLMRouter:
    """
    Routes LLM requests to appropriate providers based on:
    - Task complexity
    - Cost optimization targets
    - Rate limits
    """
    
    def __init__(self):
        self.gemini_client = None
        self.anthropic_client = None
        self._init_clients()
        
        # Usage tracking
        self.call_counts = {tier: 0 for tier in ModelTier}
    
    def _init_clients(self):
        """Initialize LLM clients."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            self.gemini_client = genai
            logger.info("Gemini client initialized")
        except Exception as e:
            logger.warning("Gemini client failed to initialize", error=str(e))
        
        try:
            from anthropic import Anthropic
            self.anthropic_client = Anthropic(
                api_key=os.environ.get("ANTHROPIC_API_KEY")
            )
            logger.info("Anthropic client initialized")
        except Exception as e:
            logger.warning("Anthropic client failed to initialize", error=str(e))
    
    async def generate(
        self,
        prompt: str,
        model_tier: str = "free",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.3,
    ) -> str:
        """
        Generate text using the appropriate model tier.
        
        Args:
            prompt: User prompt
            model_tier: "free", "ultra_cheap", "standard", or "premium"
            system_prompt: Optional system instruction
            max_tokens: Maximum response tokens
            temperature: Creativity parameter (0-1)
        
        Returns:
            Generated text
        """
        tier = ModelTier(model_tier)
        self.call_counts[tier] += 1
        
        logger.info("LLM generate", tier=tier.value, prompt_length=len(prompt))
        
        try:
            if tier in [ModelTier.FREE]:
                return await self._call_gemini(prompt, system_prompt, max_tokens, temperature)
            elif tier in [ModelTier.STANDARD, ModelTier.PREMIUM]:
                return await self._call_anthropic(prompt, system_prompt, max_tokens, temperature, tier)
            else:
                # Fallback to Gemini
                return await self._call_gemini(prompt, system_prompt, max_tokens, temperature)
        except Exception as e:
            logger.error("LLM call failed", tier=tier.value, error=str(e))
            # Fallback chain
            if tier != ModelTier.FREE:
                logger.info("Falling back to Gemini")
                return await self._call_gemini(prompt, system_prompt, max_tokens, temperature)
            raise
    
    async def _call_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Call Gemini 2.5 Flash (FREE tier)."""
        if not self.gemini_client:
            raise RuntimeError("Gemini client not initialized")
        
        model = self.gemini_client.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt,
        )
        
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        
        return response.text
    
    async def _call_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        tier: ModelTier,
    ) -> str:
        """Call Anthropic (Claude) models."""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")
        
        model = TIER_MODELS.get(tier, TIER_MODELS[ModelTier.STANDARD])
        
        messages = [{"role": "user", "content": prompt}]
        
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt or "You are a helpful assistant.",
            messages=messages,
        )
        
        return response.content[0].text
    
    async def classify_intent(
        self,
        query: str,
        context: Optional[dict] = None,
        parcel_id: Optional[str] = None,
    ) -> dict:
        """
        Classify user intent and extract entities.
        Uses Gemini Flash for cost-effective classification.
        """
        prompt = f"""
Classify the following user query about zoning/real estate.

QUERY: {query}
CONTEXT: {context or {}}
HAS_PARCEL: {parcel_id is not None}

Return a JSON object with:
- intent: one of [feasibility_check, zoning_lookup, allowed_uses, dimensional_standards, hbu_analysis, cma_request, value_estimate, geographic_search, parcel_comparison, report_request, definition, greeting, clarification]
- entities: dict with extracted values (address, zone_code, use_type, etc.)
- confidence: 0-1 score

Return ONLY valid JSON, no markdown.
"""
        
        try:
            response = await self.generate(
                prompt=prompt,
                model_tier="free",
                system_prompt="You are an intent classification system. Return only valid JSON.",
                max_tokens=500,
                temperature=0.1,
            )
            
            import json
            # Clean response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            
            return json.loads(response)
            
        except Exception as e:
            logger.warning("Intent classification failed", error=str(e))
            return {
                "intent": "zoning_lookup",
                "entities": {},
                "confidence": 0.5,
            }
    
    def get_usage_stats(self) -> dict:
        """Get usage statistics."""
        total = sum(self.call_counts.values())
        if total == 0:
            return {tier.value: 0 for tier in ModelTier}
        
        return {
            tier.value: {
                "calls": count,
                "percentage": count / total * 100,
            }
            for tier, count in self.call_counts.items()
        }
