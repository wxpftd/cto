from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseLLMClient(ABC):
    def __init__(self, api_key: str, model: str, timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> LLMResponse:
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        pass
