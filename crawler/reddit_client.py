"""Reddit API 客户端"""
import praw
from praw.models import Subreddit
from typing import Any


class RedditClient:
    """Reddit API 客户端封装"""

    def __init__(self, config: dict[str, Any]):
        """初始化 Reddit 客户端

        Args:
            config: 包含 Reddit API 凭证的配置字典
        """
        self.reddit = praw.Reddit(
            client_id=config["reddit"]["client_id"],
            client_secret=config["reddit"]["client_secret"],
            user_agent=config["reddit"]["user_agent"]
        )

    def get_subreddit(self, name: str) -> Subreddit:
        """获取子版块对象

        Args:
            name: 子版块名称（不含 r/）

        Returns:
            Subreddit 对象
        """
        return self.reddit.subreddit(name)

    def test_connection(self) -> bool:
        """测试 API 连接是否正常

        Returns:
            True 如果连接正常，False 如果失败
        """
        try:
            # 尝试获取一个已知的子版块来验证连接
            self.reddit.subreddit("test").id
            return True
        except Exception:
            return False