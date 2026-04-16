"""爬取模块测试"""
import pytest
from unittest.mock import Mock, patch
from crawler.reddit_client import RedditClient


def test_reddit_client_init():
    """测试 Reddit 客户端初始化"""
    config = {
        "reddit": {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "user_agent": "test_agent"
        }
    }
    with patch("crawler.reddit_client.praw.Reddit") as mock_praw:
        client = RedditClient(config)
        mock_praw.assert_called_once_with(
            client_id="test_id",
            client_secret="test_secret",
            user_agent="test_agent"
        )


def test_reddit_client_get_subreddit():
    """测试获取子版块"""
    config = {
        "reddit": {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "user_agent": "test_agent"
        }
    }
    with patch("crawler.reddit_client.praw.Reddit") as mock_praw:
        mock_reddit = Mock()
        mock_praw.return_value = mock_reddit
        mock_subreddit = Mock()
        mock_reddit.subreddit.return_value = mock_subreddit

        client = RedditClient(config)
        result = client.get_subreddit("SomebodyMakeThis")

        mock_reddit.subreddit.assert_called_once_with("SomebodyMakeThis")
        assert result == mock_subreddit


def test_reddit_client_test_connection_success():
    """测试连接检测成功"""
    config = {
        "reddit": {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "user_agent": "test_agent"
        }
    }
    with patch("crawler.reddit_client.praw.Reddit") as mock_praw:
        mock_reddit = Mock()
        mock_praw.return_value = mock_reddit
        mock_subreddit = Mock()
        mock_subreddit.id = "test_id"
        mock_reddit.subreddit.return_value = mock_subreddit

        client = RedditClient(config)
        assert client.test_connection() is True


def test_reddit_client_test_connection_failure():
    """测试连接检测失败"""
    config = {
        "reddit": {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "user_agent": "test_agent"
        }
    }
    with patch("crawler.reddit_client.praw.Reddit") as mock_praw:
        mock_reddit = Mock()
        mock_praw.return_value = mock_reddit
        mock_reddit.subreddit.side_effect = Exception("Connection failed")

        client = RedditClient(config)
        assert client.test_connection() is False