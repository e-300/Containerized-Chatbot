"""
Implementation Layer Tests

Tests for the AnthropicAgent class.
Focuses on Anthropic API integration, error handling, and agent behavior.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from anthropic.types import TextBlock
from agent.claude import AnthropicAgent
from anthropic import APIError


class TestAnthropicAgentInitialization:
    """Test AnthropicAgent initialization and configuration"""

    def test_agent_initializes_with_api_key(self):
        """Verify agent initializes with API key"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        assert agent.api_key == "test-key"

    def test_agent_uses_default_system_prompt(self):
        """Verify default system prompt is used when none provided"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        assert agent.system_prompt == "You are a helpful developer assistant."

    def test_agent_uses_custom_system_prompt(self):
        """Verify custom system prompt is applied"""
        custom_prompt = "You are a security expert."
        agent = AnthropicAgent(api_key="test-key", system_prompt=custom_prompt)
        assert agent.system_prompt == custom_prompt

    def test_agent_initializes_client(self):
        """Verify Anthropic client is initialized"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        assert agent.client is not None

    def test_agent_has_correct_model(self):
        """Verify correct Claude model is set"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        assert agent.model == "claude-3-5-haiku-latest"


class TestTextExtraction:
    """Test the _extract_text helper method"""

    def test_extract_single_text_block(self):
        """Verify single text block is extracted correctly"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        
        mock_block = Mock(spec=TextBlock)
        mock_block.text = "Hello, world!"
        
        mock_response = Mock()
        mock_response.content = [mock_block]
        
        result = agent._extract_text(mock_response)
        assert result == "Hello, world!"

    def test_extract_multiple_text_blocks(self):
        """Verify multiple text blocks are joined with newlines"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        
        mock_block1 = Mock(spec=TextBlock)
        mock_block1.text = "First line"
        
        mock_block2 = Mock(spec=TextBlock)
        mock_block2.text = "Second line"
        
        mock_response = Mock()
        mock_response.content = [mock_block1, mock_block2]
        
        result = agent._extract_text(mock_response)
        assert result == "First line\nSecond line"

    def test_extract_no_text_blocks(self):
        """Verify graceful handling when no text blocks present"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        
        mock_response = Mock()
        mock_response.content = []
        
        result = agent._extract_text(mock_response)
        assert result == "No text response returned."

    def test_extract_ignores_non_text_blocks(self):
        """Verify non-TextBlock content is ignored"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.text = "Real text"
        
        mock_other_block = Mock()  # Not a TextBlock
        mock_other_block.text = "Should be ignored"
        
        mock_response = Mock()
        mock_response.content = [mock_other_block, mock_text_block]
        
        result = agent._extract_text(mock_response)
        assert result == "Real text"


class TestChatMethod:
    """Test the low-level chat method"""

    @patch('agent.claude.Anthropic')
    def test_chat_successful_response(self, mock_anthropic_class):
        """Verify chat method handles successful API response"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.text = "Test response"
        
        mock_response = Mock()
        mock_response.content = [mock_text_block]
        
        mock_client.messages.create.return_value = mock_response
        
        agent = AnthropicAgent(api_key="test-key", system_prompt="Test prompt")
        result = agent.chat("Hello")
        
        assert result == "Test response"
        mock_client.messages.create.assert_called_once()

    @patch('agent.claude.Anthropic')
    def test_chat_api_error_handling(self, mock_anthropic_class):
        """Verify chat method handles API errors gracefully"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Create a proper mock for APIError
        mock_response = Mock()
        mock_response.status_code = 500
        
        mock_client.messages.create.side_effect = APIError(
            message="API Error",
            request=mock_response,
            body={"error": "test error"}
        )
        
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        result = agent.chat("Hello")
        
        assert "Anthropic API error" in result

    @patch('agent.claude.Anthropic')
    def test_chat_unexpected_error_handling(self, mock_anthropic_class):
        """Verify chat method handles unexpected errors"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        mock_client.messages.create.side_effect = Exception("Unexpected error")
        
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        result = agent.chat("Hello")
        
        assert "Unexpected error" in result

    @patch('agent.claude.Anthropic')
    def test_chat_uses_correct_parameters(self, mock_anthropic_class):
        """Verify chat method calls API with correct parameters"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.text = "Response"
        
        mock_response = Mock()
        mock_response.content = [mock_text_block]
        
        mock_client.messages.create.return_value = mock_response
        
        agent = AnthropicAgent(api_key="test-key", system_prompt="Custom prompt")
        agent.chat("Test input")
        
        # Verify the call was made with correct parameters
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == "claude-3-5-haiku-latest"
        assert call_kwargs['max_tokens'] == 1024
        assert call_kwargs['system'] == "Custom prompt"
        assert call_kwargs['messages'][0]['content'] == "Test input"


class TestProcessMethod:
    """Test the high-level process method"""

    @patch.object(AnthropicAgent, 'chat')
    def test_process_empty_input(self, mock_chat):
        """Verify process handles empty input"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        result = agent.process("")
        
        assert result == "Input is empty."
        mock_chat.assert_not_called()

    @patch.object(AnthropicAgent, 'chat')
    def test_process_whitespace_input(self, mock_chat):
        """Verify process handles whitespace-only input"""
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        result = agent.process("   ")
        
        assert result == "Input is empty."
        mock_chat.assert_not_called()

    @patch.object(AnthropicAgent, 'chat')
    def test_process_valid_input(self, mock_chat):
        """Verify process calls chat with valid input"""
        mock_chat.return_value = "Chat response"
        
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        result = agent.process("Valid input")
        
        assert result == "Chat response"
        mock_chat.assert_called_once_with("Valid input")

    @patch.object(AnthropicAgent, 'chat')
    def test_process_error_handling(self, mock_chat):
        """Verify process handles chat errors gracefully"""
        mock_chat.side_effect = Exception("Chat failed")
        
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        result = agent.process("Test input")
        
        assert "Processing error" in result

    @patch.object(AnthropicAgent, 'chat')
    def test_process_passes_input_to_chat(self, mock_chat):
        """Verify process passes user input directly to chat"""
        mock_chat.return_value = "Response"
        
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        test_input = "What is the capital of France?"
        agent.process(test_input)
        
        mock_chat.assert_called_once_with(test_input)


class TestAgentIntegration:
    """Integration tests for AnthropicAgent"""

    @patch('agent.claude.Anthropic')
    def test_full_pipeline(self, mock_anthropic_class):
        """Test complete flow from process to chat to response"""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        mock_text_block = Mock(spec=TextBlock)
        mock_text_block.text = "Integration test response"
        
        mock_response = Mock()
        mock_response.content = [mock_text_block]
        
        mock_client.messages.create.return_value = mock_response
        
        agent = AnthropicAgent(api_key="test-key", system_prompt="Test")
        result = agent.process("Test query")
        
        assert result == "Integration test response"

    def test_agent_implements_interface(self):
        """Verify AnthropicAgent properly implements AI_Platform"""
        from agent.base import AI_Platform
        
        agent = AnthropicAgent(api_key="test-key", system_prompt=None)
        assert isinstance(agent, AI_Platform)