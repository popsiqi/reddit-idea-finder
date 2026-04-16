"""分析模块测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from analyzer.claude_client import ClaudeClient


def test_claude_client_init():
    """测试 Claude 客户端初始化"""
    config = {
        "claude": {
            "api_key": "test_api_key",
            "model": "claude-sonnet-4-6"
        }
    }
    with patch("analyzer.claude_client.Anthropic") as mock_anthropic:
        client = ClaudeClient(config)
        mock_anthropic.assert_called_once_with(api_key="test_api_key")
        assert client.model == "claude-sonnet-4-6"


def test_claude_client_analyze():
    """测试分析方法"""
    config = {
        "claude": {
            "api_key": "test_api_key",
            "model": "claude-sonnet-4-6"
        }
    }
    with patch("analyzer.claude_client.Anthropic") as mock_anthropic:
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # 模拟响应
        mock_message = Mock()
        mock_content = Mock()
        mock_content.text = "This is a test response"
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(config)
        result = client.analyze("Test prompt", max_tokens=1000)

        mock_client.messages.create.assert_called_once_with(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": "Test prompt"}]
        )
        assert result == "This is a test response"


def test_claude_client_analyze_default_max_tokens():
    """测试分析方法使用默认 max_tokens"""
    config = {
        "claude": {
            "api_key": "test_api_key",
            "model": "claude-sonnet-4-6"
        }
    }
    with patch("analyzer.claude_client.Anthropic") as mock_anthropic:
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_message = Mock()
        mock_content = Mock()
        mock_content.text = "Response"
        mock_message.content = [mock_content]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(config)
        client.analyze("Test prompt")

        # 验证默认 max_tokens 为 4096
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["max_tokens"] == 4096


def test_claude_client_test_connection_success():
    """测试连接检测成功"""
    config = {
        "claude": {
            "api_key": "test_api_key",
            "model": "claude-sonnet-4-6"
        }
    }
    with patch("analyzer.claude_client.Anthropic") as mock_anthropic:
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        mock_message = Mock()
        mock_message.content = [Mock(text="OK")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(config)
        assert client.test_connection() is True


def test_claude_client_test_connection_failure():
    """测试连接检测失败"""
    config = {
        "claude": {
            "api_key": "test_api_key",
            "model": "claude-sonnet-4-6"
        }
    }
    with patch("analyzer.claude_client.Anthropic") as mock_anthropic:
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        client = ClaudeClient(config)
        assert client.test_connection() is False


def test_claude_client_model_property():
    """测试模型属性"""
    config = {
        "claude": {
            "api_key": "test_api_key",
            "model": "claude-opus-4"
        }
    }
    with patch("analyzer.claude_client.Anthropic"):
        client = ClaudeClient(config)
        assert client.model == "claude-opus-4"