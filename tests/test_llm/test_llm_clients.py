import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.llm.factory import get_llm_client
from app.llm.openai_client import OpenAIClient
from app.llm.claude_client import ClaudeClient
from app.llm.base import LLMResponse


@pytest.mark.asyncio
class TestLLMFactory:
    
    def test_get_openai_client(self):
        """Test getting OpenAI client"""
        with patch('app.llm.factory.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "openai"
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "gpt-4"
            mock_settings.LLM_TIMEOUT_SECONDS = 30
            
            client = get_llm_client()
            
            assert isinstance(client, OpenAIClient)
            assert client.model == "gpt-4"
    
    def test_get_claude_client(self):
        """Test getting Claude client"""
        with patch('app.llm.factory.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "claude"
            mock_settings.ANTHROPIC_API_KEY = "test-key"
            mock_settings.LLM_MODEL = "claude-3-opus-20240229"
            mock_settings.LLM_TIMEOUT_SECONDS = 30
            
            client = get_llm_client()
            
            assert isinstance(client, ClaudeClient)
            assert client.model == "claude-3-opus-20240229"
    
    def test_get_client_missing_api_key(self):
        """Test error when API key is missing"""
        with patch('app.llm.factory.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "openai"
            mock_settings.OPENAI_API_KEY = None
            
            with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
                get_llm_client()
    
    def test_get_client_unsupported_provider(self):
        """Test error for unsupported provider"""
        with patch('app.llm.factory.settings') as mock_settings:
            mock_settings.LLM_PROVIDER = "unsupported"
            
            with pytest.raises(ValueError, match="Unsupported LLM provider"):
                get_llm_client()


@pytest.mark.asyncio
class TestOpenAIClient:
    
    @patch('app.llm.openai_client.AsyncOpenAI')
    async def test_complete_success(self, mock_openai_class):
        """Test successful OpenAI completion"""
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.model = "gpt-4"
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 100
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 50
        
        mock_client.chat.completions.create.return_value = mock_response
        
        client = OpenAIClient(api_key="test-key", model="gpt-4")
        response = await client.complete("Test prompt")
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.model == "gpt-4"
        assert response.tokens_used == 100
        assert response.metadata["prompt_tokens"] == 50
        assert response.metadata["completion_tokens"] == 50
    
    @patch('app.llm.openai_client.AsyncOpenAI')
    async def test_complete_with_params(self, mock_openai_class):
        """Test OpenAI completion with custom parameters"""
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.model = "gpt-4"
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage = None
        
        mock_client.chat.completions.create.return_value = mock_response
        
        client = OpenAIClient(api_key="test-key", model="gpt-4")
        response = await client.complete("Test", temperature=0.5, max_tokens=200)
        
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["temperature"] == 0.5
        assert call_args.kwargs["max_tokens"] == 200
    
    def test_get_provider_name(self):
        """Test getting provider name"""
        client = OpenAIClient(api_key="test-key", model="gpt-4")
        assert client.get_provider_name() == "openai"


@pytest.mark.asyncio
class TestClaudeClient:
    
    @patch('app.llm.claude_client.AsyncAnthropic')
    async def test_complete_success(self, mock_anthropic_class):
        """Test successful Claude completion"""
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        
        mock_content = MagicMock()
        mock_content.text = "Test response"
        
        mock_response = MagicMock()
        mock_response.model = "claude-3-opus-20240229"
        mock_response.content = [mock_content]
        mock_response.stop_reason = "end_turn"
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 50
        
        mock_client.messages.create.return_value = mock_response
        
        client = ClaudeClient(api_key="test-key", model="claude-3-opus-20240229")
        response = await client.complete("Test prompt")
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.model == "claude-3-opus-20240229"
        assert response.tokens_used == 100
        assert response.metadata["input_tokens"] == 50
        assert response.metadata["output_tokens"] == 50
    
    @patch('app.llm.claude_client.AsyncAnthropic')
    async def test_complete_with_params(self, mock_anthropic_class):
        """Test Claude completion with custom parameters"""
        mock_client = AsyncMock()
        mock_anthropic_class.return_value = mock_client
        
        mock_content = MagicMock()
        mock_content.text = "Test"
        
        mock_response = MagicMock()
        mock_response.model = "claude-3-opus-20240229"
        mock_response.content = [mock_content]
        mock_response.stop_reason = "end_turn"
        mock_response.usage = None
        
        mock_client.messages.create.return_value = mock_response
        
        client = ClaudeClient(api_key="test-key")
        response = await client.complete("Test", temperature=0.5, max_tokens=200)
        
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["temperature"] == 0.5
        assert call_args.kwargs["max_tokens"] == 200
    
    def test_get_provider_name(self):
        """Test getting provider name"""
        client = ClaudeClient(api_key="test-key")
        assert client.get_provider_name() == "claude"
