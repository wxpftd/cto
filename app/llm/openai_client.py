from typing import Dict, Any
from openai import AsyncOpenAI
from .base import BaseLLMClient, LLMResponse
import logging

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4", timeout: int = 30):
        super().__init__(api_key, model, timeout)
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
    
    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that classifies and organizes tasks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else None,
                finish_reason=choice.finish_reason,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "completion_tokens": response.usage.completion_tokens if response.usage else None,
                }
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def get_provider_name(self) -> str:
        return "openai"
