"""帖子和评论爬取逻辑"""
import time
from datetime import datetime, timezone
from typing import Any
from praw.models import Submission, Comment
from crawler.reddit_client import RedditClient


class Fetcher:
    """数据爬取器"""

    # Reddit API 速率限制：60 请求/分钟
    RATE_LIMIT_DELAY = 1.0  # 每次请求后等待 1 秒

    def __init__(self, client: RedditClient, max_comments: int = 100):
        """初始化爬取器

        Args:
            client: Reddit 客户端
            max_comments: 每个帖子最多爬取的评论数
        """
        self.client = client
        self.max_comments = max_comments

    def fetch_top_posts(
        self,
        subreddit_name: str,
        time_filter: str,
        limit: int = 50,
        progress_callback: callable | None = None
    ) -> list[dict[str, Any]]:
        """爬取子版块的热门帖子

        Args:
            subreddit_name: 子版块名称
            time_filter: 时间过滤器 (week/month/year/all)
            limit: 帖子数量限制
            progress_callback: 进度回调函数

        Returns:
            帖子数据列表
        """
        subreddit = self.client.get_subreddit(subreddit_name)
        posts = []

        for i, submission in enumerate(subreddit.top(time_filter=time_filter, limit=limit)):
            post_data = self._extract_post_data(submission)
            posts.append(post_data)

            if progress_callback:
                progress_callback(i + 1, limit, subreddit_name)

            # 速率控制
            time.sleep(self.RATE_LIMIT_DELAY)

        return posts

    def fetch_comments(
        self,
        post_data: dict[str, Any],
        submission: Submission,
        progress_callback: callable | None = None
    ) -> list[dict[str, Any]]:
        """爬取帖子的评论

        Args:
            post_data: 帖子数据
            submission: PRAW Submission 对象
            progress_callback: 进度回调函数

        Returns:
            评论数据列表
        """
        comments = []
        submission.comments.replace_more(limit=0)  # 跳过 "more comments" 链接
        time.sleep(self.RATE_LIMIT_DELAY)  # 速率控制

        for i, comment in enumerate(submission.comments.list()[:self.max_comments]):
            if isinstance(comment, Comment):
                comment_data = self._extract_comment_data(comment)
                comments.append(comment_data)

                if progress_callback and (i + 1) % 10 == 0:
                    progress_callback(i + 1, min(len(submission.comments.list()), self.max_comments), post_data["id"])

        return comments

    def _extract_post_data(self, submission: Submission) -> dict[str, Any]:
        """提取帖子数据"""
        return {
            "id": submission.id,
            "subreddit": submission.subreddit.display_name,
            "title": submission.title,
            "content": submission.selftext or "",
            "author": str(submission.author) if submission.author else "[deleted]",
            "created_utc": submission.created_utc,
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "url": f"https://reddit.com/r/{submission.subreddit.display_name}/comments/{submission.id}"
        }

    def _extract_comment_data(self, comment: Comment) -> dict[str, Any]:
        """提取评论数据"""
        return {
            "id": comment.id,
            "author": str(comment.author) if comment.author else "[deleted]",
            "body": comment.body or "",
            "score": comment.score,
            "created_utc": comment.created_utc
        }

    def crawl_all(
        self,
        subreddits: list[str],
        time_filter: str,
        posts_limit: int = 50,
        progress_callback: callable | None = None
    ) -> dict[str, Any]:
        """爬取所有子版块的帖子和评论

        Args:
            subreddits: 子版块名称列表
            time_filter: 时间过滤器
            posts_limit: 每个子版块的帖子数量限制
            progress_callback: 进度回调函数

        Returns:
            包含元数据和帖子数据的字典
        """
        all_posts = []

        for subreddit_name in subreddits:
            posts = self.fetch_top_posts(
                subreddit_name=subreddit_name,
                time_filter=time_filter,
                limit=posts_limit,
                progress_callback=progress_callback
            )
            all_posts.extend(posts)

        # 爬取评论
        total_comments = 0
        for post_data in all_posts:
            time.sleep(self.RATE_LIMIT_DELAY)  # 速率控制
            submission = self.client.get_submission(post_data["id"])
            comments = self.fetch_comments(post_data, submission, progress_callback)
            post_data["comments"] = comments
            total_comments += len(comments)

        return {
            "crawl_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "subreddits": subreddits,
                "time_range": time_filter,
                "total_posts": len(all_posts),
                "total_comments": total_comments
            },
            "posts": all_posts
        }