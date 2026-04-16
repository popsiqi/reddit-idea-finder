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


# Analyzer 测试
from analyzer.analyzer import Analyzer


def test_analyzer_extract_priority():
    """测试优先级提取"""
    mock_client = Mock()
    analyzer = Analyzer(mock_client)

    assert analyzer.extract_priority("优先级评分：⭐⭐⭐⭐⭐") == 5
    assert analyzer.extract_priority("优先级评分：⭐⭐⭐⭐") == 4
    assert analyzer.extract_priority("优先级评分：⭐⭐⭐") == 3
    assert analyzer.extract_priority("优先级评分：⭐⭐") == 2
    assert analyzer.extract_priority("优先级评分：⭐") == 1
    assert analyzer.extract_priority("无星级") == 0


def test_analyzer_analyze_post():
    """测试单个帖子分析"""
    mock_client = Mock()
    mock_client.analyze.return_value = "分析结果文本"
    analyzer = Analyzer(mock_client)

    post_data = {
        "id": "test123",
        "title": "Test Title",
        "content": "Test Content",
        "subreddit": "SomebodyMakeThis",
        "score": 100,
        "num_comments": 10,
        "comments": [
            {"score": 50, "body": "Great idea!"},
            {"score": 30, "body": "I would use this"}
        ]
    }

    result = analyzer.analyze_post(post_data)

    assert result["post_id"] == "test123"
    assert result["post_title"] == "Test Title"
    assert result["analysis"] == "分析结果文本"
    mock_client.analyze.assert_called_once()


def test_analyzer_analyze_posts_top_n():
    """测试批量分析 Top N 功能"""
    mock_client = Mock()
    mock_client.analyze.return_value = "分析结果"
    analyzer = Analyzer(mock_client)

    posts = [
        {"id": "1", "title": "Post 1", "score": 100, "comments": []},
        {"id": "2", "title": "Post 2", "score": 200, "comments": []},
        {"id": "3", "title": "Post 3", "score": 50, "comments": []},
    ]

    results = analyzer.analyze_posts(posts, top_n=2)

    assert len(results) == 2
    # 应该只分析热度最高的 2 个帖子（score 200 和 100）
    assert results[0]["post_id"] == "2"
    assert results[1]["post_id"] == "1"


def test_analyzer_analyze_posts_empty_comments():
    """测试无评论的帖子分析"""
    mock_client = Mock()
    mock_client.analyze.return_value = "分析结果"
    analyzer = Analyzer(mock_client)

    post_data = {
        "id": "test123",
        "title": "Test Title",
        "content": "Test Content",
        "subreddit": "SomebodyMakeThis",
        "score": 100,
        "num_comments": 0,
        "comments": []
    }

    result = analyzer.analyze_post(post_data)

    assert result["post_id"] == "test123"
    mock_client.analyze.assert_called_once()
    # 验证 prompt 中包含 "无评论"
    call_args = mock_client.analyze.call_args[0][0]
    assert "无评论" in call_args


def test_analyzer_analyze_posts_handles_error():
    """测试分析失败时的错误处理"""
    mock_client = Mock()
    mock_client.analyze.side_effect = Exception("API error")
    analyzer = Analyzer(mock_client)

    posts = [
        {"id": "1", "title": "Post 1", "score": 100, "comments": []},
    ]

    results = analyzer.analyze_posts(posts, top_n=1)

    assert len(results) == 1
    assert "分析失败" in results[0]["analysis"]