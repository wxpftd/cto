from typing import Dict, Any
from anthropic import AsyncAnthropic
from .base import BaseLLMClient, LLMResponse
import logging

logger = logging.getLogger(__name__)


class ClaudeClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", timeout: int = 30):
        super().__init__(api_key, model, timeout)
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)
    
    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = ""
            if response.content:
                content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            
            return LLMResponse(
                content=content,
                model=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                finish_reason=response.stop_reason,
                metadata={
                    "input_tokens": response.usage.input_tokens if response.usage else None,
                    "output_tokens": response.usage.output_tokens if response.usage else None,
                }
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def get_provider_name(self) -> str:
        return "claude"
