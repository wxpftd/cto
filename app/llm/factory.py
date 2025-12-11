from typing import Optional
from .base import BaseLLMClient
from .openai_client import OpenAIClient
from .claude_client import ClaudeClient
from app.core.config import settings


def get_llm_client(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMClient:
    provider = provider or settings.LLM_PROVIDER
    model = model or settings.LLM_MODEL
    timeout = settings.LLM_TIMEOUT_SECONDS
    
    if provider == "openai":
        api_key = api_key or settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        return OpenAIClient(api_key=api_key, model=model, timeout=timeout)
    
    elif provider == "claude":
        api_key = api_key or settings.ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        return ClaudeClient(api_key=api_key, model=model, timeout=timeout)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
