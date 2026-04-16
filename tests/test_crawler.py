"""爬取模块测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from crawler.reddit_client import RedditClient
from crawler.fetcher import Fetcher


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


def test_fetcher_extract_post_data():
    """测试帖子数据提取"""
    mock_client = Mock()
    fetcher = Fetcher(mock_client)

    submission = MagicMock()
    submission.id = "abc123"
    submission.subreddit.display_name = "SomebodyMakeThis"
    submission.title = "Test Title"
    submission.selftext = "Test Content"
    submission.author.__str__ = Mock(return_value="test_author")
    submission.created_utc = 1711234567.0
    submission.score = 100
    submission.upvote_ratio = 0.95
    submission.num_comments = 10

    result = fetcher._extract_post_data(submission)

    assert result["id"] == "abc123"
    assert result["subreddit"] == "SomebodyMakeThis"
    assert result["title"] == "Test Title"
    assert result["score"] == 100


def test_fetcher_extract_comment_data():
    """测试评论数据提取"""
    mock_client = Mock()
    fetcher = Fetcher(mock_client)

    comment = MagicMock()
    comment.id = "def456"
    comment.author.__str__ = Mock(return_value="commenter")
    comment.body = "Test comment"
    comment.score = 5
    comment.created_utc = 1711235678.0

    result = fetcher._extract_comment_data(comment)

    assert result["id"] == "def456"
    assert result["author"] == "commenter"
    assert result["body"] == "Test comment"
    assert result["score"] == 5


def test_fetcher_max_comments_limit():
    """测试评论数量限制"""
    mock_client = Mock()
    fetcher = Fetcher(mock_client, max_comments=10)

    submission = MagicMock()
    submission.comments.replace_more = Mock()
    # 创建 20 个模拟评论
    from praw.models import Comment
    mock_comments = []
    for _ in range(20):
        c = MagicMock()
        c.__class__ = Comment  # Make isinstance(c, Comment) return True
        c.id = f"comment_{c}"
        c.author.__str__ = Mock(return_value="author")
        c.body = "body"
        c.score = 1
        c.created_utc = 1711234567.0
        mock_comments.append(c)
    submission.comments.list.return_value = mock_comments

    post_data = {"id": "test_post"}
    comments = fetcher.fetch_comments(post_data, submission)

    assert len(comments) == 10


def test_reddit_client_get_submission():
    """测试获取帖子"""
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
        mock_submission = Mock()
        mock_reddit.submission.return_value = mock_submission

        client = RedditClient(config)
        result = client.get_submission("abc123")

        mock_reddit.submission.assert_called_once_with(id="abc123")
        assert result == mock_submission